# MetaGPT快速尝鲜

## **智能体**

在MetaGPT看来，可以将智能体想象成环境中的数字人，其中

智能体 = 大语言模型（LLM） + 观察 + 思考 + 行动 + 记忆

这个公式概括了智能体的功能本质。为了理解每个组成部分，让我们将其与人类进行类比：

1. **大语言模型（LLM）**：LLM作为智能体的"大脑"部分，使其能够处理信息，从交互中学习，做出决策并执行行动。
2. **观察**：这是智能体的感知机制，使其能够感知其环境。智能体可能会接收来自另一个智能体的文本消息、来自监视摄像头的视觉数据或来自客户服务录音的音频等一系列信号。这些观察构成了所有后续行动的基础。
3. **思考**：思考过程涉及分析观察结果和记忆内容并考虑可能的行动。这是智能体内部的决策过程，其可能由LLM进行驱动。
4. **行动**：这些是智能体对其思考和观察的显式响应。行动可以是利用LLM生成代码，或是手动预定义的操作，如阅读本地文件。此外，智能体还可以执行使用工具的操作，包括在互联网上搜索天气，使用计算器进行数学计算等。
5. **记忆**：智能体的记忆存储过去的经验。这对学习至关重要，因为它允许智能体参考先前的结果并据此调整未来的行动。

## **多智能体**

多智能体系统可以视为一个智能体社会，其中

多智能体 = 智能体 + 环境 + 标准流程（SOP） + 通信 + 经济

这些组件各自发挥着重要的作用：

1. **智能体**：在上面单独定义的基础上，在多智能体系统中的智能体协同工作，每个智能体都具备独特有的LLM、观察、思考、行动和记忆。
2. **环境**：环境是智能体生存和互动的公共场所。智能体从环境中观察到重要信息，并发布行动的输出结果以供其他智能体使用。
3. **标准流程（SOP）**：这些是管理智能体行动和交互的既定程序，确保系统内部的有序和高效运作。例如，在汽车制造的SOP中，一个智能体焊接汽车零件，而另一个安装电缆，保持装配线的有序运作。
4. **通信**：通信是智能体之间信息交流的过程。它对于系统内的协作、谈判和竞争至关重要。
5. **经济**：这指的是多智能体环境中的价值交换系统，决定资源分配和任务优先级。

## **任务**

对于每一个任务，至少要明确两点：目标和期望。目标和期望都可以用自然语言去描述。

其他需要明确的是上下文、回调、输出、使用的工具。

回调可以是一个python函数。使用的工具可以是一个python列表。

你可以用pydantic去约束输出的格式，把大模型的模糊输出变为强制结构化输出。

## **工具**

一个常用的工具就是搜索引擎。例如谷歌的 [serper](https://serper.dev/)。国内的替代品是什么？

还有爬虫工具

## **实践操作**

新建一个Jupyter notebook，把下面的代码拷贝进去：

```python
import asyncio
from metagpt.roles import (
    Architect,
    Engineer,
    ProductManager,
    ProjectManager,
)
from metagpt.team import Team
async def startup(idea: str):
    company = Team()
    company.hire(
        [
            ProductManager(),
            Architect(),
            ProjectManager(),
            Engineer(),
        ]
    )
    company.invest(investment=3.0)
    company.run_project(idea=idea)

    await company.run(n_round=5)
```

在上面的代码中，我们直接用默认的角色即可。这些角色都要做什么动作都已经写好了，直接拿过来用。

然后执行下面这行代码，开始干活：

```python
await startup(idea="开发一个刷题程序")
```

然后就会输出下面的内容：

```
2024-04-18 15:23:48.546 | INFO     | metagpt.team:invest:90 - Investment: $3.0.
2024-04-18 15:23:48.556 | INFO     | metagpt.roles.role:_act:391 - Alice(Product Manager): to do PrepareDocuments(PrepareDocuments)
2024-04-18 15:23:48.950 | INFO     | metagpt.utils.file_repository:save:57 - save to: E:\JupyterFiles\funcs\tutorial\metaGPT\workspace\20240418152348\docs\requirement.txt
2024-04-18 15:23:48.959 | INFO     | metagpt.roles.role:_act:391 - Alice(Product Manager): to do WritePRD(WritePRD)
2024-04-18 15:23:48.964 | INFO     | metagpt.actions.write_prd:run:86 - New requirement detected: 开发一个刷题程序

[CONTENT]
{
    "Language": "zh_cn",
    "Programming Language": "Python",
    "Original Requirements": "开发一个刷题程序",
    "Project Name": "practice_question_program",
    "Product Goals": [
        "满足用户刷题需求",
        "提供高质量的题目内容",
        "界面友好，操作简便"
    ],
    "User Stories": [
        "作为一个用户，我希望能够按照不同类别刷题",
        "作为一个用户，我想要实时查看我的答题进度和正确率",
        "作为一个用户，我想要在答错题目后看到正确答案和解题思路",
        "作为一个用户，我想要一个简洁美观的界面",
        "作为一个用户，我想要程序支持移动端操作"
    ],
    "Competitive Analysis": [
        "刷题平台A：题目种类丰富，但界面复杂",
        "刷题平台B：界面简洁，但题目更新不够及时",
        "刷题平台C：题目更新快，但用户交互体验较差"
    ],
    "Competitive Quadrant Chart": "quadrantChart\n    title \"刷题平台的用户覆盖与活跃度\"\n    x-axis \"低覆盖\" --> \"高覆盖\"\n    y-axis \"低活跃度\" --> \"高活跃度\"\n    quadrant-1 \"市场拓展潜力\"\n    quadrant-2 \"需提升用户活跃\"\n    quadrant-3 \"需重新评估\"\n    quadrant-4 \"可优化改进\"\n    \"平台A\": [0.4, 0.7]\n    \"平台B\": [0.6, 0.4]\n    \"平台C\": [0.3, 0.5]\n    \"我们的目标产品\": [0.5, 0.6]",
    "Requirement Analysis": "用户需要一个能够随时随地进行题目练习，并且能够获得及时反馈和解答的平台。",
    "Requirement Pool": [
        [
            "P0",
            "题目分类和筛选功能"
        ],
        [
            "P0",
            "实时答题统计和反馈"
        ],
        [
            "P1",
            "正确答案及解题思路展示"
        ],
        [
            "P1",
            "移动端适配"
        ],
        [
            "P2",
            "用户界面美化"
        ]
    ],
    "UI Design draft": "提供清晰的题目展示，简单的导航栏，以及直观的进度统计。",
    "Anything UNCLEAR": "目前没有不清楚的地方。"
}
[/CONTENT]
```

最终在workspace文件夹下生成了一个flask网站程序，前后端都有。
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/db0eba94070e4956bc0cb0ed6d427966.png)
