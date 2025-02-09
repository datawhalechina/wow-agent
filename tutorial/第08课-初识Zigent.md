# 初识 Zigent：构建你的又一个智能搜索代理

Zigent 是一个基于 [Agentlite](https://github.com/SalesforceAIResearch/AgentLite) 框架改进的智能代理开发框架。Agentlite 最初由 Salesforce AI Research 团队开发，是一个强大的 Agent 开发框架。Zigent 在其基础上进行了定制化改进，使其更适合特定场景的应用。

在本课中，我们将学习如何使用 Zigent 框架创建一个简单但功能完整的搜索代理。这个代理能够通过 DuckDuckGo 搜索引擎查找信息并回答问题。

## 环境准备

首先，我们需要准备必要的环境和依赖：

```bash
# 建议 Python > 3.8
pip install duckduckgo_search
```

准备大模型相关的环境，比如```api_key```和```base_url```,此处使用自塾提供的大模型服务: http://101.132.164.17:8000 。

```python
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
# 从环境变量中读取api_key
api_key = os.getenv('ZISHU_API_KEY')
base_url = "http://101.132.164.17:8000/v1"
chat_model = "glm-4-flash"
```

引入 zigent 相关的方法如Action、Agent、大模型配置等以及 duckduckgo_search ：

```python
from typing import List
from zigent.agents import ABCAgent, BaseAgent
from zigent.llm.agent_llms import LLM
from zigent.commons import TaskPackage
from zigent.actions.BaseAction import BaseAction
from zigent.logging.multi_agent_log import AgentLogger
from duckduckgo_search import DDGS
```

## 配置 LLM

我们需要配置大语言模型。这里使用 zigent 封装的 LLM加载和配置 LLM 服务：

```python
llm = LLM(api_key=api_key, base_url=base_url, model_name=chat_model)
response = llm.run("你是谁？")
print(response)
```
我是一个人工智能助手，专门设计来帮助用户解答问题、提供信息以及执行各种任务。我的目标是成为您生活中的助手，帮助您更高效地获取所需信息。有什么我可以帮您的吗？



## 创建搜索动作

首先，我们需要创建一个搜索动作类，它将处理与 DuckDuckGo 的具体交互：
需要注意的是，DuckDuckGo需要科学上网。
```python
class DuckSearchAction(BaseAction):
    def __init__(self) -> None:
        action_name = "DuckDuckGo_Search"
        action_desc = "Using this action to search online content."
        params_doc = {"query": "the search string. be simple."}
        self.ddgs = DDGS()
        super().__init__(
            action_name=action_name, 
            action_desc=action_desc, 
            params_doc=params_doc,
        )

    def __call__(self, query):
        results = self.ddgs.chat(query)
        return results
```

这个类主要做两件事：

1. 初始化时配置动作的名称、描述和参数说明
2. 通过 __call__ 方法执行实际的搜索操作
使用示例：

```python
search_action = DuckSearchAction()
results = search_action("什么是 agent")
print(results)
```

我们将得到类似结果：


“Agent”这个词在不同的领域有不同的含义。以下是一些常见的解释：

1. **一般意义**：在日常用语中，agent指的是一个代理人或代表，负责代表他人进行某种活动或决策 。

2. **计算机科学**：在人工智能和计算机科学中，agent通常指的是一种能够感知其环境并采取行动以 实现特定目标的程序或系统。例如，智能代理可以在网络上自动执行任务。

3. **商业**：在商业领域，agent可以指代中介或代理商，他们代表公司或个人进行交易或谈判。     

4. **生物学**：在生物学中，agent可以指代某种物质或生物体，能够引起特定的生物反应，例如病原 体。

具体的含义通常取决于上下文。如果你有特定的领域或上下文，请告诉我，我可以提供更详细的信息。


## 创建搜索代理

接下来，我们创建一个继承自 BaseAgent 的搜索代理类，它需要一个大语言模型 (llm)、一组动作（默认是 DuckSearchAction）、代理名称和角色描述：

```python
class DuckSearchAgent(BaseAgent):
    def __init__(
        self,
        llm: LLM,
        actions: List[BaseAction] = [DuckSearchAction()],
        manager: ABCAgent = None,
        **kwargs
    ):
        name = "duck_search_agent"
        role = "You can answer questions by using duck duck go search content."
        super().__init__(
            name=name,
            role=role,
            llm=llm,
            actions=actions,
            manager=manager
        )
```

## 执行代理

最后，我们来执行我们创建的代理：

```python
def do_search_agent():
    # 创建代理实例
    search_agent = DuckSearchAgent(llm=llm)

    # 创建任务
    task = "what is the found date of microsoft"
    task_pack = TaskPackage(instruction=task)

    # 执行任务并获取响应
    response = search_agent(task_pack)
    print("response:", response)

if __name__ == "__main__":
    do_search_agent()
```

执行程序之后，理想情况下，我们将获得类似下面的日志结果：

```log
Agent duck_search_agent receives the following TaskPackage:
[
        Task ID: 51c6eb6c-c544-4732-8765-982228f61d31
        Instruction: what is the found date of microsoft
]
====duck_search_agent starts execution on TaskPackage 51c6eb6c-c544-4732-8765-982228f61d31====
Agent duck_search_agent takes 0-step Action:
{
        name: DuckDuckGo_Search
        params: {'query': 'Microsoft founding date'}
}
Observation: Microsoft was founded on April 4, 1975.
Agent duck_search_agent takes 1-step Action:
{
        name: Finish
        params: {'response': 'Microsoft was founded on April 4, 1975.'}
}
Observation: Microsoft was founded on April 4, 1975.
=========duck_search_agent finish execution. TaskPackage[ID:51c6eb6c-c544-4732-8765-982228f61d31] status:
[
        completion: completed
        answer: Microsoft was founded on April 4, 1975.
]
==========
response: Microsoft was founded on April 4, 1975.
```


如果不想通过科学上网，可以利用 ZhipuAI 的 [web_search](https://open.bigmodel.cn/dev/howuse/websearch) 实现。
开始前我们需要安装一下 ZhipuAI SDK:

```bash
pip install --upgrade zhipuai
```
并在 `.env` 中新增 `ZHIPU_API_KEY`并填入您的 ZhipuAI APIKey。
和上文环境准备、配置 LLM，此处新增了 ZhipuAI SDK 的引用以及 ZHIPU_API_KEY 的配置。

```python
import os
import json
import requests
from dotenv import load_dotenv
from typing import List
from zigent.agents import BaseAgent, ABCAgent
from zigent.llm.agent_llms import LLM
from zigent.commons import TaskPackage
from zigent.actions.BaseAction import BaseAction
from zhipuai import ZhipuAI
from datetime import datetime

# 加载环境变量
load_dotenv()
api_key = os.getenv('ZISHU_API_KEY')
base_url = "http://101.132.164.17:8000/v1"
chat_model = "Qwen2.5-72B"
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')

# 配置LLM
llm = LLM(api_key=api_key, base_url=base_url, model_name=chat_model)
```

定义Zhipu Web Search工具，使用智谱AI的GLM-4模型进行联网搜索，返回搜索结果的字符串。建议使用免费的 `glm-4-flash`

```python
# 定义Zhipu Web Search工具
def zhipu_web_search_tool(query: str) -> str:
    """
    使用智谱AI的GLM-4模型进行联网搜索，返回搜索结果的字符串。
    
    参数:
    - query: 搜索关键词

    返回:
    - 搜索结果的字符串形式
    """
    # 初始化客户端
    client = ZhipuAI(api_key=ZHIPU_API_KEY)

    # 获取当前日期
    current_date = datetime.now().strftime("%Y-%m-%d")

    print("current_date:", current_date)
    
    # 设置工具
    tools = [{
        "type": "web_search",
        "web_search": {
            "enable": True
        }
    }]

    # 系统提示模板，包含时间信息
    system_prompt = f"""你是一个具备网络访问能力的智能助手，在适当情况下，优先使用网络信息（参考信息）来回答，
    以确保用户得到最新、准确的帮助。当前日期是 {current_date}。"""
        
    # 构建消息
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]
        
    # 调用API
    response = client.chat.completions.create(
        model="glm-4-flash",
        messages=messages,
        tools=tools
    )
    
    # 返回结果
    return response.choices[0].message.content
```

实现 ZhipuSearchAction:
```python
class ZhipuSearchAction(BaseAction):
    def __init__(self) -> None:
        action_name = "Zhipu_Search"
        action_desc = "Using this action to search online content."
        params_doc = {"query": "the search string. be simple."}
        super().__init__(
            action_name=action_name,
            action_desc=action_desc,
            params_doc=params_doc,
        )

    def __call__(self, query):
        results = zhipu_web_search_tool(query)
        return results
```

实现 ZhipuSearchAgent：
```python
class ZhipuSearchAgent(BaseAgent):
    def __init__(
        self,
        llm: LLM,
        actions: List[BaseAction] = [ZhipuSearchAction()],
        manager: ABCAgent = None,
        **kwargs
    ):
        name = "zhiu_search_agent"
        role = "You can answer questions by using Zhipu search content."
        super().__init__(
            name=name,
            role=role,
            llm=llm,
            actions=actions,
            manager=manager,
        )

```

实现 do_search_agent 并调用，这里以 `2025年洛杉矶大火` 为例：

```python
def do_search_agent():
    # 创建代理实例
    search_agent = ZhipuSearchAgent(llm=llm)

    # 创建任务
    task = "2025年洛杉矶大火"
    task_pack = TaskPackage(instruction=task)

    # 执行任务并获取响应
    response = search_agent(task_pack)
    print(response)

if __name__ == "__main__":
    do_search_agent()
```

预期的返回结果类似：

```
Agent zhiu_search_agent receives the following TaskPackage:
[
        Task ID: c18ec1b9-dfdd-441b-9b62-8354f803a7a4
        Instruction: 2025年洛杉矶大火
]
====zhiu_search_agent starts execution on TaskPackage c18ec1b9-dfdd-441b-9b62-8354f803a7a4====
Agent zhiu_search_agent takes 0-step Action:
{
        name: Zhipu_Search
        params: {'query': '2025年洛杉矶大火'}
}
current_date: 2025-01-16
Observation: 2025年洛杉矶大火是美国历史上最为严重的自然灾害之一。这场大火始于1月7日，起火地点位于洛杉矶东北部的帕萨迪纳地区。火灾迅速蔓延，主要得益于干燥的植被和强劲的圣安娜风，风速达到每小时160公里，相当[TLDR]
Agent zhiu_search_agent takes 1-step Action:
{
        name: Finish
        params: {'response': '2025年洛杉矶大火是美国历史上最严重的自然灾害之一，始于1月7日，主要由于干燥的植被和强劲的圣安娜风导致。这场火灾烧毁了超过12,000公顷的土地，数千栋 建筑被毁，造成至少24人死亡，约18万人被迫撤离。经济损失可能达到1350亿至1500亿美元。'}
}
Observation: Task Completed.
=========zhiu_search_agent finish execution. TaskPackage[ID:c18ec1b9-dfdd-441b-9b62-8354f803a7a4] status:
[
        completion: completed
        answer: 2025年洛杉矶大火是美国历史上最严重的自然灾害之一，始于1月7日，主要由于干燥的植被和强劲的圣安娜风导致。这场火灾烧毁了超过12,000公顷的土地，数千栋建筑被毁，造成 至少24人死亡，约18万人被迫撤离。经济损失可能达到1350亿至1500亿美元。
]
==========
2025年洛杉矶大火是美国历史上最严重的自然灾害之一，始于1月7日，主要由于干燥的植被和强劲的圣安娜风导致。这场火灾烧毁了超过12,000公顷的土地，数千栋建筑被毁，造成至少24人死亡，约18万人被迫撤离。经济损失可能达到1350亿至1500亿美元。
```