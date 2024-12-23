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

然后配置对话模型和嵌入模型。
```python
# 配置对话模型
from llama_index.llms.ollama import Ollama
llm = Ollama(base_url="http://192.168.0.123:11434", model="qwen2:7b")
```

```python
# 配置嵌入模型
from llama_index.embeddings.ollama import OllamaEmbedding
embedding = OllamaEmbedding(base_url="http://192.168.0.123:11434", model_name="qwen2:7b")
```

导入Llama-index相关的库，并配置对话模型和嵌入模型。
```python
from llama_index.core.agent import ReActAgent  
from llama_index.core.tools import FunctionTool  
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings  
from llama_index.core.tools import QueryEngineTool   
from llama_index.core import SQLDatabase  
from llama_index.core.query_engine import NLSQLTableQueryEngine  
from sqlalchemy import create_engine, select  

# 构建本地嵌入模型
Settings.embed_model = embedding

# 创建本地大模型  
Settings.llm = llm
```


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
# 构建ReActAgent
agent = ReActAgent.from_tools([multiply_tool, add_tool, staff_tool], verbose=True)  
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
