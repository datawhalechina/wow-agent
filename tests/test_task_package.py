"""Offline regressions for task identity and per-task agent memory."""

import json
import tempfile
import unittest
from pathlib import Path

from zigent.agents import BaseAgent, ManagerAgent
from zigent.commons import TaskPackage
from zigent.logging.multi_agent_log import AgentLogger


def action(name, **params):
    return f"{name}[{json.dumps(params)}]"


class ScriptedLLM:
    """Control only the model boundary; use the real agent execution loop."""

    def __init__(self, *responses):
        self.responses = iter(responses)
        self.prompts = []

    def run(self, prompt):
        self.prompts.append(prompt)
        return next(self.responses)


class TaskPackageTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.logger = AgentLogger(
            log_file_name=str(Path(directory.name) / "agent.log"),
            FLAG_PRINT=False,
        )

    def make_worker(self, *answers):
        llm = ScriptedLLM(*(action("Finish", response=answer) for answer in answers))
        return BaseAgent(
            name="Worker",
            role="Answer each assigned task.",
            llm=llm,
            actions=[],
            logger=self.logger,
        )

    def assert_recorded_answer(self, agent, task, answer):
        chain = agent.short_term_memory.get_action_chain(task)
        self.assertEqual(len(chain), 1)
        self.assertEqual(chain[0][0].name, "Finish")
        self.assertEqual(chain[0][0].params, {"response": answer})
        self.assertEqual(chain[0][1], "Task Completed.")

    def test_new_tasks_receive_distinct_default_ids(self):
        first = TaskPackage(instruction="First task")
        second = TaskPackage(instruction="Second task")
        self.assertNotEqual(first.task_id, second.task_id)

    def test_explicit_task_id_is_preserved(self):
        task = TaskPackage(instruction="Restored task", task_id="saved-task-id")
        self.assertEqual(task.task_id, "saved-task-id")

    def test_sequential_tasks_keep_their_own_action_history(self):
        worker = self.make_worker("First answer", "Second answer")
        first = TaskPackage(instruction="First task")
        second = TaskPackage(instruction="Second task")

        self.assertEqual(worker(first), "First answer")
        self.assertEqual(worker(second), "Second answer")

        self.assert_recorded_answer(worker, first, "First answer")
        self.assert_recorded_answer(worker, second, "Second answer")
        self.assertEqual(len(worker.short_term_memory.memory), 2)
        self.assertEqual(len(worker.llm.prompts), 2)

    def test_repeated_delegation_keeps_each_worker_task_history(self):
        worker = self.make_worker("First finding", "Second finding")
        manager_llm = ScriptedLLM(
            action("Worker", Task="Investigate the first question"),
            action("Worker", Task="Investigate the second question"),
            action("Finish", response="Combined answer"),
        )
        manager = ManagerAgent(
            llm=manager_llm,
            TeamAgents=[worker],
            logger=self.logger,
        )
        parent = TaskPackage(instruction="Investigate both questions")

        self.assertEqual(manager(parent), "Combined answer")

        first, second = worker.task_pool
        self.assert_recorded_answer(worker, first, "First finding")
        self.assert_recorded_answer(worker, second, "Second finding")
        self.assertEqual(len({parent.task_id, first.task_id, second.task_id}), 3)
        self.assertEqual(len(worker.short_term_memory.memory), 2)
        self.assertEqual(len(worker.llm.prompts), 2)
        self.assertEqual(len(manager_llm.prompts), 3)
        manager_history = manager.short_term_memory.get_action_chain(parent)
        self.assertEqual(
            [observation for _, observation in manager_history],
            ["First finding", "Second finding", "Task Completed."],
        )


if __name__ == "__main__":
    unittest.main()
