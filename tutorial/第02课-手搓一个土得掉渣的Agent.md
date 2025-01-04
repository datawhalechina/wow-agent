先准备需要的python库：
pip install openai python-dotenv
然后配置模型。

本节课根据智谱官方glm-cookbook中的Agent案例改编而来，特此鸣谢。

国内模型可以是智谱、Yi、千问deepseek等等。KIMI是不行的，因为Kimi家没有嵌入模型。
要想用openai库对接国内的大模型，对于每个厂家，我们都需要准备四样前菜：
- 第一：一个api_key，这个需要到各家的开放平台上去申请。 
- 第二：一个base_url，这个需要到各家的开放平台上去拷贝。 
- 第三：他们家的对话模型名称。  

在这三样东西里面，第一个api_key你要好好保密，不要泄露出去。免得被人盗用，让你的余额用光光。

后面两样东西都是公开的。

比如对于智谱：
```python
base_url = "https://open.bigmodel.cn/api/paas/v4/"
chat_model = "glm-4-flash"
```

在项目的根目录新建一个txt文件，把文件名改成.env。需要注意的是，前面这个点儿不能省略。因为这个文件就叫做dotenv，dot就是点儿的意思。
里面填入一行字符串：
ZHIPU_API_KEY=你的api_key

把ZHIPU_API_KEY写到.env文件的原因是为了保密，同时可以方便地在不同的代码中读取。


对于阿里的千问：
```python
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
chat_model = "qwen-plus"
```
.env请模仿上边智谱的例子自行创建。

对于自塾提供的默认API
```python
base_url = "http://43.200.7.56:8008/v1"
chat_model = "glm-4-flash"
```
本项目自带的.env可以直接拿来用。里面就是自塾提供的api_key。

我们这里以自塾默认API为例。



咱们现在先把四样前菜准备一下吧：

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

构造client
构造client只需要两个东西：api_key和base_url。

```python
from openai import OpenAI
client = OpenAI(
    api_key = api_key,
    base_url = base_url
)
```

有了这个client，我们就可以去实现各种能力了。

定义各种prompt。

```python
sys_prompt = """你是一个聪明的客服。您将能够根据用户的问题将不同的任务分配给不同的人。您有以下业务线：
1.用户注册。如果用户想要执行这样的操作，您应该发送一个带有"registered workers"的特殊令牌。并告诉用户您正在调用它。
2.用户数据查询。如果用户想要执行这样的操作，您应该发送一个带有"query workers"的特殊令牌。并告诉用户您正在调用它。
3.删除用户数据。如果用户想执行这种类型的操作，您应该发送一个带有"delete workers"的特殊令牌。并告诉用户您正在调用它。
"""
registered_prompt = """
您的任务是根据用户信息存储数据。您需要从用户那里获得以下信息：
1.用户名、性别、年龄
2.用户设置的密码
3.用户的电子邮件地址
如果用户没有提供此信息，您需要提示用户提供。如果用户提供了此信息，则需要将此信息存储在数据库中，并告诉用户注册成功。
存储方法是使用SQL语句。您可以使用SQL编写插入语句，并且需要生成用户ID并将其返回给用户。
如果用户没有新问题，您应该回复带有 "customer service" 的特殊令牌，以结束任务。
"""
query_prompt = """
您的任务是查询用户信息。您需要从用户那里获得以下信息：
1.用户ID
2.用户设置的密码
如果用户没有提供此信息，则需要提示用户提供。如果用户提供了此信息，那么需要查询数据库。如果用户ID和密码匹配，则需要返回用户的信息。
如果用户没有新问题，您应该回复带有 "customer service" 的特殊令牌，以结束任务。
"""
delete_prompt = """
您的任务是删除用户信息。您需要从用户那里获得以下信息：
1.用户ID
2.用户设置的密码
3.用户的电子邮件地址
如果用户没有提供此信息，则需要提示用户提供该信息。
如果用户提供了这些信息，则需要查询数据库。如果用户ID和密码匹配，您需要通知用户验证码已发送到他们的电子邮件，需要进行验证。
如果用户没有新问题，您应该回复带有 "customer service" 的特殊令牌，以结束任务。
"""
```

定义一个智能客服智能体。

```python
class SmartAssistant:
    def __init__(self):
        self.client = client 

        self.system_prompt = sys_prompt
        self.registered_prompt = registered_prompt
        self.query_prompt = query_prompt
        self.delete_prompt = delete_prompt

        # Using a dictionary to store different sets of messages
        self.messages = {
            "system": [{"role": "system", "content": self.system_prompt}],
            "registered": [{"role": "system", "content": self.registered_prompt}],
            "query": [{"role": "system", "content": self.query_prompt}],
            "delete": [{"role": "system", "content": self.delete_prompt}]
        }

        # Current assignment for handling messages
        self.current_assignment = "system"

    def get_response(self, user_input):
        self.messages[self.current_assignment].append({"role": "user", "content": user_input})
        while True:
            response = self.client.chat.completions.create(
                model=chat_model,
                messages=self.messages[self.current_assignment],
                temperature=0.9,
                stream=False,
                max_tokens=2000,
            )

            ai_response = response.choices[0].message.content
            if "registered workers" in ai_response:
                self.current_assignment = "registered"
                print("意图识别:",ai_response)
                print("switch to <registered>")
                self.messages[self.current_assignment].append({"role": "user", "content": user_input})
            elif "query workers" in ai_response:
                self.current_assignment = "query"
                print("意图识别:",ai_response)
                print("switch to <query>")
                self.messages[self.current_assignment].append({"role": "user", "content": user_input})
            elif "delete workers" in ai_response:
                self.current_assignment = "delete"
                print("意图识别:",ai_response)
                print("switch to <delete>")
                self.messages[self.current_assignment].append({"role": "user", "content": user_input})
            elif "customer service" in ai_response:
                print("意图识别:",ai_response)
                print("switch to <customer service>")
                self.messages["system"] += self.messages[self.current_assignment]
                self.current_assignment = "system"
                return ai_response
            else:
                self.messages[self.current_assignment].append({"role": "assistant", "content": ai_response})
                return ai_response

    def start_conversation(self):
        while True:
            user_input = input("User: ")
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting conversation.")
                break
            response = self.get_response(user_input)
            print("Assistant:", response)
```

来运用一下这个Agent。

```python
assistant = SmartAssistant()
assistant.start_conversation()
```

输出如下：
Assistant: 您好，liwei。请问有什么可以帮助您的吗？如果您需要注册、查询或删除用户数据，请告诉我具体的需求，我将根据您的需求调用相应的业务线。
意图识别: 要查看您的账户信息，我需要调用用户数据查询的服务。请稍等，我将发送一个带有"query workers"的特殊令牌以执行这个操作。<|assistant|>query workers
switch to <query>
Assistant: 为了查看您的账户信息，请提供以下信息：
1. 您的用户ID
2. 您设置的密码

如果这些信息不全，请补充完整，以便我能够查询数据库并返回您的账户信息。如果您不需要查询账户信息，或者有其他问题，请告诉我。
Assistant: 您已提供了用户ID。为了完成查询，请提供您设置的密码。
意图识别: 用户ID 1001 和密码 123456 匹配。以下是您的账户信息：

- 用户ID：1001
- 用户名：JohnDoe
- 邮箱地址：johndoe@example.com
- 注册日期：2021-01-01
- 余额：$500.00

如果您需要进一步的帮助或有其他问题，请告诉我。如果已经处理完您的问题，您可以直接回复 "customer service" 来结束任务。
switch to <customer service>
Assistant: 用户ID 1001 和密码 123456 匹配。以下是您的账户信息：

- 用户ID：1001
- 用户名：JohnDoe
- 邮箱地址：johndoe@example.com
- 注册日期：2021-01-01
- 余额：$500.00

如果您需要进一步的帮助或有其他问题，请告诉我。如果已经处理完您的问题，您可以直接回复 "customer service" 来结束任务。
Assistant: 抱歉，您提供的密码与我们的系统记录不匹配。请确认您提供的密码是否正确，或者如果您需要帮助重置密码，请告诉我。
意图识别: customer service
switch to <customer service>
Assistant: customer service
Exiting conversation.