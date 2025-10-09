# OpenAI Agents SDK | 大模型智能体框架实战指南

🤖 OpenAI Agents SDK 官方框架
从安装到多模型集成，构建你的智能体应用

GitHub stars GitHub forks Python zread
在线阅读 English Version 讨论交流  

🎯 系统化学习  |    完整的智能体框架体系	

🛠️ 动手实践      |    快速集成与测试案例	

🚀 生产就绪      |    多模型兼容与异步支持	

📊 扩展性强      |    支持100+ LLM模型  

## 项目简介（中文 | English）

本项目是一个面向大模型应用开发者的OpenAI Agents SDK实战教程，旨在通过简明路径和代码实践，帮助开发者快速上手2025年3月推出的官方智能体框架。该框架与MCP协议深度融合，默认使用OpenAI Chat Completions API，但通过LiteLLM轻松切换到DeepSeek、智谱GLM、阿里DashScope或Mistral等模型，构建高效的多代理工作流和智能问答系统。

主要内容包括：  

- 框架核心：代理构建、手动工具、会话管理和追踪调试  
- 多模型集成：LiteLLM与OpenAI兼容端点的配置与切换  
- 异步/同步执行：Jupyter兼容与循环优化  
- 日志与安全：自定义日志与敏感数据保护

## 项目意义

随着大模型生态的演进，OpenAI Agents SDK已成为构建多代理应用的首选框架。然而，现有的教程往往忽略国内模型集成和异步兼容问题。本项目从实践出发，结合框架最新特性，帮助开发者：  

- 快速掌握代理循环与工具集成  
- 实现模型无关的跨提供商部署  
- 优化生产级应用的安全与调试  
- 构建可扩展的智能体系统

## 项目受众

本项目适合以下人群学习：  

- 具备Python基础、对智能体框架感兴趣的开发者  
- 希望集成国内大模型的AI工程师  
- 构建代理应用的系统开发者  
- 对OpenAI工具链有学习需求的研究人员

前置要求：  

- 掌握Python基础语法和常用库  
- 了解基本的LLM API概念（推荐但非必需）  
- 具备虚拟环境操作能力

## 项目亮点

- **多模型兼容**：无缝支持OpenAI、DeepSeek、智谱等100+模型，无需重写代码  
- **异步优先**：内置Runner支持同步/异步，Jupyter Notebook友好  
- **轻量高效**：代理、手动和会话管理一站式集成，易于生产部署  
- **安全导向**：日志自定义与敏感数据屏蔽，防范API密钥泄露  
- **实战导向**：从Hello World到多代理笑话生成，快速上手框架

## 内容大纲

**第一部分：框架入门**  

- 01-安装与配置.md 📖 查看章节  
  - 虚拟环境搭建  
  - 依赖安装与API密钥管理
- 02-初步尝鲜.md 📖 查看章节  
  - Agents SDK简介与MCP融合  
  - 核心组件：代理、Runner与工具

**第二部分：模型集成**  

- 03-Agent配置.md 📖 查看章节  
  - Hello World代理示例  
  - 同步/异步运行
- 04-Agent生命周期.md 📖 查看章节  
  - LiteLLM配置DeepSeek  
  - 智谱GLM与Mistral实践

**第三部分：高级特性**  

- 05-运行.md 📖 查看章节  
  - 历史管理与SQLite/Redis支持  
  - 内置追踪与调试
- 06-工具.md 📖 查看章节  
  - 详细日志启用  
  - 模型设置与敏感数据保护

**第四部分：扩展应用**

- 07-MCP.md 📖 查看章节  
  - Handoff与工具集成  
  - 生产级循环优化

## 任务安排

| 任务编号         | 任务内容                         | 截止时间               |
| ---------------- | -------------------------------- | ---------------------- |
| 10月13日正式开始 |                                  |                        |
| Task01           | 编程配置小试牛刀 (第1、2节)      | 截止时间 10月15日03:00 |
| Task02           | Agent模块 (第3、4、5节)          | 截止时间 10月18日03:00 |
| Task03           | 工具模块 (第6、7节)              | 截止时间 10月20日03:00 |
| Task04           | 综合Agent开发 (第8、9、10、11节) | 截止时间 10月24日03:00 |

## 目录结构说明

openai-agents-sdk/
├── docs/           # 教程文档
├── code/           # 代码示例
├── examples/       # 实战案例
└── README.md       # 项目说明  

## 贡献者名单

| 姓名                                     | 职责                         | 简介         |
| ---------------------------------------- | ---------------------------- | ------------ |
| [黎伟](https://github.com/omige)         | 项目负责人                   | 规划教程整体 |
| [胡琦](https://github.com/hu-qi)         | zigent章节                   | 塾员         |
| [珞索](https://github.com/galaAella)     | metagpt章节                  | 塾员         |
| [陈嘉诺](https://github.com/Tangent-90C) | openai-agent SDK章节         | 塾员         |
| [汤耀月](https://github.com/SuTang-vain) | openai-agent SDK章节项目说明 | 塾员         |

**特别感谢**
感谢OpenAI官方文档与LiteLLM社区的支持
感谢所有为框架做出贡献的开发者们  

## 参与贡献

- 如果你发现了一些问题，可以提Issue进行反馈，如果提完没有人回复你可以联系[胡琦](https://github.com/hu-qi)同学进行反馈跟进~  
- 如果你想参与贡献本项目，可以提Pull request，如果提完没有人回复你可以联系[黎伟](https://github.com/omige)同学进行反馈跟进~  
- 如果你对 Datawhale 很感兴趣并想要发起一个新的项目，请按照[Datawhale开源项目指南](https://github.com/datawhalechina/DOPMC/blob/main/GUIDE.md)进行操作即可~

------

## 关于 Datawhale

**Datawhale公众号二维码粘贴处**
扫描二维码关注 Datawhale 公众号，获取更多优质开源内容  

------

## LICENSE

[![知识共享许可协议](https://camo.githubusercontent.com/3902ebad4b3a5ba7e8f4caba5f7cfed6c3e8b7c020c502ad250fbc04f8bc7c25/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6c6963656e73652d434325323042592d2d4e432d2d5341253230342e302d6c6967687467726579)](http://creativecommons.org/licenses/by-nc-sa/4.0/)
本作品采用[知识共享署名-非商业性使用-相同方式共享 4.0 国际许可协议](http://creativecommons.org/licenses/by-nc-sa/4.0/)进行许可。

*注：默认使用CC 4.0协议，也可根据自身项目情况选用其他协议*
