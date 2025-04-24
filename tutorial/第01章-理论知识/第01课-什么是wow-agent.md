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
