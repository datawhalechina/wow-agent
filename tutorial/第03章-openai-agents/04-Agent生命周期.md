生命周期事件（挂钩）
有时，您希望观察代理的生命周期。例如，您可能希望记录事件，或在某些事件发生时预取数据。您可以使用hooks属性连接到代理生命周期。将AgentHooks或RunHooks类子类化，并重写您感兴趣的方法。

## 概述
总体来说，生命周期钩子分为两大类：

第一类：Agent钩子，可以挂载到具体的Agent上，只有当这个具体的Agent进行到某个生命周期事件的时候，触发特定操作。

第二类：Run钩子，可以挂载到Runner上，每个Agent进行到某个生命周期事件的时候，均触发特定操作。

对于Agent钩子，事件有 
- on_start，该Agent开始时
- on_end，该Agent结束时
- on_handoff，发生移交时
- on_tool_start，工具使用开始时
- on_tool_end，工具使用结束时


对于Run钩子，事件有 
- on_agent_start， 某个Agent开始时
- on_agent_end， 某个Agent结束时
- on_handoff，发生移交时
- on_tool_start，工具使用开始时
- on_tool_end，工具使用结束时

## 开始结束
我们现在来做一个最简单的，用我们最开始跑过的一个Agent来做on_start和on_end这两个钩子。


```python
from agents import Agent, Runner, AgentHooks, RunContextWrapper, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
import os
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
# 从环境变量中读取api_key
api_key = os.getenv('azure_key')
base_url = os.getenv('azure_endpoint')
chat_model = "azure/gpt-4o"
set_tracing_disabled(disabled=True)
llm = LitellmModel(model=chat_model, api_key=api_key, base_url=base_url)

# 定义钩子，这里只定义了on_start和on_end这两个事件
class MyAgentHooks(AgentHooks):
    def __init__(self):
        self.event_counter = 0

    async def on_start(self, context: RunContextWrapper, agent: Agent) -> None:
        self.event_counter += 1
        print(f"{self.event_counter}: Agent {agent.name} started")

    async def on_end(self, context: RunContextWrapper, agent: Agent, output) -> None:
        self.event_counter += 1
        print(
            f"{self.event_counter}: Agent {agent.name} ended with output {output}"
        )

agent = Agent(name="旅行助手", model=llm, hooks=MyAgentHooks(), instructions="You are a helpful assistant")
async def main():
    result = await Runner.run(agent, "孔子全名叫什么?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

这会输出：

1: Agent 旅行助手 started
2: Agent 旅行助手 ended with output 孔子的全名是**孔丘**，字**仲尼**。他是中国古代著名的思想家、教育家和儒家学派的创始人，约生活于公元前551年（鲁襄公
二十二年）至公元前479年（鲁哀公十六年）。孔子常称自己是“述而不作”的文化传承者，他的思想和言行被后人记录在《论语》中，对中国文化产生了深远影响。在后世 
，他被尊奉为“至圣先师”。
孔子的全名是**孔丘**，字**仲尼**。他是中国古代著名的思想家、教育家和儒家学派的创始人，约生活于公元前551年（鲁襄公二十二年）至公元前479年（鲁哀公十六年
）。孔子常称自己是“述而不作”的文化传承者，他的思想和言行被后人记录在《论语》中，对中国文化产生了深远影响。在后世，他被尊奉为“至圣先师”。


需要注意的是，context: RunContextWrapper这个参数是不能省的，就算用不到也不能删掉。

钩子也可以使用Run钩子，用法差不多，就是挂载的时候，需要挂载到run函数中。另外事件名称有区别。
- on_start，该Agent开始时
- on_end，该Agent结束时

变成了

- on_agent_start， 某个Agent开始时
- on_agent_end， 某个Agent结束时


```python
from agents import Agent, Runner, RunHooks, RunContextWrapper, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
import os
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
# 从环境变量中读取api_key
api_key = os.getenv('azure_key')
base_url = os.getenv('azure_endpoint')
chat_model = "azure/gpt-4o"
set_tracing_disabled(disabled=True)
llm = LitellmModel(model=chat_model, api_key=api_key, base_url=base_url)

# 定义钩子，这里只定义了on_start和on_end这两个事件
class MyRunHooks(RunHooks):
    def __init__(self):
        self.event_counter = 0

    async def on_agent_start(self, context: RunContextWrapper, agent: Agent) -> None:
        self.event_counter += 1
        print(f"{self.event_counter}: Agent {agent.name} started")

    async def on_agent_end(self, context: RunContextWrapper, agent: Agent, output) -> None:
        self.event_counter += 1
        print(
            f"{self.event_counter}: Agent {agent.name} ended with output {output}"
        )

agent = Agent(name="旅行助手", model=llm, instructions="You are a helpful assistant")
async def main():
    result = await Runner.run(agent, hooks=MyRunHooks(), input="孟子全名叫什么?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```
这会输出：
1: Agent 旅行助手 started
2: Agent 旅行助手 ended with output 孟子的全名是**孟轲**（拼音：Mèng Kē）。他是战国时期著名的思想家、教育家，儒家学派的重要代表人物，与孔子并称“孔孟”。孟子的思想集中体现在《孟子》一书中，他提倡“仁政”、强调“民贵君轻”，主张性善论，影响深远。
孟子的全名是**孟轲**（拼音：Mèng Kē）。他是战国时期著名的思想家、教育家，儒家学派的重要代表人物，与孔子并称“孔孟”。孟子的思想集中体现在《孟子》一书中 ，他提倡“仁政”、强调“民贵君轻”，主张性善论，影响深远。

## 工具使用

对于AgentHooks和RunHooks，事件函数名称都是一样的，而且函数的参数也都一样。
- on_tool_start，工具使用开始时
- on_tool_end，工具使用结束时

```python
on_tool_start(
    context: RunContextWrapper[TContext],
    agent: Agent[TContext],
    tool: Tool,
) -> None

on_tool_end(
    context: RunContextWrapper[TContext],
    agent: Agent[TContext],
    tool: Tool,
    result: str,
) -> None
```
可见，on_tool_end函数仅仅比on_tool_start函数多了一个result参数。

我们还是改造一下上节课的一段调用工具的代码，给它加上生命周期。

先用AgentHooks类
```python
from agents import Agent, AgentHooks, RunContextWrapper, function_tool, Runner, Tool, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
import os
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
# 从环境变量中读取api_key
api_key = os.getenv('azure_key')
base_url = os.getenv('azure_endpoint')
chat_model = "azure/gpt-4o"
set_tracing_disabled(disabled=True)
llm = LitellmModel(model=chat_model, api_key=api_key, base_url=base_url)

@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny"

# 定义钩子，这里只定义了on_tool_start和on_tool_end这两个事件
class MyAgentHooks(AgentHooks):
    def __init__(self):
        self.event_counter = 0

    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool) -> None:
        self.event_counter += 1
        print(f"{self.event_counter}: Agent {agent.name} started to use Tool {tool.name}")

    async def on_tool_end(self, context: RunContextWrapper, agent: Agent, tool: Tool, output) -> None:
        self.event_counter += 1
        print(
            f"{self.event_counter}: Agent {agent.name} ended to use Tool {tool.name} with output {output}"
        )

agent = Agent(
    name="天气助手",
    instructions="始终用汉赋的形式回答用户",
    model=llm,
    tools=[get_weather],
    hooks=MyAgentHooks(),
)

async def main():
    result = await Runner.run(agent, "上海最近适合出去玩吗?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```


运行以上代码，会输出：
1: Agent 天气助手 started to use Tool get_weather
2: Agent 天气助手 ended to use Tool get_weather with output The weather in 上海 is sunny
巍巍沪上，嘉名上海。观最近之天气，阳光普照，晴空万里，是时光临于外，或漫步黄浦江畔，或伫立于豫园之庭。清风徐来，暖意融融，正宜游玩之时矣！

再用RunHooks类，由于事件函数名称都是一样的，而且函数的参数也都一样，所以只需要改动继承的类名以及调用的位置即可。

```python
from agents import Agent, RunHooks, RunContextWrapper, function_tool, Runner, Tool, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
import os
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
# 从环境变量中读取api_key
api_key = os.getenv('azure_key')
base_url = os.getenv('azure_endpoint')
chat_model = "azure/gpt-4o"
set_tracing_disabled(disabled=True)
llm = LitellmModel(model=chat_model, api_key=api_key, base_url=base_url)

@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny"

# 定义钩子，这里只定义了on_tool_start和on_tool_end这两个事件
class MyRunHooks(RunHooks):
    def __init__(self):
        self.event_counter = 0

    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool) -> None:
        self.event_counter += 1
        print(f"{self.event_counter}: Agent {agent.name} started to use Tool {tool.name}")

    async def on_tool_end(self, context: RunContextWrapper, agent: Agent, tool: Tool, output) -> None:
        self.event_counter += 1
        print(
            f"{self.event_counter}: Agent {agent.name} ended to use Tool {tool.name} with output {output}"
        )

agent = Agent(
    name="天气助手",
    instructions="始终用汉赋的形式回答用户",
    model=llm,
    tools=[get_weather],
)

async def main():
    result = await Runner.run(agent, hooks=MyRunHooks(), input="上海最近适合出去玩吗?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

运行以上代码会输出：
1: Agent 天气助手 started to use Tool get_weather
2: Agent 天气助手 ended to use Tool get_weather with output The weather in 上海 is sunny
上海之天气清朗，阳光普照，晴空如洗，碧蓝如墨。适逢此佳景，宜出游登览，踏青赏景，闲庭信步，尽享自然之美。天公作美，莫负良辰，可策马奔赴山水间矣！

## 移交

移交虽然只有一个事件函数on_handoff，但是参数的区别还是比较大的。我们还是以上节课的一个例子来增加生命周期。

用AgentHooks类的移交事件
```python
from agents import Agent, AgentHooks, RunContextWrapper, Runner, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
import os
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
# 从环境变量中读取api_key
api_key = os.getenv('azure_key')
base_url = os.getenv('azure_endpoint')
chat_model = "azure/gpt-4o"
set_tracing_disabled(disabled=True)
llm = LitellmModel(model=chat_model, api_key=api_key, base_url=base_url)


# 定义钩子，这里只定义了on_handoff这个事件
class MyAgentHooks(AgentHooks):
    def __init__(self):
        self.event_counter = 0

    async def on_handoff(self, context: RunContextWrapper, agent: Agent, source: Agent) -> None:
        self.event_counter += 1
        print(
            f"{self.event_counter}: Agent {source.name} handed off to {agent.name}"
        )

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
    model=llm,
    hooks=MyAgentHooks(),
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
    model=llm,
    hooks=MyAgentHooks(),
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent],
    model=llm,
    hooks=MyAgentHooks(),
)

async def main():
    result = await Runner.run(triage_agent, "如何证明勾股定理？")
    print(result.final_output)

    result = await Runner.run(triage_agent, "介绍一下孔子生活的年代?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```


1: Agent Triage Agent handed off to Math Tutor
证明勾股定理的方法有许多种，下面我将为你提供一个十分经典的几何证明方法，称为“面积法”。这一方法基于直角三角形和正方形的面积关系。

**勾股定理陈述：** 在直角三角形中，斜边的平方等于两直角边的平方和。若直角三角形的两直角边长度为 \(a\) 和 \(b\)，斜边长度为 \(c\)，则：
\[
c^2 = a^2 + b^2
\]

### 用面积法来证明：

1. **构造两个正方形：**
   首先，画一个边长为 \(a+b\) 的正方形，其面积为 \((a+b)^2\)。在这个大正方形的内部，利用边长为 \(a\)、\(b\) 和 \(c\) 的直角三角形进行分割。

2. **放置四个直角三角形：**
   在正方形的四个角上放置四个相同的直角三角形，它们的边分别为 \(a, b, c\)。四个直角三角形的面积总和为：
   \[
   4 \times \frac{1}{2}ab = 2ab
   \]

3. **观察正方形内部的空区域：**
   将四个直角三角形放好以后，正方形内部余下的空区域其实是一个小正方形，这个小正方形的边长为 \(c\)，因此其面积为：
   \[
   c^2
   \]

4. **正方形总面积表示法：**
   总面积可以通过两种方式来表达：
   - 第一种是大正方形的直接面积： \((a+b)^2\)
   - 第二种是四个直角三角形的总面积加上内部小正方形面积： \(4 \times \frac{1}{2}ab + c^2 = 2ab + c^2\)

5. **等式展开并化简：**
   由两种面积表示法可得：
   \[
   (a+b)^2 = 2ab + c^2
   \]
   展开左侧：
   \[
   a^2 + 2ab + b^2 = 2ab + c^2
   \]
   两边消去 \(2ab\) 后得到：
   \[
   a^2 + b^2 = c^2
   \]
   即得到了勾股定理的结论。

### 直观理解：

这种方法利用几何形状的面积关系，避免了复杂的代数运算，同时直观地揭示了斜边平方等于两直角边平方和的本质。

如果有需要，我还可以讲其他的勾股定理证明方法（比如代数法或拼图法）。
2: Agent Triage Agent handed off to History Tutor
孔子（公元前551年—公元前479年），是中国古代著名的哲学家、思想家、教育家和政治人物。他生活的时代是春秋时期，这是中国历史上一个重要的动荡时代，对后来的
社会发展和文化传承有着深远的影响。

春秋时期从公元前770年至公元前476年，是周朝分裂后诸侯割据的一个历史阶段。这个时期社会动荡频繁，礼崩乐坏，旧的宗法制度逐渐瓦解。各诸侯国之间争夺权力，战
争频繁。同时，新兴的思想和学派开始涌现，试图寻找解决社会问题的方法。

孔子出生于鲁国陬邑（今天的山东曲阜）。他的父亲是一位小官员，但在孔子三岁时便去世了，家境贫寒。然而，孔子从小就对知识和礼仪充满兴趣，并逐渐在鲁国及邻近
地区赢得了声誉。

孔子以提倡“仁”“礼”为核心，其思想反映了对社会和人生的深刻思考。他创立并教授儒家学说，主张通过道德修养、循礼守法和重视教育来维护社会秩序。在他晚年时期，
孔子周游列国，希望能够说服各国君主采纳自己的治国理念，但在当时并未得到广泛的政治支持。

孔子去世后，他的弟子们将其思想整理记录下来，形成了《论语》等经典著作，为后世儒家思想奠定了基础。儒家思想对中国乃至整个东亚地区的文化和政治产生了深远的
影响，一直延续至今。


用RunHooks类的移交事件，注意on_handoff函数的参数发生了比较大的变化。
```python
from agents import Agent, RunHooks, RunContextWrapper, Runner, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
import os
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
# 从环境变量中读取api_key
api_key = os.getenv('azure_key')
base_url = os.getenv('azure_endpoint')
chat_model = "azure/gpt-4o"
set_tracing_disabled(disabled=True)
llm = LitellmModel(model=chat_model, api_key=api_key, base_url=base_url)


# 定义钩子，这里只定义了on_handoff这个事件
class MyRunHooks(RunHooks):
    def __init__(self):
        self.event_counter = 0

    async def on_handoff(
        self, context: RunContextWrapper, from_agent: Agent, to_agent: Agent
    ) -> None:
        self.event_counter += 1
        print(
            f"### {self.event_counter}: Handoff from {from_agent.name} to {to_agent.name}."
        )

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
    model=llm,
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
    model=llm,
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent],
    model=llm,
)

async def main():
    result = await Runner.run(triage_agent, hooks=MyRunHooks(), input="勾股定理在西方叫什么？")
    print(result.final_output)

    result = await Runner.run(triage_agent, hooks=MyRunHooks(), input="孔子和孟子什么关系?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

运行后输出以下内容：
### 1: Handoff from Triage Agent to History Tutor.
在西方，勾股定理被称为“Pythagorean Theorem”（毕达哥拉斯定理）。这个定理得名于古希腊数学家毕达哥拉斯（Pythagoras），他和他的学派在几何学中进行了重要的
研究。但其实在毕达哥拉斯之前，中国、印度等地的早期数学家也对这个定理有了相关的认识。

这个定理的核心内容是：对于任何一个直角三角形，其两个直角边的长度平方之和等于斜边的长度平方，即表达为数学公式：a² + b² = c²。这一原理在古代的建筑和工程
实践中就有了重要的应用。
### 1: Handoff from Triage Agent to History Tutor.
孔子和孟子的关系主要是思想传承上的师承关系，但二者并非直接的师徒，孟子是孔子的后继者之一。

**孔子**（公元前551年－公元前479年）是春秋时期的思想家、教育家，也是儒家学派的创始人。他提出了“仁”、“礼”等核心概念，并重视修身齐家治国平天下的理念。  

**孟子**（约公元前372年－公元前289年），生活在孔子去世后百余年的战国时期，是儒家学派的重要继承和发展者，被后人称为“亚圣”。孟子继承了孔子的思想，但也进
行了深化和补充，特别是他提出了“性善论”，强调人的本性是善良的，并且非常重视富国强民的实际政治主张。

虽然他们没有直接的师徒关系，但孔子的思想影响了孟子以及后来的整个儒家学派。孟子被视为儒家思想的伟大发展者，两人共同奠定了儒学的核心基础。