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

```python
def get_completion(prompt):
    response = client.chat.completions.create(
        model="glm-4-flash",  # 填写需要调用的模型名称
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content
```

先试试这个大模型是否可用：
```python
response = get_completion("你是谁？")
print(response)
```
我是一个人工智能助手，专门设计来帮助用户解答问题、提供信息以及执行各种任务。我的目标是成为您生活中的助手，帮助您更高效地获取所需信息。有什么我可以帮您的吗？

到这一步说明大模型可用。如果得不到这个回答，就说明大模型不可用，不要往下进行，要先去搞定一个可用的大模型。



智能体需要大量的prompt工程。代码是调用机器能力的工具， Prompt 是调用大模型能力的工具。Prompt 越来越像新时代的编程语言。让我们来学习一下著名的LangGPT。

参考：[https://github.com/EmbraceAGI/LangGPT](https://github.com/EmbraceAGI/LangGPT)

## **什么是结构化 Prompt ？**

结构化的思想很普遍，结构化内容也很普遍，我们日常写作的文章，看到的书籍都在使用标题、子标题、段落、句子等语法结构。结构化 Prompt 的思想通俗点来说就是像写文章一样写 Prompt。

为了阅读、表达的方便，我们日常有各种写作的模板，用来控制内容的组织呈现形式。例如古代的八股文、现代的简历模板、学生实验报告模板、论文模板等等模板。所以结构化编写 Prompt 自然也有各种各样优质的模板帮助你把 Prompt 写的更轻松、性能更好。所以写结构化 Prompt 可以有各种各样的模板，你可以像用 PPT 模板一样选择或创造自己喜欢的模板。

## **LangGPT 变量：**

我们发现 ChatGPT 可以识别各种良好标记的层级结构内容。大模型可以识别文章的标题，段落名，段落正文等层级结构，如果我们告诉他标题，模型知道我们指的是标题以及标题下的正文内容。

这意味着我们将 prompt 的内容用结构化方式呈现，并设置标题即可方便的引用，修改，设置 prompt 内容。可以直接使用段落标题来指代大段内容，也可以告诉ChatGPT修改调整指定内容。这类似于编程中的变量，因此我们可以将这种标题当做变量使用。

Markdown 的语法层级结构很好，适合编写 prompt，因此 LangGPT 的变量基于 markdown语法。实际上除 markdown外各种能实现标记作用，如 json,yaml, 甚至好好排版好格式 都可以。

变量为 Prompt 的编写带来了很大的灵活性。使用变量可以方便的引用角色内容，设置和更改角色属性。这是一般的 prompt 方法实现起来不方便的。

## **LangGPT 模板：**

ChatGPT 十分擅长角色扮演，大部分优质 prompt 开头往往就是 “我希望你作为xxx”，“我希望你扮演xxx” 的句式定义一个角色，只要提供角色说明，角色行为，技能等描述，就能做出很符合角色的行为。

如果你熟悉编程语言里的 “对象”，就知道其实 prompt 的“角色声明”和类声明很像。因此 可以将 prompt 抽象为一个角色 （Role），包含名字，描述，技能，工作方法等描述，然后就得到了 LangGPT 的 Role 模板。

使用 Role 模板，只需要按照模板填写相应内容即可。

除了变量和模板外，LangGPT 还提供了命令，记忆器，条件句等语法设置方法。

## **结构化 prompt 的几个概念：**

**标识符**：#, <> 等符号(-, []也是)，这两个符号依次标识标题,变量，控制内容层级，用于标识层次结构。

**属性词**：Role, Profile, Initialization 等等，属性词包含语义，是对模块下内容的总结和提示，用于标识语义结构。

使用分隔符清晰标示输入的不同部分,像三重引号、XML标记、节标题等分隔符可以帮助标示需要以不同方式处理的文本部分。

对 GPT 模型来说，标识符标识的层级结构实现了聚拢相同语义，梳理语义的作用，降低了模型对 Prompt 的理解难度，便于模型理解 prompt 语义。

属性词实现了对 prompt 内容的语义提示和归纳作用，缓解了 Prompt 中不当内容的干扰。 使用属性词与 prompt 内容相结合，实现了局部的总分结构，便于模型提纲挈领的获得 prompt 整体语义。

一个好的结构化 Prompt 模板，某种意义上是构建了一个好的全局思维链。 如 LangGPT 中展示的模板设计时就考虑了如下思维链:

Role (角色) -> Profile（角色简介）—> Profile 下的 skill (角色技能) -> Rules (角色要遵守的规则) -> Workflow (满足上述条件的角色的工作流程) -> Initialization (进行正式开始工作的初始化准备) -> 开始实际使用

构建 Prompt 时，不妨参考优质模板的全局思维链路，熟练掌握后，完全可以对其进行增删改留调整得到一个适合自己使用的模板。例如当你需要控制输出格式，尤其是需要格式化输出时，完全可以增加 Ouput 或者 OutputFormat 这样的模块

**保持上下文语义一致性**

包含两个方面，一个是格式语义一致性，一个是内容语义一致性。

- 格式语义一致性是指标识符的标识功能前后一致。 最好不要混用，比如 # 既用于标识标题，又用于标识变量这种行为就造成了前后不一致，这会对模型识别 Prompt 的层级结构造成干扰。

- 内容语义一致性是指思维链路上的属性词语义合适。 例如 LangGPT 中的 Profile 属性词，原来是 Features，但实践+思考后我更换为了 Profile，使之功能更加明确：即角色的简历。结构化 Prompt 思想被诸多朋友广泛使用后衍生出了许许多多的模板，但基本都保留了 Profile 的诸多设计，说明其设计是成功有效的。

**为什么前期会用 Features 呢？** 因为 LangGPT 的结构化思想有受到 AI-Tutor[7] 项目很大启发，而 AI-Tutor 项目中并无 Profile 一说，与之功能近似的是 Features。但 AI-Tutor 项目中的提示词过于复杂，并不通用。为形成一套简单有效且通用的 Prompt 构建方法，我参考 AutoGPT 中的提示词，结合自己对 Prompt 的理解，提出了 LangGPT 中的结构化思想，重新设计了并构建了 LangGPT 中的结构化模板。

内容语义一致性还包括属性词和相应模块内容的语义一致。 例如 Rules 部分是角色需要遵守规则，则不宜将角色技能、描述大量堆砌在此。

## LangGPT 中的 Role （角色）模板

### Role: Your_Role_Name

#### Profile

- Author: YZFly
- Version: 0.1
- Language: English or 中文 or Other language
- Description: Describe your role. Give an overview of the character's characteristics and skills

##### Skill-1
1.技能描述1
2.技能描述2

##### Skill-2
1.技能描述1
2.技能描述2

### Rules
1. Don't break character under any circumstance.
2. Don't talk nonsense and make up facts.

### Workflow
1. First, xxx
2. Then, xxx
3. Finally, xxx

### Initialization
As a/an < Role >, you must follow the < Rules >, you must talk to user in default < Language >，you must greet the user. Then introduce yourself and introduce the < Workflow >.

Prompt Chain 将原有需求分解，通过用多个小的 Prompt 来串联/并联，共同解决一项复杂任务。

Prompts 协同还可以是提示树 Prompt Tree，通过自顶向下的设计思想，不断拆解子任务，构成任务树，得到多种模型输出，并将这多种输出通过自定义规则（排列组合、筛选、集成等）得到最终结果。 API 版本的 Prompt Chain 结合编程可以将整个流程变得更加自动化

## **prompt设计方法论**

1. 数据准备。收集高质量的案例数据作为后续分析的基础。
2. 模型选择。根据具体创作目的,选择合适的大语言模型。
3. 提示词设计。结合案例数据,设计初版提示词;注意角色设置、背景描述、目标定义、约束条件等要点。
4. 测试与迭代。将提示词输入 GPT 进行测试,分析结果;通过追问、深度交流、指出问题等方式与 GPT 进行交流,获取优化建议。
5. 修正提示词。根据 GPT 提供的反馈,调整提示词的各个部分,强化有效因素,消除无效因素。
6. 重复测试。输入经修正的提示词重新测试,比较结果,继续追问GPT并调整提示词。
7. 循环迭代。重复上述测试-交流-修正过程,直到结果满意为止。
8. 总结提炼。归纳提示词优化过程中获得的宝贵经验,形成设计提示词的最佳实践。
9. 应用拓展。将掌握的方法论应用到其他创意内容的设计中,不断丰富提示词设计的技能。


让我们为本课的智能体定义各种prompt。

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