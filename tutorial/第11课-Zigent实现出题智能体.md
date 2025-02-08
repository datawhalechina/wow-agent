# Zigent实现出题智能体

本节课我们将通过Zigent框架实现一个出题智能体，其主要功能是根据指定的Markdown文件内容自动生成考卷。该智能体支持单选题、多选题和填空题三种题型，并能将生成的考卷保存为Markdown文件。

## 设计思路

出题智能体的核心功能包括：

1. 从指定目录加载Markdown文件作为知识来源
2. 根据用户指定的受众群体和考察目的生成考卷
3. 支持多种题型（单选题、多选题、填空题）
4. 自动保存生成的考卷并返回结果路径

## 代码实现

### 1. 引入依赖

首先引入必要的依赖：

```python
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import json

from zigent.llm.agent_llms import LLM
from zigent.actions import BaseAction, ThinkAct, FinishAct
from zigent.agents import BaseAgent
from zigent.commons import TaskPackage, AgentAct
from zigent.actions.InnerActions import INNER_ACT_KEY
```

### 2. 定义出题Action

定义`QuizGenerationAction`类，负责生成考卷题目：

```python
class QuizGenerationAction(BaseAction):
    """Generate quiz questions from markdown content"""
    def __init__(self, llm: LLM) -> None:
        action_name = "GenerateQuiz"
        action_desc = "Generate quiz questions from markdown content"
        params_doc = {
            "content": "(Type: string): The markdown content to generate questions from",
            "question_types": "(Type: list): List of question types to generate",
            "audience": "(Type: string): Target audience for the quiz",
            "purpose": "(Type: string): Purpose of the quiz"
        }
        super().__init__(action_name, action_desc, params_doc)
        self.llm = llm
        
    def __call__(self, **kwargs):
        content = kwargs.get("content", "")
        question_types = kwargs.get("question_types", [])
        audience = kwargs.get("audience", "")
        purpose = kwargs.get("purpose", "")
        
        prompt = f"""
        你是一个辅助设计考卷的机器人,全程使用中文。
        你的任务是帮助用户快速创建、设计考卷，考卷以markdown格式给出。
        
        要求：
        1. 受众群体：{audience}
        2. 考察目的：{purpose}
        3. 需要包含以下题型：{", ".join(question_types)}
        4. 考卷格式要求：
        """
        prompt += """
        # 问卷标题
        ---
        1. 这是判断题的题干?
            - (x) True
            - ( ) False
        # (x)为正确答案

        2. 这是单选题的题干
            - (x) 这是正确选项
            - ( ) 这是错误选项
        # (x)为正确答案

        3. 这是多选题的题干?
            - [x] 这是正确选项1
            - [x] 这是正确选项2
            - [ ] 这是错误选项1
            - [ ] 这是错误选项2
        # [x]为正确答案

        4. 这是填空题的题干?
            - R:= 填空题答案
        #填空题正确答案格式
        """
        
        prompt += f"\n请根据以下内容生成考卷：\n{content}"
        
        quiz_content = self.llm.run(prompt)
        return {
            "quiz_content": quiz_content,
            "audience": audience,
            "purpose": purpose,
            "question_types": question_types
        }
```

### 3. 定义保存Action

定义`SaveQuizAction`类，负责保存生成的考卷：

```python
class SaveQuizAction(BaseAction):
    """Save quiz to file and return URL"""
    def __init__(self) -> None:
        action_name = "SaveQuiz"
        action_desc = "Save quiz content to file and return URL"
        params_doc = {
            "quiz_content": "(Type: string): The quiz content to save",
            "quiz_title": "(Type: string): Title of the quiz"
        }
        super().__init__(action_name, action_desc, params_doc)
        
    def __call__(self, **kwargs):
        quiz_content = kwargs.get("quiz_content", "")
        quiz_title = kwargs.get("quiz_title", "quiz")
        
        output_dir = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"{quiz_title}.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(quiz_content)
            
        return {
            "file_path": output_file,
            "quiz_url": f"/{output_file}"
        }
```

### 4. 定义出题智能体

定义`QuizGeneratorAgent`类，管理整个出题流程：

```python
class QuizGeneratorAgent(BaseAgent):
    """Quiz generation agent that manages quiz creation process"""
    def __init__(
        self,
        llm: LLM,
        markdown_dir: str
    ):
        name = "QuizGeneratorAgent"
        role = """你是一个专业的考卷生成助手。你可以根据提供的Markdown内容生成结构良好、
        内容全面的考卷。你擅长根据受众群体和考察目的设计合适的题目。"""
        
        super().__init__(
            name=name,
            role=role,
            llm=llm,
        )
        
        self.markdown_dir = markdown_dir
        self.quiz_action = QuizGenerationAction(llm)
        self.save_action = SaveQuizAction()
        
        self._add_quiz_example()
        
    def _load_markdown_content(self) -> str:
        """Load all markdown files from directory"""
        content = []
        for root, _, files in os.walk(self.markdown_dir):
            for file in files:
                if file.endswith(".md"):
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        content.append(f.read())
        return "\n".join(content)
        
    def __call__(self, task: TaskPackage):
        """Process the quiz generation task"""
        # Parse task parameters
        params = json.loads(task.instruction)
        audience = params.get("audience", "")
        purpose = params.get("purpose", "")
        question_types = params.get("question_types", [])
        
        # Load markdown content
        content = self._load_markdown_content()
        
        # Generate quiz
        quiz_result = self.quiz_action(
            content=content,
            question_types=question_types,
            audience=audience,
            purpose=purpose
        )
        
        # Save quiz
        save_result = self.save_action(
            quiz_content=quiz_result["quiz_content"],
            quiz_title="generated_quiz"
        )
        
        task.answer = {
            "quiz_content": quiz_result["quiz_content"],
            "quiz_url": save_result["quiz_url"]
        }
        task.completion = "completed"
        
        return task


    def _add_quiz_example(self):
        """Add an illustration example for the quiz generator"""
        exp_task = json.dumps({
            "audience": "零基础",  # 受众
            "purpose": "测试Python基础知识掌握情况", # 目的
            "question_types": ["单选题", "多选题", "填空题"] # 题型
        })
        exp_task_pack = TaskPackage(instruction=exp_task)
        
        act_1 = AgentAct(
            name=ThinkAct.action_name,
            params={INNER_ACT_KEY: """首先，我会加载Markdown内容，然后根据受众群体和考察目的生成考卷。"""}
        )
        obs_1 = "OK. 开始加载Markdown内容。"
        
        act_2 = AgentAct(
            name=self.quiz_action.action_name,
            params={
                "content": "Python基础内容...",
                "question_types": ["单选题", "多选题", "填空题"],
                "audience": "零基础",
                "purpose": "测试Python基础知识掌握情况"
            }
        )
        obs_2 = """# Python基础测试
        1. Python是什么类型的语言?
            - (x) 解释型
            - ( ) 编译型
        # (x)为正确答案"""
        
        act_3 = AgentAct(
            name=self.save_action.action_name,
            params={
                "quiz_content": obs_2,
                "quiz_title": "Python基础测试"
            }
        )
        obs_3 = {"file_path": "2025-01-15_03-37-40/Python基础测试.md", "quiz_url": "/2025-01-15_03-37-40/Python基础测试.md"}
        
        act_4 = AgentAct(
            name=FinishAct.action_name,
            params={INNER_ACT_KEY: "考卷生成并保存成功。"}
        )
        obs_4 = "考卷生成任务完成。"
        
        exp_act_obs = [(act_1, obs_1), (act_2, obs_2), (act_3, obs_3), (act_4, obs_4)]
        
        self.prompt_gen.add_example(
            task=exp_task_pack,
            action_chain=exp_act_obs
        )

```

## 使用示例

可以通过以下方式使用出题智能体，记得修改指定包含Markdown文件的目录并定义考卷参数 ：

```python
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('ZISHU_API_KEY')
base_url = "http://43.200.7.56:8008/v1"
chat_model = "deepseek-chat"

llm = LLM(api_key=api_key, base_url=base_url, model_name=chat_model)

# 创建出题智能体
markdown_dir = "docs"  # 指定包含Markdown文件的目录
agent = QuizGeneratorAgent(llm=llm, markdown_dir=markdown_dir)

# 定义考卷参数
quiz_params = {
    "audience": "零基础", # 受众群体
    "purpose": "测试基础知识掌握情况", # 考察目的
    "question_types": ["单选题"] # 需要包含的题型
}

# 生成考卷
task = TaskPackage(instruction=json.dumps(quiz_params))
result = agent(task)

print("生成的考卷内容：")
print(result.answer["quiz_content"])
print(f"考卷路径: {result.answer['quiz_url']}")
```

理想情况下，输出类似：

```
生成的考卷内容：
# AI Agent基础知识测试卷
---

1. wow-agent是自塾（zishu.co）出品的第几个开源项目？
    - ( ) 第一个
    - (x) 第三个
    - ( ) 第五个
    - ( ) 第七个
# (x)为正确答案

2. 以下哪个不是自塾在2024年出品的开源项目？
    - ( ) wow-fullstack
    - ( ) wow-rag
    - (x) wow-llm
    - ( ) wow-agent
# (x)为正确答案

3. 以下哪些是Agents的核心组件？（多选）
    - [x] 模型 (Model)
    - [x] 工具 (Tools)
    - [x] 编排层 (Orchestration Layer)
    - [ ] 数据库 (Database)
# [x]为正确答案

4. Agents的运作机制中，以下哪个步骤是正确的？
    - ( ) 接收输入 -> 执行行动 -> 理解输入 -> 推理规划
    - (x) 接收输入 -> 理解输入 -> 推理规划 -> 执行行动
    - ( ) 理解输入 -> 接收输入 -> 推理规划 -> 执行行动
    - ( ) 推理规划 -> 接收输入 -> 理解输入 -> 执行行动
# (x)为正确答案

5. 以下哪个不是Agents的优势？
    - ( ) 知识扩展
    - ( ) 自主行动
    - ( ) 多轮交互
    - (x) 依赖大量人工干预
# (x)为正确答案

6. 以下哪个是Agents的应用场景？
    - ( ) 智能客服
    - ( ) 个性化推荐
    - ( ) 虚拟助手
    - (x) 以上都是
# (x)为正确答案

7. 以下哪个是Agents的开发工具？
    - ( ) LangChain
    - ( ) LangGraph
    - ( ) Vertex AI
    - (x) 以上都是
# (x)为正确答案

8. 以下哪个是结构化Prompt的标识符？
    - ( ) #
    - ( ) <>
    - ( ) -
    - (x) 以上都是
# (x)为正确答案

9. 以下哪个是结构化Prompt的属性词？
    - ( ) Role
    - ( ) Profile
    - ( ) Initialization
    - (x) 以上都是
# (x)为正确答案

10. 以下哪个是LangGPT的Role模板中的内容？
    - ( ) Role
    - ( ) Profile
    - ( ) Rules
    - (x) 以上都是
# (x)为正确答案

11. 以下哪个是prompt设计方法论的步骤？
    - ( ) 数据准备
    - ( ) 模型选择
    - ( ) 提示词设计
    - (x) 以上都是
# (x)为正确答案

12. 以下哪个是智能客服智能体的业务线？
    - ( ) 用户注册
    - ( ) 用户数据查询
    - ( ) 删除用户数据
    - (x) 以上都是
# (x)为正确答案

13. 以下哪个是智能客服智能体的注册任务中需要获取的用户信息？
    - ( ) 用户名、性别、年龄
    - ( ) 用户设置的密码
    - ( ) 用户的电子邮件地址
    - (x) 以上都是
# (x)为正确答案

14. 以下哪个是智能客服智能体的查询任务中需要获取的用户信息？
    - ( ) 用户ID
    - ( ) 用户设置的密码
    - (x) 以上都是
    - ( ) 用户的电子邮件地址
# (x)为正确答案

15. 以下哪个是智能客服智能体的删除任务中需要获取的用户信息？
    - ( ) 用户ID
    - ( ) 用户设置的密码
    - ( ) 用户的电子邮件地址
    - (x) 以上都是
# (x)为正确答案

16. 以下哪个是阅卷智能体的输出格式？
    - ( ) JSON
    - ( ) XML
    - ( ) YAML
    - (x) 以上都是
# (x)为正确答案

17. 以下哪个是阅卷智能体的评分标准？
    - ( ) 宽松
    - ( ) 严格
    - (x) 适当宽松
    - ( ) 以上都是
# (x)为正确答案

18. 以下哪个是阅卷智能体的评分范围？
    - ( ) 0-5分
    - (x) 0-10分
    - ( ) 0-100分
    - ( ) 以上都是
# (x)为正确答案

19. 以下哪个是阅卷智能体的评分结果？
    - ( ) llmgetscore
    - ( ) llmcomments
    - (x) 以上都是
    - ( ) 以上都不是
# (x)为正确答案

20. 以下哪个是阅卷智能体的评分结果中的评语？
    - ( ) llmgetscore
    - (x) llmcomments
    - ( ) 以上都是
    - ( ) 以上都不是
# (x)为正确答案
考卷URL: /2025-01-15_12-46-31\generated_quiz.md
```

## 总结

总的来说，我们通过Zigent框架实现的简单的出题智能体，实现了我们一开始的设计：

1. 根据指定目录的Markdown内容自动生成考卷
2. 支持多种题型
3. 自动保存生成的考卷
4. 提供简单的命令行交互界面

未来我们可以进一步扩展功能，如支持更多题型、自动阅卷评分等功能。
