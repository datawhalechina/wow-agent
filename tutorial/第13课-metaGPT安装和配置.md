# metaGPT 安装和配置指南

请确保你的系统已安装Python 3.9+且版本低于3.12。你可以通过以下命令进行检查：

```powershell
python --version
```

或者直接在cmd窗口输入`python`，看看进入的是哪个版本。

## metagpt安装

### 方法一：pip安装
```powershell
pip install metagpt
```
注意：如使用该方法，后续运行实例还需手动拉取metagpt/ext目录，因为pip的metagpt包没有ext目录。

### 方法二：源码安装（推荐）
须先检查是否安装git，没有的话请先安装git。

打开VS Code，点击"Clone Git Repository"，使用以下仓库地址：
```
https://github.com/geekan/MetaGPT
```

如果该链接不能拉取GitHub仓库，请尝试使用其他镜像或代理：
```bash
# 使用gitclone.com代理
git clone https://gitclone.com/github.com/geekan/MetaGPT.git

# 使用fastgit.org代理
git clone https://hub.fastgit.org/geekan/MetaGPT.git

# 使用kgithub.com代理
git clone https://kgithub.com/geekan/MetaGPT.git
```

然后在当前环境终端输入以下命令：
```bash
pip install -e .
# 如需使用RAG模块，继续执行以下代码：
pip install -e .[rag] 
```

## metagpt配置

完成metagpt安装后，使用MetaGPT需要配置模型API：

1. 在当前工作目录中创建一个名为config的文件夹
2. 在其中添加一个名为config2.yaml的新文件
3. 将您自己的API信息填入文件中

### 支持的API配置示例

#### 智谱API（推荐国内用户）
```yaml
llm:
  api_type: 'zhipuai'
  api_key: 'YOUR_API_KEY'
  model: 'glm-4'
```

#### 科大讯飞Spark API
```yaml
llm:
  api_type: 'spark'
  app_id: 'YOUR_APPID'
  api_key: 'YOUR_API_KEY'
  api_secret: 'YOUR_API_SECRET'
  domain: 'generalv3.5'
  base_url: 'wss://spark-api.xf-yun.com/v3.5/chat'
```
注意：科大讯飞的API无法支持异步，适合简单问题，不适合多步骤任务。

#### 百度千帆API
```yaml
llm:
  api_type: 'qianfan'
  api_key: 'YOUR_API_KEY'
  secret_key: 'YOUR_SECRET_KEY'
  model: 'ERNIE-Bot-4'
```
支持的模型包括：ERNIE-Bot-4、ERNIE-3.5等多种模型。

#### 月之暗面Moonshot API
```yaml
llm:
  api_type: 'moonshot'
  base_url: 'https://api.moonshot.cn/v1'
  api_key: 'YOUR_API_KEY'
  model: 'moonshot-v1-8k'
```

#### 本地ollama API（推荐）
```yaml
llm:
  api_type: 'ollama'
  base_url: 'http://192.168.0.123:11434/api'
  model: 'qwen2.5:7b'
  
repair_llm_output: true
```
注意：将IP地址替换为部署大模型的电脑IP，冒号后需要有空格。

## 验证配置

使用以下代码检验配置是否成功：

```python
from metagpt.config2 import Config 
def print_llm_config():
    # 加载默认配置
    config = Config.default()

    # 获取LLM配置
    llm_config = config.llm
    # 打印LLM配置的详细信息
    if llm_config:
        print(f"API类型: {llm_config.api_type}")
        print(f"API密钥: {llm_config.api_key}")
        print(f"模型: {llm_config.model}")
    else:
        print("没有配置LLM")

if __name__ == "__main__":
    print_llm_config()
```

或者简单运行：
```python
from metagpt.actions import Action
```
不报错即为配置成功。

## 本地部署ollama（推荐）

由于Agent会消耗大量Token，本地部署更经济实用：

1. 访问 [https://ollama.com](https://ollama.com) 下载Windows版本并安装
2. 安装完成后，打开命令行窗口，输入 `ollama`，出现使用说明即安装成功
3. 运行 `ollama run qwen2:1.5b` 安装轻量级模型（不到1G）
4. 输入 `/bye` 退出交互页面
5. 在浏览器中输入 `127.0.0.1:11434`，显示"Ollama is running"表示端口正常

### ollama配置优化

1. 将模型存储在硬盘而非内存中：
   - 创建文件夹，如 `D:\programs\ollama\models`
   - 新建系统环境变量：
     - 变量名：`OLLAMA_MODELS`
     - 变量值：`D:\programs\ollama\models`

2. 允许局域网访问：
   - 新建环境变量：
     - 变量名：`OLLAMA_HOST`
     - 变量值：`0.0.0.0:11434`

## 测试ollama API

### 基本请求示例
```python
import json
import requests

BASE_URL = "http://192.168.0.123:11434/api/chat"  # 替换为你的IP
payload = {
  "model": "qwen2:1.5b",
  "messages": [
    {
      "role": "user",
      "content": "请写一篇1000字左右的文章，论述法学专业的就业前景。"
    }
  ]
}
response = requests.post(BASE_URL, json=payload)
print(response.text)
```

### 流式输出示例
```python
import json
import requests

BASE_URL = "http://192.168.0.123:11434/api/chat"  # 替换为你的IP
payload = {
  "model": "qwen2:1.5b",
  "messages": [
    {
      "role": "user",
      "content": "请写一篇1000字左右的文章，论述法学专业的就业前景。"
    }
  ],
  "stream": True
}
response = requests.post(BASE_URL, json=payload, stream=True)
if response.status_code == 200:  
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            rtn = json.loads(chunk.decode('utf-8'))
            print(rtn["message"]["content"], end="")
else:  
    print(f"Error: {response.status_code}")  

response.close()
```

注意：以上是Windows电脑的安装方法。苹果电脑安装后可以在终端进行聊天，但用requests调用时可能会报错找不到模型，目前尚无解决方案。
