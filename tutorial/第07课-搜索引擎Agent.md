首先准备各种key和模型名称

```python
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
# 从环境变量中读取api_key
api_key = os.getenv('WOWRAG_API_KEY')
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
from llama_index.core.tools import FunctionTool
import requests
# 需要先把BOCHA_API_KEY填写到.env文件中去。
BOCHA_API_KEY = os.getenv('BOCHA_API_KEY')

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
        return str(response.json())
    else:
        raise Exception(f"API请求失败，状态码: {response.status_code}, 错误信息: {response.text}")

search_tool = FunctionTool.from_defaults(fn=bocha_web_search_tool)
from llama_index.core.agent import ReActAgent
agent = ReActAgent.from_tools([search_tool], llm=llm, verbose=True)
```

测试一下是否可用
```python
# 测试用例
query = "阿里巴巴2024年的ESG报告主要讲了哪些内容？"
response = agent.chat(f"请帮我搜索以下内容：{query}")
print(response)
```

Thought: The current language of the user is: Chinese. I need to use the information provided by the web search tool to answer the question.
Answer: 阿里巴巴2024年的ESG报告主要涵盖了公司在可持续发展方面的多项进展和成就。报告强调了公司的使命——“让天下没有难做的生意”，并通过技术创新和平台优势，支持中小微企业的发展，推动社会和环境的积极变化。在环境方面，阿里巴巴致力于实现碳中和，减少温室气体排放，并通过推动生态减排和绿色物流等措施，助力建设绿水青山。社会责任方面，阿里巴巴通过各种项目和倡议，如乡村振兴、社会应急响应、科技赋能解决社会问题等，展现了其对社会包容和韧性的贡献。治理方面，阿里巴巴强化了其ESG治理架构，确保了决策过程的透明度和有效性，并在隐私保护、数据安全和科技伦理等方面持续提升能力。总体而言，阿里巴巴集团的ESG报告展示了其在推动商业、社会和环境可持续发展方面的坚定承诺和实际行动。