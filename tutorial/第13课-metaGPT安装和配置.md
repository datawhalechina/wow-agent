

# **第02课-安装和配置**

请确保你的系统已安装Python 3.9+且版本低于3.12。你可以通过以下命令进行检查：

```powershell
python --version
```

或者直接在cmd窗口输入`python`，看看进入的是哪个版本？
**metagpt安装**
1.pip安装（如使用该方法后续运行实例还需手动拉取metagpt/ext目录，因为pip的metagpt包没有ext目录）
```powershell
pip install metagpt
```
2.git拉取
须先检查是否安装git，没有的话请先安装git。
打开刚刚安装的 VS Code，点击 Clone Git Repository，提前将 MetaGPT 的代码仓库复制好：
https://github.com/geekan/MetaGPT
如果该链接不能拉取metagithub仓库，请尝试使用其他镜像或代理，例如：
  使用 gitclone.com 代理
  git clone https://gitclone.com/github.com/geekan/MetaGPT.git
  使用 fastgit.org 代理
  git clone https://hub.fastgit.org/geekan/MetaGPT.git
  使用 kgithub.com 代理
  git clone https://kgithub.com/geekan/MetaGPT.git
然后在当前环境终端输入以下命令：
  pip install -e .
  #如需使用RAG模块，继续执行以下代码：
  pip install -e .[rag] 
**metagpt配置**
完成metagpt安装后，使用MetaGPT需要配置模型API。

1. 在当前工作目录中创建一个名为config的文件夹，并在其中添加一个名为config2.yaml的新文件。
2. 将示例config2.yaml文件的内容复制到您的新文件中。
3. 将您自己的值填入文件中：

**智谱 API**

国内的大模型，智谱的效果是非常好的。

config2.yaml

```yaml
llm:
  api_type: 'zhipuai'
  api_key: 'YOUR_API_KEY'
  model: 'glm-4'
```

**科大讯飞的大模型 Spark API：**

科大讯飞的API无法支持异步，所以回答一两个简单的问题还可以，如果要做步骤多于两个的任务，目前效果还不太可观。

config2.yaml

```yaml
llm:
  api_type: 'spark'
  app_id: 'YOUR_APPID'
  api_key: 'YOUR_API_KEY'
  api_secret: 'YOUR_API_SECRET'
  domain: 'generalv3.5'
  base_url: 'wss://spark-api.xf-yun.com/v3.5/chat'
```

**百度 千帆 API**

千帆的TPM比较低，适合当作回答问题来用。面对比较复杂的任务就会报错使用超限制。

config2.yaml

```yaml
llm:
  api_type: 'qianfan'
  api_key: 'YOUR_API_KEY'
  secret_key: 'YOUR_SECRET_KEY'
  model: 'ERNIE-Bot-4'
```

Supported models: {'ERNIE-3.5-8K-0205', 'ERNIE-Bot-turbo-AI', 'ChatLaw', 'Qianfan-Chinese-Llama-2-13B', 'Yi-34B-Chat', 'ERNIE-Bot-4', 'Llama-2-70b-chat', 'ChatGLM2-6B-32K', 'Llama-2-7b-chat', 'Llama-2-13b-chat', 'ERNIE-Bot-8k', 'ERNIE-Speed', 'ERNIE-3.5-4K-0205', 'ERNIE-Bot', 'Mixtral-8x7B-Instruct', 'EB-turbo-AppBuilder', 'ERNIE-Bot-turbo', 'BLOOMZ-7B', 'XuanYuan-70B-Chat-4bit', 'Qianfan-BLOOMZ-7B-compressed', 'Qianfan-Chinese-Llama-2-7B', 'AquilaChat-7B'}

**月之暗面 Moonshot API**

月之暗面的TPM也比较低，只能当作回答问题来用。面对复杂的任务会报错使用超限制。若要使用建议充值去提升TPM。

config2.yaml

```yaml
llm:
  api_type: 'moonshot'
  base_url: 'https://api.moonshot.cn/v1'
  api_key: 'YOUR_API_KEY'
  model: 'moonshot-v1-8k'
```

**本地ollama API**

config2.yaml


```yaml
llm:
  api_type: 'ollama'
  base_url: 'http://192.168.0.123:11434/api'
  model: 'qwen2.5:7b'
  
repair_llm_output: true
```

代码中192.168.0.123就是部署了大模型的电脑的IP，

请根据实际情况进行替换

有一个小细节需要注意，冒号后面需要有个空格，否则会报错。

如何检验自己是否配置成功呢？

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

执行上面的代码，如果输出的llm类型、密钥都没问题，就说明配置成功。
API类型: LLMType.OLLAMA
API密钥: sk-
模型: qwen2.5:7b

或者运行：

```python
from metagpt.actions import Action
```

不报错即为配置成功。

由于Agent会消耗大量的Token，如果用大模型厂商的API，不光需要花很多钱，而且每分钟请求数还很少。所以，非必要不要用大模型厂商的API。我们本地用ollama部署一个大模型，不复杂的。

访问 [https://ollama.com](https://ollama.com)。

下载Windows版本。直接安装。

安装完成后，打开命令行窗口，输入 ollama，如果出现

Usage:

Available Commands:

之类的信息，说明安装成功。

我们用qwen2:1.5b这个模型就行，整个还不到1G。

运行 ollama run qwen2:1.5b

如果出现了success，就说明安装成功。

然后会出现一个>>>符号，这就是对话窗口。可以直接输入问题。

想要退出交互页面，直接输入 /bye 就行。斜杠是需要的。否则不是退出交互页面，而是对大模型说话，它会继续跟你聊。

在浏览器中输入 127.0.0.1:11434，如果出现

Ollama is running

说明端口运行正常。

安装完ollama后，我们还需要进行配置一下，主要是两个方面。

第一：这时候模型是放在内存中的。我们希望把模型放在硬盘中。所以，我们可以在硬盘中建一个文件夹，比如：

D:\programs\ollama\models

然后新建系统环境变量。 

变量名： OLLAMA\_MODELS  

变量值： D:\programs\ollama\models  

第二：这时候的大模型只能通过127.0.0.1:11434来访问。我们希望在局域网中的任何电脑都可以访问。这也是通过新建环境变量来解决。

变量名： OLLAMA\_HOST 

变量值： 0.0.0.0:11434 

这样就完成了配置。是不是非常简单方便？

```python
# 我们先用requets库来测试一下大模型
import json
import requests
# 192.168.0.70就是部署了大模型的电脑的IP，
# 请根据实际情况进行替换
BASE_URL = "http://192.168.0.123:11434/api/chat"
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

如果想要流式输出，怎么办呢？


```python
# 我们先用requets库来测试一下大模型
import json
import requests
# 192.168.0.70就是部署了大模型的电脑的IP，
# 请根据实际情况进行替换
BASE_URL = "http://192.168.0.123:11434/api/chat"
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
response = requests.post(BASE_URL, json=payload, stream=True)  # 在这里设置stream=True告诉requests不要立即下载响应内容  
# 检查响应状态码  
if response.status_code == 200:  
    # 使用iter_content()迭代响应体  
    for chunk in response.iter_content(chunk_size=1024):  # 你可以设置chunk_size为你想要的大小  
        if chunk:  
            # 在这里处理chunk（例如，打印、写入文件等）  
            rtn = json.loads(chunk.decode('utf-8')) # 假设响应是文本，并且使用UTF-8编码  
            print(rtn["message"]["content"], end="")
else:  
    print(f"Error: {response.status_code}")  

# 不要忘记关闭响应  
response.close()
```

注意以上是Windows电脑的安装方法。苹果电脑按照上述安装好后，可以在终端进行聊天，但是用requests调用的时候，会报错找不到模型。这个问题我们暂时还没有解决方案。


