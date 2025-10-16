这里我们会深入探讨Agent的配置

## 基本配置

instructions：也称为开发人员消息或系统提示。
model：使用哪个LLM，以及可选的model_settings来配置模型调优参数，如温度、top_p等。
tools：Agent可以用来完成任务的工具。

```python
from agents import Agent, ModelSettings, function_tool, Runner, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
import os
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
# 从环境变量中读取api_key
api_key = os.getenv('mistral_key')
base_url = 'https://api.mistral.ai/v1'
chat_model = "mistral/mistral-small-latest"
set_tracing_disabled(disabled=True)
llm = LitellmModel(model=chat_model, api_key=api_key, base_url=base_url)

@function_tool 
def get_weather(city: str) -> str: 
    """查询一个城市的天气
    Args:
        city: 要查询天气的城市
    """
    # 注：上方的字符串是get_weather的函数描述，用于告诉Agent该函数用法，需详细填写
    print(f"天气查询工具被调用了，查询的是{city}")
    return f"The weather in {city} is sunny" 

agent = Agent(
    name="天气助手",
    instructions="始终用汉赋的形式回答用户",
    model=llm,
    tools=[get_weather],
)

async def main():
    result = await Runner.run(agent, "上海最近适合出去玩吗?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

运行以上代码会输出：

碧空如洗，晴风徐来，上海之景，无不熠熠生辉。阳光普照，天气和暖，正是出游良辰，探景宜时。若欲游览，今时正好，莫负晴日美时光。


## 输出类型
默认情况下，Agent生成纯文本（即str）输出。如果希望Agent生成特定类型的输出，可以使用output_type参数。一个常见的选择是使用Pydantic对象，但我们支持任何可以封装在Pydantic TypeAdapter中的类型——数据类、列表、TypedDict等。


```python
from agents import Agent, Runner, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
from pydantic import BaseModel
import os
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
# 从环境变量中读取api_key
api_key = os.getenv('mistral_key')
base_url = 'https://api.mistral.ai/v1'
chat_model = "mistral/mistral-small-latest"
set_tracing_disabled(disabled=True)
llm = LitellmModel(model=chat_model, api_key=api_key, base_url=base_url)

class Candidate(BaseModel):
    name: str
    gender: str
    location: str

agent = Agent(
    name="简历助手",
    instructions="根据要求的格式抽取相应的信息",
    model=llm,
    output_type=Candidate,
)

async def main():
    result = await Runner.run(agent, "我叫李婷，女，现居上海，想要应聘前台岗位。")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

运行以上代码会输出：
name='李婷' gender='女' location='上海'
这输出的其实是一个pydantic对象。


## 上下文
Agent在上下文类型上是通用的。Context是一个依赖注入工具：它是一个你创建并传递给Runner.run（）的对象，它被传递给每个agent, tool, handoff等，它充当代理运行的依赖关系和状态的抓取包。您可以提供任何Python对象作为上下文。

这是通过RunContextWrapper类和其中的context属性表示的。其工作方式是：
- 你可以创建任何你想要的Python对象。一种常见的模式是使用数据类或Pydantic对象。
- 您将该对象传递给各种run方法（例如Runner.run（…，**context=whatever**））。
- 您的所有工具调用、生命周期挂钩等都将传递一个包装器对象RunContextWrapper[T]，其中T表示您可以通过wrapper.context访问的上下文对象类型。

典型的用法如下：
```python
@dataclass
class UserContext:
    uid: str
    is_pro_user: bool

    async def fetch_purchases() -> list[Purchase]:
        return ...

agent = Agent[UserContext](
    ...,
)
```


可以将上下文用于以下内容：
- 跑步的上下文数据（例如用户名/uid或其他用户信息）
- 依赖关系（例如记录器对象、数据提取器等）
- 帮助函数

注意：上下文对象不会发送到LLM。它纯粹是一个本地对象，可以对其进行读取、写入和调用方法。
最重要的是要注意：运行的每个代理、工具、生命周期等都必须使用相同类型的上下文。


```python
import asyncio
from dataclasses import dataclass
from agents.extensions.models.litellm_model import LitellmModel
from agents import Agent, RunContextWrapper, Runner, function_tool, set_tracing_disabled
import os
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
# 从环境变量中读取api_key
api_key = os.getenv('mistral_key')
base_url = 'https://api.mistral.ai/v1'
chat_model = "mistral/mistral-small-latest"
set_tracing_disabled(disabled=True)
llm = LitellmModel(model=chat_model, api_key=api_key, base_url=base_url)



@dataclass
class UserInfo:  
    name: str
    uid: int

@function_tool
async def fetch_user_age(wrapper: RunContextWrapper[UserInfo]) -> str:
    """
    获取当前用户的年龄信息。

    Args:
        wrapper (RunContextWrapper[UserInfo]): 包含用户上下文信息的包装器，
            可通过 wrapper.context 访问 UserInfo 实例。

    Returns:
        str: 格式化的年龄字符串，例如 "User John is 47 years old"。
    """  
    # 可以看到，所有的工具都可以访问到这个wrapper.context
    return f"User {wrapper.context.name} is 47 years old"

async def main():
    user_info = UserInfo(name="John", uid=123)

    agent = Agent[UserInfo](  
        name="Assistant",
        tools=[fetch_user_age],
        model=llm,
    )

    result = await Runner.run(  
        starting_agent=agent,
        input="What is the age of the user?",
        context=user_info,
    )

    print(result.final_output)  
    # The user John is 47 years old.

if __name__ == "__main__":
    asyncio.run(main())
```

运行上面代码会输出：
The user, John, is 47 years old.

发送到LLM的大模型上下文需要在提示词中构建。

当调用大模型时，它唯一能获取的数据来自对话历史记录。这意味着如果您想让大模型感知新数据，必须通过以下方式将其加入对话历史：

添加到Agent的instructions。这也被称为"系统提示词"或"开发者消息"。系统提示词可以是静态字符串，也可以是接收上下文并输出字符串的动态函数。这种策略适用于始终需要的信息（例如用户名或当前日期）
调用Runner.run函数时添加到input。这与instructions策略类似，但允许您在命令链较低层级添加消息
通过函数工具暴露。这适用于_按需获取_上下文——大模型可自主决定何时需要数据，并通过调用工具获取
使用检索或网络搜索。这些特殊工具能从文件/数据库（检索）或互联网（网络搜索）获取相关数据，对于生成基于相关上下文数据的"接地气"响应非常有用





## 动态指令
在大多数情况下，可以在创建Agent时提供指令。但是，也可以通过函数提供动态指令。该函数将接收代理和上下文，并且必须返回提示。常规函数和异步函数都可以接受。

一般的用法是这样的。
```python
def dynamic_instructions(
    context: RunContextWrapper[UserContext], agent: Agent[UserContext]
) -> str:
    return f"The user's name is {context.context.name}. Help them with their questions."


agent = Agent[UserContext](
    name="Triage agent",
    instructions=dynamic_instructions,
)
```
下面通过一个完整的例子来说明：
```python
import asyncio
from dataclasses import dataclass
from agents.extensions.models.litellm_model import LitellmModel
from agents import Agent, RunContextWrapper, Runner, function_tool, set_tracing_disabled
import os
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
# 从环境变量中读取api_key
api_key = os.getenv('mistral_key')
base_url = 'https://api.mistral.ai/v1'
chat_model = "mistral/mistral-small-latest"
set_tracing_disabled(disabled=True)
llm = LitellmModel(model=chat_model, api_key=api_key, base_url=base_url)


@dataclass
class PatInfo:
    ip_type: str
    def advice(self) -> str:
        if self.ip_type=="发明":
            return "重点为用户讲解发明专利申请的实质审查要求"
        elif self.ip_type=="实用新型":
            return "重点为用户讲解实用新型专利申请的形式审查要求"

def dynamic_instructions(
    context: RunContextWrapper[PatInfo], agent: Agent[PatInfo]
) -> str:
    return f"用汉赋的句式{context.context.advice()}."


async def main():
    ip_info = PatInfo(ip_type="实用新型")

    agent = Agent[PatInfo](  
        name="Assistant",
        instructions=dynamic_instructions,
        model=llm,
    )

    result = await Runner.run(  
        starting_agent=agent,
        input="我想申请专利",
        context=ip_info,
    )

    print(result.final_output)  

if __name__ == "__main__":
    asyncio.run(main())
```

输出：
**汉赋式形式讲解实用新型专利申请的审查要求**

夫创新为道，专利为径；独创方案，唯实用新型可据。欲成申请之势，先备形式之需；若未周章，则审查不通矣。

其文件所备，尤需齐全。盖分四目，如列星次：其一者，**请求书**也；包含申请之名，发明人之号，申请人之居，以及相关事务之详；此为递表之首，无疏漏者，可为受
理。
其二者，**说明书**也；盖述技术之状，发明之核，或详其结构之适用，高效之比。文字为主，实示为辅；要求清晰，不容模糊。若有附图一页，更添举技方便之势，无图
之例亦有；但图文合璧最佳。
其三者，**权利要求书**；界定权利，划技术之域；其需定义严密，概念清晰。一字之差，权益之失；合规审定，谓不可轻。
其四者，**摘要**；简述所创之精髓，为公告所用，字数勿多，百字之内；阅览若引，精简为宜。

更有附图，固不可少。若为构造分明，图就钩沉；若为技术运用，图载事实。图符之式，线笔分明；长宽合规，标注分清。图与文配，技理双联。

至审查之事，尚须留意三端：**文字、格式、页码**。文字篇幅，勿失规范之章；格式依表，勿乱规矩之行；页码标明，开卷便览。虽细枝末节，亦为审查之要；姑且倘忽
，恐难通过。

综上要诀，形式审明。若规范之备，或可一步通审。一旦疏漏，或需二度再修；严规且遵，成功方至。

愿君备妥诉求，精筹所创。依法申请，合规则成；权利有彰，创新有护！


## 克隆
通过在Agent上使用clone（）方法，您可以复制Agent，并可以选择更改任何您喜欢的属性。

```python
pirate_agent = Agent(
    name="Pirate",
    instructions="Write like a pirate",
    model="o3-mini",
)

robot_agent = pirate_agent.clone(
    name="Robot",
    instructions="Write like a robot",
)
```


