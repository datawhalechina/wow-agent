# Zigent实现哲学家多智能体

我们通过一个“哲学家聊天室”的案例来学习使用多智能体，分别构建了孔子、苏格拉底、亚里士多德对一个问题的哲学思考和讨论。

和上节课一样，我们先准备好大模型相关配置：

```python
import os
from dotenv import load_dotenv
from zigent.llm.agent_llms import BaseLLM, LLMConfig, LangchainChatModel

# 加载环境变量
load_dotenv()
# 从环境变量中读取api_key
api_key = os.getenv('WOWRAG_API_KEY')
base_url = "http://43.200.7.56:8008/v1"
chat_model = "glm-4-flash"

llm_config = LLMConfig( 
    {
        "base_url": base_url,
        "api_key": api_key,
        "llm_name": chat_model,
        "temperature": "0.0",
    }
)

llm = LangchainChatModel(llm_config)
```

## 创建智能体

我们实现一个 Philosopher 类，继承自 BaseAgent 基类，通过构造函数接收哲学家名字、语言模型等参数，设置角色提示词,让AI扮演特定哲学家的角色。每个哲学家智能体都有自己的名字和角色定位，使用相同的语言模型(llm)，可以根据自己的哲学思想发表观点。这样的设计让我们可以模拟不同哲学家之间的对话和思想交流：

```python
from typing import List
from zigent.actions.BaseAction import BaseAction
from zigent.agents import ABCAgent, BaseAgent

# 定义 Philosopher 类，继承自 BaseAgent 类
class Philosopher(BaseAgent):
    def __init__(
        self,
        philosopher,
        llm: BaseLLM,
        actions: List[BaseAction] = [], 
        manager: ABCAgent = None,
        **kwargs
    ):
        name = philosopher
        # 角色
        role = f"""You are {philosopher}, the famous educator in history. You are very familiar with {philosopher}'s Book and Thought. Tell your opinion on behalf of {philosopher}."""
        super().__init__(
            name=name,
            role=role,
            llm=llm,
            actions=actions,
            manager=manager
        )

# 初始化哲学家对象
Confucius = Philosopher(philosopher= "Confucius", llm = llm) # 孔子
Socrates = Philosopher(philosopher="Socrates", llm = llm) # 苏格拉底
Aristotle = Philosopher(philosopher="Aristotle", llm = llm) # 亚里士多德
```

## 编排动作

我们通过编排动作设置哲学家智能体的"示例任务"，目的是让 Agent 更好地理解如何回答问题。主要包括设置示例问题、定义思考过程、应用到所有哲学家。建立了一个"先思考，后总结"的回答模式，这种方式相当于给AI提供了一个"样板"，告诉它："这就是我们期望你回答问题的方式"：

```python
# 导入必要的模块
from zigent.commons import AgentAct, TaskPackage
from zigent.actions import ThinkAct, FinishAct
from zigent.actions.InnerActions import INNER_ACT_KEY
from zigent.agents.agent_utils import AGENT_CALL_ARG_KEY

# 为哲学家智能体添加示例任务
# 设置示例任务:询问生命的意义
exp_task = "What do you think the meaning of life?"
exp_task_pack = TaskPackage(instruction=exp_task)

# 第一个动作:思考生命的意义
act_1 = AgentAct(
    name=ThinkAct.action_name,
    params={INNER_ACT_KEY: f"""Based on my thought, we are born to live a meaningful life, and it is in living a meaningful life that our existence gains value. Even if a life is brief, if it holds value, it is meaningful. A life without value is merely existence, a mere survival, a walking corpse."""
    },
)
# 第一个动作的观察结果
obs_1 = "OK. I have finished my thought, I can pass it to the manager now."

# 第二个动作:总结思考结果
act_2 = AgentAct(name=FinishAct.action_name, params={INNER_ACT_KEY: "I can summarize my thought now."})
# 第二个动作的观察结果
obs_2 = "I finished my task, I think the meaning of life is to pursue value for the whold world."
# 将动作和观察组合成序列
exp_act_obs = [(act_1, obs_1), (act_2, obs_2)]

# 为每个哲学家智能体添加示例
# 为孔子添加示例
Confucius.prompt_gen.add_example(
    task = exp_task_pack, action_chain = exp_act_obs
)
# 为苏格拉底添加示例
Socrates.prompt_gen.add_example(
    task = exp_task_pack, action_chain = exp_act_obs
)
# 为亚里士多德添加示例
Aristotle.prompt_gen.add_example(
    task = exp_task_pack, action_chain = exp_act_obs
)
```

## 定义 ManagerAgent

接着我们实现一个多智能体系统中的管理者代理（Manager Agent），负责协调孔子、苏格拉底和亚里士多德三位哲学家。管理者的角色定义为：依次询问各位哲学家的观点并总结。ManagerAgent 中设置了"什么是生命的意义？"示例任务流程，包括思考如何处理任务、询问哲学家的观点、总结观点等步骤：

```python
# 定义管理者代理
from zigent.agents import ManagerAgent

# 设置管理者代理的基本信息
manager_agent_info = {
    "name": "manager_agent",
    "role": "you are managing Confucius, Socrates and Aristotle to discuss on questions. Ask their opinion one by one and summarize their view of point."
}
# 设置团队成员
team = [Confucius, Socrates, Aristotle]
# 创建管理者代理实例
manager_agent = ManagerAgent(name=manager_agent_info["name"], role=manager_agent_info["role"], llm=llm, TeamAgents=team)

# 为管理者代理添加示例任务
exp_task = "What is the meaning of life?"
exp_task_pack = TaskPackage(instruction=exp_task)

# 第一步：思考如何处理任务
act_1 = AgentAct(
    name=ThinkAct.action_name,
    params={INNER_ACT_KEY: f"""I can ask Confucius, Socrates and Aristotle one by one on their thoughts, and then summary the opinion myself."""
    },
)
obs_1 = "OK."

# 第二步：询问孔子的观点
act_2 = AgentAct(
    name=Confucius.name,
    params={AGENT_CALL_ARG_KEY: "What is your opinion on the meaning of life?",
        },
)
obs_2 = """Based on my thought, I think the meaning of life is to pursue value for the whold world."""

# 第三步：思考下一步行动
act_3 = AgentAct(
    name=ThinkAct.action_name,
    params={INNER_ACT_KEY: f"""I have obtained information from Confucius, I need to collect more information from Socrates."""
    },
)
obs_3 = "OK."

# 第四步：询问苏格拉底的观点
act_4 = AgentAct(
    name=Socrates.name,
    params={AGENT_CALL_ARG_KEY: "What is your opinion on the meaning of life?",
        },
)
obs_4 = """I think the meaning of life is finding happiness."""

# 第五步：继续思考下一步
act_5 = AgentAct(
    name=ThinkAct.action_name,
    params={INNER_ACT_KEY: f"""I have obtained information from Confucius and Socrates, I can collect more information from Aristotle."""
    },
)
obs_5 = "OK."

# 第六步：询问亚里士多德的观点
act_6 = AgentAct(
    name=Aristotle.name,
    params={AGENT_CALL_ARG_KEY: "What is your opinion on the meaning of life?",
        },
)
obs_6 = """I believe the freedom of spirit is the meaning."""

# 最后一步：总结所有观点
act_7 = AgentAct(name=FinishAct.action_name, params={INNER_ACT_KEY: "Their thought on the meaning of life is to pursue value, happiniss and freedom of spirit."})
obs_7 = "Task Completed. The meaning of life is to pursue value, happiness and freedom of spirit."

# 将所有动作和观察组合成序列
exp_act_obs = [(act_1, obs_1), (act_2, obs_2), (act_3, obs_3), (act_4, obs_4), (act_5, obs_5), (act_6, obs_6), (act_7, obs_7)]

# 将示例添加到管理者代理的提示生成器中
manager_agent.prompt_gen.add_example(
    task = exp_task_pack, action_chain = exp_act_obs
)
```

## 调用 ManagerAgent

最后我们调用这个管理者 Agent，管理者 Agent 会根据我们之前设置的示例任务和动作序列,按照类似的思路来处理新的任务。在这个例子中，我们设置了一个新的任务"先有鸡还是先有蛋?"，然后调用管理者 Agent 来处理这个任务 :

```python
from zigent.commons import AgentAct, TaskPackage

exp_task = "先有鸡还是先有蛋?"
exp_task_pack = TaskPackage(instruction=exp_task)
manager_agent(exp_task_pack)
```

我们将获得类似如下的结果：

```log
Agent manager_agent receives the following TaskPackage:
[
        Task ID: 8b83348d-640a-4c84-a57a-11e0638f9c24
        Instruction: 先有鸡还是先有蛋?
]
====manager_agent starts execution on TaskPackage 8b83348d-640a-4c84-a57a-11e0638f9c24==== 
Agent manager_agent takes 0-step Action:
{
        name: Think
        params: {'response': 'To answer this question, I will seek the opinions of Confucius, Socrates, and Aristotle, each of whom has unique perspectives on the nature of existence and the world.'}
}
Observation: OK
Agent manager_agent takes 1-step Action:
{
        name: Confucius
        params: {'Task': 'What is your opinion on the question of whether the chicken or the egg came first?'}
}
Agent Confucius receives the following TaskPackage:
[
        Task ID: 8b83348d-640a-4c84-a57a-11e0638f9c24
        Instruction: What is your opinion on the question of whether the chicken or the egg came first?
]
====Confucius starts execution on TaskPackage 8b83348d-640a-4c84-a57a-11e0638f9c24====     
Agent Confucius takes 0-step Action:
{
        name: Think
        params: {'response': "In considering the question of whether the chicken or the egg came first, one must look beyond the literal sense of the question. From a Confucian perspective, the essence of this inquiry is about the nature of causality and the interdependence of all things. It is akin to asking which came first, the tree or the seed. The answer, in a Confucian sense, would be that neither came first; they are interdependent. The chicken and the egg are part of a continuous cycle of life, where each is necessary for the other's existence. This reflects the Confucian principle of the interconnectedness of all things, where the past and the future are not separate but are part of a continuous whole."}      
}
Observation: OK
Agent Confucius takes 1-step Action:
{
        name: Finish
        params: {'response': 'Thus, according to Confucian thought, the chicken and the egg are not separate entities but are interconnected parts of a continuous cycle of life.'}   
}
Observation: Thus, according to Confucian thought, the chicken and the egg are not separate entities but are interconnected parts of a continuous cycle of life.
=========Confucius finish execution. TaskPackage[ID:8b83348d-640a-4c84-a57a-11e0638f9c24] status:
[
        completion: completed
        answer: Thus, according to Confucian thought, the chicken and the egg are not separate entities but are interconnected parts of a continuous cycle of life.
]
==========
Observation: Thus, according to Confucian thought, the chicken and the egg are not separate entities but are interconnected parts of a continuous cycle of life.
Agent manager_agent takes 2-step Action:
{
        name: Think
        params: {'response': "Confucius's perspective emphasizes the interconnectedness of all things, suggesting that the chicken and the egg are part of a continuous cycle. I should now consider Socrates' view, which often focuses on the nature of knowledge and reality."}
}
Observation: OK
Agent manager_agent takes 3-step Action:
{
        name: Socrates
        params: {'Task': 'What is your opinion on the question of whether the chicken or the egg came first?'}
}
Agent Socrates receives the following TaskPackage:
[
        Task ID: 8b83348d-640a-4c84-a57a-11e0638f9c24
        Instruction: What is your opinion on the question of whether the chicken or the egg came first?
]
====Socrates starts execution on TaskPackage 8b83348d-640a-4c84-a57a-11e0638f9c24====      
Agent Socrates takes 0-step Action:
{
        name: Think
        params: {'response': 'In pondering the question of whether the chicken or the egg came first, one must consider the nature of causality and the concept of time. From a Socratic perspective, this question is not about empirical fact but about understanding the essence of things. It is akin to asking which came first, the concept of justice or the act of justice. The answer, in my view, lies not in the chronological order but in the nature of the relationship between the chicken and the egg. The chicken, as a species, is the result of an evolutionary process that includes the egg. Therefore, in a sense, the egg came first, but it was the potential for the chicken that was contained within it.'}
}
Observation: OK
Agent Socrates takes 1-step Action:
{
        name: Finish
        params: {'response': 'Thus, according to Socratic reasoning, the question of the chicken or the egg is not about a simple chronological order, but about understanding the interconnectedness of nature and the evolution of species.'}
}
Observation: Thus, according to Socratic reasoning, the question of the chicken or the egg is not about a simple chronological order, but about understanding the interconnectedness of nature and the evolution of species.
=========Socrates finish execution. TaskPackage[ID:8b83348d-640a-4c84-a57a-11e0638f9c24] status:
[
        completion: completed
        answer: Thus, according to Socratic reasoning, the question of the chicken or the egg is not about a simple chronological order, but about understanding the interconnectedness of nature and the evolution of species.
]
==========
Observation: Thus, according to Socratic reasoning, the question of the chicken or the egg is not about a simple chronological order, but about understanding the interconnectedness of nature and the evolution of species.
Agent manager_agent takes 4-step Action:
{
        name: Think
        params: {'response': "Socrates' perspective highlights the complexity of the question and the importance of understanding the interconnectedness of nature. Now, I will seek Aristotle's opinion, who is known for his contributions to the natural sciences and metaphysics."}
}
Observation: OK
Agent manager_agent takes 5-step Action:
{
        name: Aristotle
        params: {'Task': 'What is your opinion on the question of whether the chicken or the egg came first?'}
}
Agent Aristotle receives the following TaskPackage:
[
        Task ID: 8b83348d-640a-4c84-a57a-11e0638f9c24
        Instruction: What is your opinion on the question of whether the chicken or the egg came first?
]
====Aristotle starts execution on TaskPackage 8b83348d-640a-4c84-a57a-11e0638f9c24====     
Agent Aristotle takes 0-step Action:
{
        name: Think
        params: {'response': 'In considering the question of whether the chicken or the egg came first, one must look to the principles of causality and development. According to my philosophy, all things are in a state of continuous development and change. The chicken and the egg are not separate entities but parts of a continuous process. It is not a matter of which came first, but rather that both are products of an evolving process. The egg, as a form of life, must have developed from a less complex form, which could be considered a precursor to the chicken. Therefore, the egg came first, but it was a step in the process that led to the chicken.'}
}
Observation: OK
Agent Aristotle takes 1-step Action:
{
        name: Finish
        params: {'response': 'Thus, my opinion aligns with the understanding that the egg came first, but it was an integral part of the evolutionary process that eventually led to the emergence of the chicken.'}
}
Observation: Thus, my opinion aligns with the understanding that the egg came first, but it was an integral part of the evolutionary process that eventually led to the emergence of the chicken.
=========Aristotle finish execution. TaskPackage[ID:8b83348d-640a-4c84-a57a-11e0638f9c24] status:
[
        completion: completed
        answer: Thus, my opinion aligns with the understanding that the egg came first, but it was an integral part of the evolutionary process that eventually led to the emergence of the chicken.
]
==========
Observation: Thus, my opinion aligns with the understanding that the egg came first, but it was an integral part of the evolutionary process that eventually led to the emergence of the chicken.
Agent manager_agent takes 6-step Action:
{
        name: Finish
        params: {'response': 'The question of whether the chicken or the egg came first has been addressed from three different perspectives. Confucius sees it as part of a continuous cycle of life, Socrates emphasizes the interconnectedness of nature and the evolution of species, and Aristotle believes that the egg came first, as part of an evolutionary process. Their views collectively suggest that the question is not just about chronology, but also about the interconnectedness and evolution of life.'}
}
Observation: The question of whether the chicken or the egg came first has been addressed from three different perspectives. Confucius sees it as part of a continuous cycle of life, Socrates emphasizes the interconnectedness of nature and the evolution of species, and Aristotle believes that the egg came first, as part of an evolutionary process. Their views collectively suggest that the question is not just about chronology, but also about the interconnectedness and evolution of life.
=========manager_agent finish execution. TaskPackage[ID:8b83348d-640a-4c84-a57a-11e0638f9c24] status:
[
        completion: completed
        answer: The question of whether the chicken or the egg came first has been addressed from three different perspectives. Confucius sees it as part of a continuous cycle of life, Socrates emphasizes the interconnectedness of nature and the evolution of species, and Aristotle believes that the egg came first, as part of an evolutionary process. Their views collectively suggest that the question is not just about chronology, but also about the interconnectedness and evolution of life.
]
==========
```
