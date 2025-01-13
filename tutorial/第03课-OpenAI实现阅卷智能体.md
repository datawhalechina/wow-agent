在各种考试中，选择题、判断题、填空题很好阅卷，只需要对比答案和作答是否完全一致即可。但是对于简答题的阅卷，就没这么简单了，通常需要对比意思是否真正答出来了，这通常需要人去阅读考生的作答。现在有了大模型，我们可以让大模型帮助我们给简答题阅卷并生成评价。


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
构造client只需要两个东西：api_key和base_url。本教程用的是自塾提供的大模型API服务，在.env文件中已经有了api_key。这个只作为教学用。如果是在生产环境中，还是建议去使用例如智谱、零一万物、月之暗面、deepseek等大厂的大模型API服务。只要有api_key、base_url、chat_model三个东西即可。

```python
from openai import OpenAI
client = OpenAI(
    api_key = api_key,
    base_url = base_url
)
```

有了这个client，我们就可以去实现各种能力了。

```python
import json
import re


def extract_json_content(text):
    # 这个函数的目标是提取大模型输出内容中的json部分，并对json中的换行符、首位空白符进行删除
    text = text.replace("\n","")
    pattern = r"```json(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        return matches[0].strip()
    return text

class JsonOutputParser:
    def parse(self, result):
        # 这个函数的目标是把json字符串解析成python对象
        # 其实这里写的这个函数性能很差，经常解析失败，有很大的优化空间
        try:
            result = extract_json_content(result)
            parsed_result = json.loads(result)
            return parsed_result
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid json output: {result}") from e

class GradingOpenAI:
    def __init__(self):
        self.model = "glm-4-flash"
        self.output_parser = JsonOutputParser()
        self.template = """你是一位中国专利代理师考试阅卷专家，
擅长根据给定的题目和答案为考生生成符合要求的评分和中文评语，
并按照特定的格式输出。
你的任务是，根据我输入的考题和答案，针对考生的作答生成评分和中文的评语，并以JSON格式返回。
阅卷标准适当宽松一些，只要考生回答出基本的意思就应当给分。
答案如果有数字标注，含义是考生如果答出这个知识点，这道题就会得到几分。
生成的中文评语需要能够被json.loads()这个函数正确解析。
生成的整个中文评语需要用英文的双引号包裹，在被包裹的字符串内部，请用中文的双引号。
中文评语中不可以出现换行符、转义字符等等。

输出格式为JSON:
{{
  "llmgetscore": 0,
  "llmcomments": "中文评语"
}}

比较学生的回答与正确答案，
并给出满分为10分的评分和中文评语。 
题目：{ques_title} 
答案：{answer} 
学生的回复：{reply}"""

    def create_prompt(self, ques_title, answer, reply):
        return self.template.format(
            ques_title=ques_title,
            answer=answer,
            reply=reply
        )

    def grade_answer(self, ques_title, answer, reply):
        success = False
        while not success:
            # 这里是一个不得已的权宜之计
            # 上面的json解析函数不是表现很差吗，那就多生成几遍，直到解析成功
            # 对大模型生成的内容先解析一下，如果解析失败，就再让大模型生成一遍
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一位专业的考试阅卷专家。"},
                        {"role": "user", "content": self.create_prompt(ques_title, answer, reply)}
                    ],
                    temperature=0.7
                )

                result = self.output_parser.parse(response.choices[0].message.content)
                success = True
            except Exception as e:
                print(f"Error occurred: {e}")
                continue

        return result['llmgetscore'], result['llmcomments']

    def run(self, input_data):
        output = []
        for item in input_data:
            score, comment = self.grade_answer(
                item['ques_title'], 
                item['answer'], 
                item['reply']
            )
            item['llmgetscore'] = score
            item['llmcomments'] = comment
            output.append(item)
        return output
grading_openai = GradingOpenAI()
```

我们可以用一个示例来测试一下：

已知有两个简答题，有题目、答案、分值和考生作答。我们需要让大模型生成评分和评价。

```python
# 示例输入数据
input_data = [
 {'ques_title': '请解释共有技术特征、区别技术特征、附加技术特征、必要技术特征的含义',
  'answer': '共有技术特征：与最接近的现有技术共有的技术特征（2.5分）； 区别技术特征：区别于最接近的现有技术的技术特征（2.5分）； 附加技术特征：对所引用的技术特征进一步限定的技术特征，增加的技术特征（2.5分）； 必要技术特征：为解决其技术问题所不可缺少的技术特征（2.5分）。',
  'fullscore': 10,
  'reply': '共有技术特征：与所对比的技术方案相同的技术特征\n区别技术特征：与所对比的技术方案相区别的技术特征\n附加技术特征：对引用的技术特征进一步限定的技术特征\n必要技术特征：解决技术问题必须可少的技术特征'},
 {'ques_title': '请解释前序部分、特征部分、引用部分、限定部分',
  'answer': '前序部分：独权中，主题+与最接近的现有技术共有的技术特征，在其特征在于之前（2.5分）； 特征部分：独权中，与区别于最接近的现有技术的技术特征，在其特征在于之后（2.5分）；引用部分：从权中引用的权利要求编号及主题 （2.5分）；限定部分：从权中附加技术特征（2.5分）。',
  'fullscore': 10,
  'reply': '前序部分：独立权利要求中与现有技术相同的技术特征\n特征部分：独立权利要求中区别于现有技术的技术特征\n引用部分：从属权利要求中引用其他权利要求的部分\n限定部分：对所引用的权利要求进一步限定的技术特征'}]
  ```

  这个示例是根据中国专利法出的两个考题。我们让大模型来阅卷。

  ```python
  # 运行智能体
graded_data = grading_openai.run(input_data)
print(graded_data)
```

下面是大模型给出的阅卷结果：

[{'ques_title': '请解释共有技术特征、区别技术特征、附加技术特征、必要技术特征的含义',
  'answer': '共有技术特征：与最接近的现有技术共有的技术特征（2.5分）； 区别技术特征：区别于最接近的现有技术的技术特征（2.5分）； 附加技术特征：对所引用的技术特征进一步限定的技术特征，增加的技术特征（2.5分）； 必要技术特征：为解决其技术问题所不可缺少的技术特征（2.5分）。',
  'fullscore': 10,
  'reply': '共有技术特征：与所对比的技术方案相同的技术特征\n区别技术特征：与所对比的技术方案相区别的技术特征\n附加技术特征：对引用的技术特征进一步限定的技术特征\n必要技术特征：解决技术问题必须可少的技术特征',
  'llmgetscore': 10,
  'llmcomments': '考生对共有技术特征、区别技术特征、附加技术特征和必要技术特征的解释基本正确，能够准确描述其含义，故给予满分10分。'},
 {'ques_title': '请解释前序部分、特征部分、引用部分、限定部分',
  'answer': '前序部分：独权中，主题+与最接近的现有技术共有的技术特征，在其特征在于之前（2.5分）； 特征部分：独权中，与区别于最接近的现有技术的技术特征，在其特征在于之后（2.5分）；引用部分：从权中引用的权利要求编号及主题 （2.5分）；限定部分：从权中附加技术特征（2.5分）。',
  'fullscore': 10,
  'reply': '前序部分：独立权利要求中与现有技术相同的技术特征\n特征部分：独立权利要求中区别于现有技术的技术特征\n引用部分：从属权利要求中引用其他权利要求的部分\n限定部分：对所引用的权利要求进一步限定的技术特征',
  'llmgetscore': 8,
  'llmcomments': '回答基本正确，对前序部分和特征部分的理解较为准确，但对引用部分和限定部分的理解略有偏差。前序部分应包含与现有技术共有的技术特征，特征部分应包含区别于现有技术的技术特征。引用部分和限定部分的解释需要更加精确。'}]