首先定义工具函数，用来完成Agent的任务。注意：大模型会根据函数的注释来判断使用哪个函数来完成任务。所以，注释一定要写清楚函数的功能和返回值。

然后把工具函数放入FunctionTool对象中，供Agent能够使用。

用 LlamaIndex 实现一个简单的 agent demo 比较容易，LlamaIndex 实现 Agent 需要导入 ReActAgent 和 Function Tool。

ReActAgent 是什么？

ReActAgent 通过结合推理（Reasoning）和行动（Acting）来创建动态的 LLM Agent 的框架。该方法允许 LLM 模型通过在复杂环境中交替进行推理步骤和行动步骤来更有效地执行任务。ReActAgent 将推理和动作形成了闭环，Agent 可以自己完成给定的任务。

一个典型的 ReActAgent 遵循以下循环：

初始推理：代理首先进行推理步骤，以理解任务、收集相关信息并决定下一步行为。
行动：代理基于其推理采取行动——例如查询API、检索数据或执行命令。
观察：代理观察行动的结果并收集任何新的信息。
优化推理：利用新信息，代理再次进行推理，更新其理解、计划或假设。
重复：代理重复该循环，在推理和行动之间交替，直到达到满意的结论或完成任务。

实现最简单的代码，通过外部工具做算术题，只是一个简单的例子。这个如果不用 Agent，其实大模型也可以回答。看一下具体的代码实现：


首先准备各种key和模型名称

```python
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
# 从环境变量中读取api_key
api_key = os.getenv('ZISHU_API_KEY')
base_url = "http://43.200.7.56:8008/v1"
chat_model = "glm-4-flash"
emb_model = "embedding-3"
```



然后来构建llm，其实任何能用的llm都行。这里自定义一个。
```python
from openai import OpenAI
from pydantic import Field  # 导入Field，用于Pydantic模型中定义字段的元数据
from llama_index.core.llms import (
    CustomLLM,
    CompletionResponse,
    LLMMetadata,
)
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms.callbacks import llm_completion_callback
from typing import List, Any, Generator
# 定义OurLLM类，继承自CustomLLM基类
class OurLLM(CustomLLM):
    api_key: str = Field(default=api_key)
    base_url: str = Field(default=base_url)
    model_name: str = Field(default=chat_model)
    client: OpenAI = Field(default=None, exclude=True)  # 显式声明 client 字段

    def __init__(self, api_key: str, base_url: str, model_name: str = chat_model, **data: Any):
        super().__init__(**data)
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)  # 使用传入的api_key和base_url初始化 client 实例

    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        return LLMMetadata(
            model_name=self.model_name,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        response = self.client.chat.completions.create(model=self.model_name, messages=[{"role": "user", "content": prompt}])
        if hasattr(response, 'choices') and len(response.choices) > 0:
            response_text = response.choices[0].message.content
            return CompletionResponse(text=response_text)
        else:
            raise Exception(f"Unexpected response format: {response}")

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, **kwargs: Any
    ) -> Generator[CompletionResponse, None, None]:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        try:
            for chunk in response:
                chunk_message = chunk.choices[0].delta
                if not chunk_message.content:
                    continue
                content = chunk_message.content
                yield CompletionResponse(text=content, delta=content)

        except Exception as e:
            raise Exception(f"Unexpected response format: {e}")

llm = OurLLM(api_key=api_key, base_url=base_url, model_name=chat_model)
```

测试一下这个llm能用吗？
```python
response = llm.stream_complete("你是谁？")
for chunk in response:
    print(chunk, end="", flush=True)
```
我是一个人工智能助手，名叫 ChatGLM，是基于清华大学 KEG 实验室和智谱 AI 公司于 2024 年共同训练的语言模型开发的。我的任务是针对用户的问题和要求提供适当的答复和支持。


```python
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool


def multiply(a: float, b: float) -> float:
    """Multiply two numbers and returns the product"""
    return a * b


def add(a: float, b: float) -> float:
    """Add two numbers and returns the sum"""
    return a + b


def main():

    multiply_tool = FunctionTool.from_defaults(fn=multiply)
    add_tool = FunctionTool.from_defaults(fn=add)

    # 创建ReActAgent实例
    agent = ReActAgent.from_tools([multiply_tool, add_tool], llm=llm, verbose=True)

    response = agent.chat("20+（2*4）等于多少？使用工具计算每一步")

    print(response)


if __name__ == "__main__":
    main()

```

可以看出，它将提问中的计算步骤分别利用了我们自定义的函数 add 和 multiply ，而不是走大模型。挺有意思的吧，我们可以自定义 agent 中的某些处理流程。除了使用 prompt 外，我们的控制权更大了。

当我们问大模型一个天气的问题，当没有工具时，大模型这么回答，作为大语言模型，他不知道天气情况并给出去哪里可以查到天气情况。
现在为我们的 Agent 添加一个查询天气的方法，返回假数据做测试

```python
def get_weather(city: str) -> int:
    """
    Gets the weather temperature of a specified city.

    Args:
    city (str): The name or abbreviation of the city.

    Returns:
    int: The temperature of the city. Returns 20 for 'NY' (New York),
         30 for 'BJ' (Beijing), and -1 for unknown cities.
    """

    # Convert the input city to uppercase to handle case-insensitive comparisons
    city = city.upper()

    # Check if the city is New York ('NY')
    if city == "NY":
        return 20  # Return 20°C for New York

    # Check if the city is Beijing ('BJ')
    elif city == "BJ":
        return 30  # Return 30°C for Beijing

    # If the city is neither 'NY' nor 'BJ', return -1 to indicate unknown city
    else:
        return -1

weather_tool = FunctionTool.from_defaults(fn=get_weather)

agent = ReActAgent.from_tools([multiply_tool, add_tool, weather_tool], llm=llm, verbose=True)

response = agent.chat("纽约天气怎么样?")

```

可以看到模型的推理能力很强，将纽约转成了 NY。可以在 arize_phoenix 中看到 agent 的具体提示词，工具被装换成了提示词。
ReActAgent 使得业务自动向代码转换成为可能，只要有 API 模型就可以调用，很多业务场景都适用，LlamaIndex 提供了一些开源的工具实现，可以到官网查看。

虽然 Agent 可以实现业务功能， 但是一个 Agent 不能完成所有的功能，这也符合软件解耦的设计原则，不同的 Agent 可以完成不同的任务，各司其职，Agent 之间可以进行交互、通信，类似于微服务。