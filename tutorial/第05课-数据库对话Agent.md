首先我们创建一个数据库：

```python
import sqlite3
# 创建数据库
sqllite_path = 'llmdb.db'
con = sqlite3.connect(sqllite_path)

# 创建表
sql = """
CREATE TABLE `section_stats` (
  `部门` varchar(100) DEFAULT NULL,
  `人数` int(11) DEFAULT NULL
);
"""
c = con.cursor()
cursor = c.execute(sql)
c.close()
con.close()
```

然后给数据库填充一些数据：
```python
con = sqlite3.connect(sqllite_path)
c = con.cursor()
data = [
    ["专利部",22],
    ["商标部",25],
]
for item in data:
    sql = """
    INSERT INTO section_stats (部门,人数) 
    values('%s','%d')
    """%(item[0],item[1])
    c.execute(sql)
    con.commit()
c.close()
con.close()
```

先配置对话模型和嵌入模型。模型的构建可以参考wow-rag课程的第二课（https://github.com/datawhalechina/wow-rag/tree/main/tutorials），里面介绍了非常多配置对话模型和嵌入模型的方式。可以直接用上一课用OurLLM创建的llm，这里采用了本地Ollama的对话模型和嵌入模型。各种配置方式都可以，只要能有个能用的llm和embedding就行。


```python
# 配置对话模型
from llama_index.llms.ollama import Ollama
llm = Ollama(base_url="http://192.168.0.123:11434", model="qwen2:7b")
```

```python
# 配置Embedding模型
from llama_index.embeddings.ollama import OllamaEmbedding
embedding = OllamaEmbedding(base_url="http://192.168.0.123:11434", model_name="qwen2:7b")
```


```python
# 测试对话模型
response = llm.complete("你是谁？")
print(response)
```
我是一个人工智能助手，专门设计来帮助用户解答问题、提供信息以及执行各种任务。我的目标是成为您生活中的助手，帮助您更高效地获取所需信息。有什么我可以帮您的吗？

```python
# 测试嵌入模型
emb = embedding.get_text_embedding("你好呀呀")
len(emb), type(emb)
```
输出 (1024, list)

说明配置成功。



导入Llama-index相关的库，并配置对话模型和嵌入模型。
```python
from llama_index.core.agent import ReActAgent  
from llama_index.core.tools import FunctionTool  
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings  
from llama_index.core.tools import QueryEngineTool   
from llama_index.core import SQLDatabase  
from llama_index.core.query_engine import NLSQLTableQueryEngine  
from sqlalchemy import create_engine, select  


# 配置默认大模型  
Settings.llm = llm
Settings.embed_model = embedding
```
这里的llm和embedding只要是llama-index支持的就行，有多种构建方法。详细可参见wow-rag课程的第二课。

```python
## 创建数据库查询引擎  
engine = create_engine("sqlite:///llmdb.db")  
# prepare data  
sql_database = SQLDatabase(engine, include_tables=["section_stats"])  
query_engine = NLSQLTableQueryEngine(  
    sql_database=sql_database,   
    tables=["section_stats"],   
    llm=Settings.llm  
)
```

```python
# 创建工具函数  
def multiply(a: float, b: float) -> float:  
    """将两个数字相乘并返回乘积。"""  
    return a * b  

multiply_tool = FunctionTool.from_defaults(fn=multiply)  

def add(a: float, b: float) -> float:  
    """将两个数字相加并返回它们的和。"""  
    return a + b

add_tool = FunctionTool.from_defaults(fn=add)

# 把数据库查询引擎封装到工具函数对象中  
staff_tool = QueryEngineTool.from_defaults(
    query_engine,
    name="section_staff",
    description="查询部门的人数。"  
)

```

```python
# 构建ReActAgent，可以加很多函数，在这里只加了加法函数和部门人数查询函数。
agent = ReActAgent.from_tools([add_tool, staff_tool], verbose=True)  
# 通过agent给出指令
response = agent.chat("请从数据库表中获取`专利部`和`商标部`的人数，并将这两个部门的人数相加！")  
```

Thought: 首先我需要使用section_staff工具来获取“专利部”和“商标部”的人数。
Action: section_staff
Action Input: {'input': '专利部'}
Observation: 根据查询结果，部门为“专利部”的统计数据共有22条。
Thought: 我还需要获取“商标部”的人数，我将再次使用section_staff工具。
Action: section_staff
Action Input: {'input': '商标部'}
Observation: 根据查询结果，部门为"商标部"的统计数据共有25条。
Thought: 我现在有了两个部门的人数：“专利部”有22人，“商标部”有25人。下一步我需要将这两个数字相加。
Action: add
Action Input: {'a': 22, 'b': 25}
Observation: 47
Thought: 我可以回答这个问题了，两个部门的人数之和是47人。
Answer: 专利部和商标部的总人数为47人。

```python
print(response)
```
专利部和商标部的总人数为47人。


注：目前这个功能不太稳定，上面这个结果看起来不错，但是是运行了好几次才得到这个结果的。或许是因为本地模型不够强大。换个更强的模型会更好。