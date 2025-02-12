wow-agent是自塾（zishu.co）出品的第三个开源项目。自塾在2024年出品了三个开源项目，分别是：

AI落地三件套
https://github.com/datawhalechina/wow-fullstack  
https://github.com/datawhalechina/wow-rag  
https://github.com/datawhalechina/wow-agent  

我眼中的AI机会在哪里？

做技术还是做应用？应用
生在中国，天然的优势就是做应用

做to C 还是做to B？to B
对比互联网革命。互联网革命改变的是人与人之间的连接关系，是消费侧革命，因此做to C的机会更大。而人工智能革命改变的是生产力，是供给侧革命，因此做to B的机会更大。

to 大B还是 to 小B？to 大B
大B和小B的分界线是员工规模，员工数量大于100人的是大B，员工数量小于100人的是小B。大B的主要需求是自动化、智能化。小B的主要需求是获客。拓客与留客同等重要。对于大B来说，留客甚至会更重要。帮助大B用AI服务好现有客户，留住现有客户。

做大模型还是做Agent？ Agent
这个世界当前最强大的生产力是大模型。大模型是脑，它必须有四肢才能赋能千行百业。这个四肢就是Agent，Agent市场必定是比大模型市场大得多的市场。

AI + X 还是 X + AI ？X + AI
AI落地，关键不在于AI，而在于行业经验。我们要充分尊重各行各业的行业经验，并把它放在基础位置。用AI去赋能行业经验，而不是取代行业经验。所以我们做 X + AI。

如何做X + AI？AI落地三件套
wow-fullstack  wow-rag  wow-agent 

2025年计划稳定在这三款开源项目中，持续打磨迭代。

通过观察市场上比较流行的开源多智能体框架，例如 metagpt、crewai、camel-ai、autogen，我们会发现这些框架安装起来有很多依赖，我们来看看安装一个metagpt-simple的依赖有多少？说出来可能吓你一跳，有下面这116个依赖库。注意哦，这可是metagpt的简易版本，如果要安装带其他功能的版本，还会增加许多依赖库。crewai的依赖库数量可能更多。

ruamel.yaml, rsa, referencing, pylance, pyasn1-modules, protobuf, portalocker, Pillow, pathable, overrides, networkx, mypy-extensions, more-itertools, mdurl, MarkupSafe, lxml, loguru, libcst, lazy-object-proxy, jupyterlab-widgets, joblib, jmespath, isodate, importlib-metadata, hyperframe, httplib2, hpack, grpcio, gitdb, future, fire, faiss_cpu, et-xmlfile, diskcache, dill, deprecation, deprecated, defusedxml, cloudpickle, click, chardet, cffi, camel-converter, cachetools, asgiref, anytree, aiolimiter, aiofiles, werkzeug, volcengine-python-sdk, typing-inspect, scikit_learn, python_docx, proto-plus, prance, playwright, pandas, opentelemetry-proto, opentelemetry-api, openpyxl, multiprocess, markdown-it-py, jsonschema-specifications, jsonschema-path, jinja2, h2, gymnasium, grpcio-tools, googleapis-common-protos, google-auth, gitpython, Django, curl-cffi, cryptography, cloudevents, botocore, bce-python-sdk, azure-core, zhipuai, ta, s3transfer, rich, pydantic-settings, opentelemetry-semantic-conventions, opentelemetry-exporter-otlp-proto-common, lancedb, jsonschema, ipywidgets, grpcio-status, google-auth-httplib2, google-api-core, channels, anthropic, typer, spark_ai_python, qdrant-client, opentelemetry-sdk, openapi-schema-validator, nbformat, msal, meilisearch, google-api-python-client, dashscope, boto3, qianfan, opentelemetry-exporter-otlp-proto-http, openapi-spec-validator, nbclient, msal-extensions, google-ai-generativelanguage, openapi_core, google-generativeai, azure-identity, agentops, semantic-kernel, metagpt-simple


框架本来是用于减少我们的代码量，但是如果我们只是想要实现一个简易的功能，但是用了这个框架却给你安装了上百个依赖库，你觉得划算吗？

所以，（此处应该有掌声，或者，点个star吧！）wow-agent 应运而生。wow-agent致力于在代码行数和依赖库数量之间取得均衡的最小值，用最划算的方式帮助您在本地搭建AI Agent，嵌入到您的生产工作环节中。

好的，既然我们的目标是构建AI Agent，那就让我们先来学习一下Agent的基本概念吧！谷歌不是2025年元旦左右时候出了个《New whitepaper Agents》嘛？我们把谷歌的这个PDF文件丢给智谱，让智谱给我们根据这个PDF文件写个Agent综述，于是就有了下面这篇短文：

生成式AI模型（LLMs）近年来取得了惊人的进步，能够创作文本、图像、代码等，展现出巨大的潜力。然而，LLMs仍然存在局限性，它们无法与外界互动，知识局限于训练数据，限制了其应用范围。为了突破这一限制，我们引入了“Agents”的概念，即能够利用工具与外界交互，并根据目标进行自主决策和行动的智能体。
### Agents的诞生：从LLMs到自主行动
LLMs强大的语言理解和生成能力，为构建Agents奠定了基础。然而，LLMs的局限性也显而易见：
* **知识局限性**：LLMs的知识仅限于训练数据，无法获取实时信息和外部知识库。
* **行动局限性**：LLMs无法与外界交互，无法执行实际操作。
为了克服这些局限性，谷歌的研究人员在《New whitepaper Agents》详细论述了“Agent”的概念，将LLMs与工具和编排层相结合，赋予其自主行动的能力。
### Agents的核心组件
一个完整的Agent主要由三个核心组件构成：

**1. 模型 (Model)**:
* **角色**：作为Agent的“大脑”，负责理解用户输入，进行推理和规划，并选择合适的工具进行执行。
* **类型**：常用的模型包括ReAct、Chain-of-Thought、Tree-of-Thought等，它们提供不同的推理框架，帮助Agent进行多轮交互和决策。
* **重要性**：模型是Agent的核心，其推理能力决定了Agent的行动效率和准确性。

**2. 工具 (Tools)**:
* **角色**：作为Agent与外界交互的“桥梁”，允许Agent访问外部数据和服务，执行各种任务。
* **类型**：工具可以是各种API，例如数据库查询、搜索引擎、代码执行器、邮件发送器等。
* **重要性**：工具扩展了Agent的能力，使其能够执行更复杂的任务。

**3. 编排层 (Orchestration Layer)**:
* **角色**：负责管理Agent的内部状态，协调模型和工具的使用，并根据目标指导Agent的行动。
* **类型**：编排层可以使用各种推理框架，例如ReAct、Chain-of-Thought等，帮助Agent进行规划和决策。
* **重要性**：编排层是Agent的“指挥中心”，负责协调各个组件，确保Agent的行动符合目标。
### Agents的运作机制：从输入到输出
Agent的运作过程可以概括为以下几个步骤：
1. **接收输入**：Agent接收用户的指令或问题。
2. **理解输入**：模型理解用户的意图，并提取关键信息。
3. **推理规划**：模型根据用户输入和当前状态，进行推理和规划，确定下一步行动。
4. **选择工具**：模型根据目标选择合适的工具。
5. **执行行动**：Agent使用工具执行行动，例如查询数据库、发送邮件等。
6. **获取结果**：Agent获取工具执行的结果。
7. **输出结果**：Agent将结果输出给用户，或进行下一步行动。
### Agents的优势：超越LLMs
与传统的LLMs相比，Agents具有以下优势：
* **知识扩展**：通过工具，Agent可以访问实时信息和外部知识库，突破训练数据的限制，提供更准确和可靠的信息。
* **自主行动**：Agent可以根据目标进行自主决策和行动，无需人工干预，提高效率和灵活性。
* **多轮交互**：Agent可以管理对话历史和上下文，进行多轮交互，提供更自然和流畅的用户体验。
* **可扩展性**：Agent可以通过添加新的工具和模型，扩展其功能和应用范围。
### Agents的应用：从智能客服到虚拟助手
Agents的应用范围非常广泛，例如：
* **智能客服**：Agent可以自动回答用户问题，处理订单，解决客户问题，提高客户满意度。
* **个性化推荐**：Agent可以根据用户的兴趣和行为，推荐商品、内容、服务等，提升用户体验。
* **虚拟助手**：Agent可以帮助用户管理日程、预订行程、发送邮件等，提高工作效率。
* **代码生成**：Agent可以根据用户的需求，自动生成代码，提高开发效率。
* **智能创作**：Agent可以根据用户的需求，创作诗歌、小说、剧本等，激发创作灵感。
* **知识图谱构建**：Agent可以从文本中提取知识，构建知识图谱，用于知识管理和推理。
### Agents的开发工具：从LangChain到Vertex AI
为了方便开发Agents，Google提供了多种工具和平台，例如：
* **LangChain**：一个开源库，可以帮助开发者构建和部署Agents。LangChain提供了一套API，方便开发者将LLMs与工具和编排层结合，构建功能强大的Agents。
* **LangGraph**：一个开源库，可以帮助开发者构建和可视化Agents。LangGraph提供了一套图形化界面，方便开发者设计和测试Agents。
* **Vertex AI**：一个云平台，提供各种AI工具和服务，例如Vertex Agent Builder、Vertex Extensions、Vertex Function Calling等，可以帮助开发者快速构建和部署Agents。Vertex AI提供了强大的基础设施和工具，方便开发者进行Agent开发、测试、部署和管理。
### Agents的未来：更智能、更强大的AI
Agents的未来充满无限可能，随着技术的不断发展，Agent将变得更加智能和强大，能够解决更复杂的问题，并应用于更广泛的领域。
* **更先进的模型**：未来将出现更强大的语言模型，能够进行更复杂的推理和规划，为Agent提供更强的决策能力。
* **更丰富的工具**：未来将出现更多种类的工具，例如自然语言处理、图像识别、语音识别、机器人控制等，为Agent提供更丰富的交互方式。
* **更智能的编排层**：未来将出现更智能的编排层，能够更好地协调模型和工具的使用，并提高Agent的效率和灵活性。
* **Agent Chaining**：未来将出现更多专门化的Agent，它们可以协同工作，解决更复杂的问题。
* **多模态交互**：未来Agent将能够处理多种模态的数据，例如文本、图像、语音等，提供更丰富的用户体验。
* **人机协作**：未来Agent将与人类进行更紧密的合作，共同完成更复杂的任务。
### 结语：Agent，AI的未来
Agents是生成式AI模型的进阶形态，它们能够利用工具与外界交互，并根据目标进行自主决策和行动，具有更广泛的应用范围和更强大的能力。随着技术的不断发展，Agent将改变我们的生活和工作方式，并推动人工智能的进步。未来，Agent将成为人工智能发展的重要方向，为我们带来更智能、更便捷的未来。
