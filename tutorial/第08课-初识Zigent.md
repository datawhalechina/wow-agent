# 初识 Zigent：构建你的又一个智能搜索代理

Zigent 是一个基于 [Agentlite](https://github.com/SalesforceAIResearch/AgentLite) 框架改进的智能代理开发框架。Agentlite 最初由 Salesforce AI Research 团队开发，是一个强大的 Agent 开发框架。Zigent 在其基础上进行了定制化改进，使其更适合特定场景的应用。

在本课中，我们将学习如何使用 Zigent 框架创建一个简单但功能完整的搜索代理。这个代理能够通过 DuckDuckGo 搜索引擎查找信息并回答问题。

## 环境准备

首先，我们需要准备必要的环境和依赖：

```bash
# 建议 Python > 3.8
pip install duckduckgo_search
```

准备大模型相关的环境，比如```api_key```和```base_url```,此处使用自塾提供的大模型服务: http://43.200.7.56:8008 。

```python
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
# 从环境变量中读取api_key
api_key = os.getenv('ZISHU_API_KEY')
base_url = "http://43.200.7.56:8008/v1"
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
            manager=manager,
            logger=agent_logger,
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


如果不想通过科学上网，可以利用上一课中提到的bocha搜索API。

```python
BOCHA_API_KEY = os.getenv('BOCHA_API_KEY')
import requests
import json
# 定义Bocha Web Search工具
def bocha_web_search_tool(query: str, count: int = 8) -> str:
    """
    使用Bocha Web Search API进行联网搜索，返回搜索结果的字符串。
    
    参数:
    - query: 搜索关键词
    - count: 返回的搜索结果数量

    返回:
    - 搜索结果的字符串形式
    """
    url = 'https://api.bochaai.com/v1/web-search'
    headers = {
        'Authorization': f'Bearer {BOCHA_API_KEY}',  # 请替换为你的API密钥
        'Content-Type': 'application/json'
    }
    data = {
        "query": query,
        "freshness": "noLimit", # 搜索的时间范围，例如 "oneDay", "oneWeek", "oneMonth", "oneYear", "noLimit"
        "summary": True, # 是否返回长文本摘要总结
        "count": count
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        # 返回给大模型的格式化的搜索结果文本
        # 可以自己对博查的搜索结果进行自定义处理
        return json.dumps(response.json())
    else:
        raise Exception(f"API请求失败，状态码: {response.status_code}, 错误信息: {response.text}")
```

```python
class BochaSearchAction(BaseAction):
    def __init__(self) -> None:
        action_name = "Bocha_Search"
        action_desc = "Using this action to search online content."
        params_doc = {"query": "the search string. be simple."}
        super().__init__(
            action_name=action_name, 
            action_desc=action_desc, 
            params_doc=params_doc,
        )

    def __call__(self, query):
        results = bocha_web_search_tool(query)
        rst = json.loads(results)
        result = ""
        for item in rst["data"]["webPages"]["value"]:
            result += item["summary"]
        return result
```


```python
search_action = BochaSearchAction()
results = search_action("上海有哪些私立小学在招聘小学英语老师？")
print(results)
```
初中英语教师
 06-24 
15-21K/月
上海-普陀区 1年以上 全职
高老师021–56080869
初中物理教师
 06-24 
15-21K/月
上海-普陀区 1年以上 全职
高老师021–5608086...上海市七宝外国语小学现因学校发展需要，特招聘优秀的 语文、数学、英语老师 。
应聘条件
1.本科及以上学历，具有教师资格证者；
2.相关专业毕业，有教学经验者优先；
3.性格开朗、耐心细致、责任心强。
联系方式
潘老师：64195394-3207
邮箱地址： qbwgyxx@126.com （有意向的老师请将简历发至邮箱）
学校地址：闵行区新镇路79号
学校简介
上海市七宝外国语小学创办于2005年，属于民办非企业单位，是一所具有鲜明外语特色的优质民办学校，现为闵行区实验小学教育集团成员校。
学校现有30个教学班，一千三百余位学生，百余位教职工。学校以“助力每个孩子卓越成长”为核心理念，以养成教育、英语特色、思维培养、个性激发为着力点，通过精细化的管理为培养具有“家国情怀、世界眼光、知文达礼、卓立胜己”的卓越学生而竭智尽力，赢得了家长与社会的广泛赞誉。
多元的学习空间
丰富的校园活动
图文：上海市七宝外国语小学
转录编辑：吴王天呈（实习）
(点击图片查看)
上观号作者：今日闵行


```python
search_action = BochaSearchAction()
class BochaSearchAgent(BaseAgent):
    def __init__(
        self,
        llm: LLM,
        actions: List[BaseAction] = [search_action],
        manager: ABCAgent = None,
        **kwargs
    ):
        name = "bocha_search_agent"
        role = "You can answer questions by using bocha search content."
        super().__init__(
            name=name,
            role=role,
            llm=llm,
            actions=actions,
            manager=manager,
        )
```

```python
def do_search_agent():
    # 创建代理实例
    search_agent = BochaSearchAgent(llm=llm)

    # 创建任务
    task = "what is the found date of microsoft"
    task_pack = TaskPackage(instruction=task)

    # 执行任务并获取响应
    response = search_agent(task_pack)
    print("response:", response)
```

```python
do_search_agent()
```
可以执行，但是貌似有些问题，后续还需要调试一下源代码。
Agent bocha_search_agent receives the following TaskPackage:
[
	Task ID: 54eea4c0-3af8-4cce-9cdd-20e1e3f2ba36
	Instruction: what is the found date of microsoft
]
====bocha_search_agent starts execution on TaskPackage 54eea4c0-3af8-4cce-9cdd-20e1e3f2ba36====
Agent bocha_search_agent takes 0-step Action:
{
	name: Bocha_Search[{"query": "found date of Microsoft"}}
	params: {}
}
Observation: "This is the wrong action to call. Please check your available action list.
Agent bocha_search_agent takes 1-step Action:
{
	name: Action:Bocha_Search[{"query": "when was Microsoft founded"}]
	params: {}
}
Observation: "This is the wrong action to call. Please check your available action list.
Agent bocha_search_agent takes 2-step Action:
{
	name: Action:Bocha_Search[{"query": "when was Microsoft founded"}]
	params: {}
}
Observation: "This is the wrong action to call. Please check your available action list.