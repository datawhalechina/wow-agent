简历信息提取是企业中经常遇到的场景，我们这一课仅用OpenAI来实现这一功能。


```python
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
# 从环境变量中读取api_key
api_key = os.getenv('ZISHU_API_KEY')
base_url = "http://101.132.164.17:8000/v1"
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
def get_completion(prompt):
    response = client.chat.completions.create(
        model=chat_model,  # 填写需要调用的模型名称
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



我们接下来实现一个简历信息提取智能体，只依赖openai库。

```python
from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, EmailStr, model_validator

# 定义这个pydantic模型是关键的关键
class Resume(BaseModel):
    name: Optional[str] = Field(None, description="求职者姓名，如果没找到就置为空字符串")
    city: Optional[str] = Field(None, description="求职者居住地，如果没找到就置为空字符串")
    birthday: Optional[str] = Field(None, description="求职者生日，如果没找到就置为空字符串")
    phone: Optional[str] = Field(None, description="求职者手机号，如果没找到就置为空字符串")
    email: Optional[str] = Field(None, description="求职者邮箱，如果没找到就置为空字符串")
    education: Optional[List[str]] = Field(None, description="求职者教育背景")
    experience: Optional[List[str]] = Field(None, description="求职者工作或实习经历，如果没找到就置为空字符串")
    project: Optional[List[str]] = Field(None, description="求职者项目经历，如果没找到就置为空字符串")
    certificates: Optional[List[str]] = Field(None, description="求职者资格证书，如果没找到就置为空字符串")

    @field_validator("birthday", mode="before")
    def validate_and_convert_date(cls, raw_date):
        if raw_date is None:
            return None
        if isinstance(raw_date, str):
            # List of acceptable date formats
            date_formats = ['%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%m-%d-%Y']
            for fmt in date_formats:
                try:
                    # Attempt to parse the date string with the current format
                    parsed_date = datetime.strptime(raw_date, fmt).date()
                    # Return the date in MM-DD-YYYY format as a string
                    return parsed_date.strftime('%m-%d-%Y')
                except ValueError:
                    continue  # Try the next format
            # If none of the formats match, raise an error
            raise ValueError(
                f"Invalid date format for 'consultation_date'. Expected one of: {', '.join(date_formats)}."
            )
        if isinstance(raw_date, date):
            # Convert date object to MM-DD-YYYY format
            return raw_date.strftime('%m-%d-%Y')

        raise ValueError(
            "Invalid type for 'consultation_date'. Must be a string or a date object."
        )


class ResumeOpenAI:
    def __init__(self):
        self.resume_profile = Resume()
        self.output_schema = self.resume_profile.model_json_schema()
        self.template = """
        You are an expert in analyzing resumes. Use the following JSON schema to extract relevant information:
        ```json
        {output_schema}
        ```json
        Extract the information from the following document and provide a structured JSON response strictly adhering to the schema above. 
        Please remove any ```json ``` characters from the output. Do not make up any information. If a field cannot be extracted, mark it as `n/a`.
        Document:
        ----------------
        {resume_content}
        ----------------
        """

    def create_prompt(self, output_schema, resume_content):
        return self.template.format(
            output_schema=output_schema,
            resume_content=resume_content
        )

    def run(self, resume_content):
        try:
            response = client.chat.completions.create(
                model=chat_model,
                # 不是所有模型都支持response_format，要看一下调用的模型是否支持这个参数
                # 千问、智谱的模型一般支持
                response_format={ "type": "json_object" },
                messages=[
                    {"role": "system", "content": "你是一位专业的简历信息提取专家。"},
                    {"role": "user", "content": self.create_prompt(self.output_schema, resume_content)}
                ],
            )

            result = response.choices[0].message.content
        except Exception as e:
            print(f"Error occurred: {e}")

        return result

resume_openai = ResumeOpenAI()
```

我们可以用一个示例来测试一下：

已知有一个简历文本，这个文本可以是经过简历文件转成图片再OCR识别后的一堆非结构化文本。

```python
# 示例输入数据
input_data = """
59a488639e2f882c1nR_2NS6EFJXwZG-UPKaR-WhnPQ~
杜素宁
MOBILE : 15904130130
E-MAIL：0da08x@163.com
Address:云南省昭通市
个人信息
民族：汉 籍贯：云南省昭通市 性别：女 年龄: 22
教育经历
2008.08-2012.08 北方工业大学 食品科学与工程 学士学位
主要经历
Project Experience
工作经历：
1997.06-2010.07 江苏华英企业管理股份有限公司 水处理工程师
工作内容:
1.负责部门内日常用品的采购；2.做好与公司内其他部门的对接工作；3.协助部门进行办公环境管理和后勤管理工作；4.销
售人员与公司的信息交流，随时保持与市场销售人员的电话沟通，销售政策及公司文件的及时传达。5.领导交办的其他工作
工作经历：
1991年12月-2012年 和宇健康科技股份有限公司 市场营销专员
09月
工作内容:
1、做好消费宾客的迎、送接待工作，接受宾客各种渠道的预定并加以落实；2、礼貌用语，详细做好预订记录；3、了解和
收集宾客的建议和意见并及时反馈给上级领导；4、以规范的服务礼节，树立公司品牌优质，文雅的服务形象。
工作经历：
2007/05-2010/03 深圳市有棵树科技有限公司 拼多多运营
工作内容:
1.负责规定区域的产品销售，做好产品介绍，确认订单，回款等销售相关工作；2.做好客户背景资料调查，竞争对手分析，
产品适用性分析；3.按公司规定完成SalesPipeline信息记录
"""
```

我们现在来运行一下这个示例简历

```python
# 运行智能体
rec_data = resume_openai.run(input_data)
print(rec_data)
```

下面是大模型给出的简历提取结果：

{
  "name": "杜素宁",
  "city": "云南省昭通市",
  "birthday": "22岁",
  "phone": "15904130130",
  "email": "0da08x@163.com",
  "education": [
    "2008.08-2012.08 北方工业大学 食品科学与工程 学士学位"
  ],
  "experience": [
    "1997.06-2010.07 江苏华英企业管理股份有限公司 水处理工程师",
    "工作内容: 负责部门内日常用品的采购；做好与公司内其他部门的对接工作；协助部门进行办公环境管理和后勤管理工作；销售人员与公司的信息交流，随时保持与市场销售人员的电话沟通，销售政策及公司文件的及时传达。领导交办的其他工作",
    "1991年12月-2007.04 和宇健康科技股份有限公司 市场营销专员",
    "工作内容: 做好消费宾客的迎、送接待工作，接受宾客各种渠道的预定并加以落实；礼貌用语，详细做好预订记录；了解和收集宾客的建议和意见并及时反馈给上级领导；以规范的服务礼节，树立公司品牌优质，文雅的服务形象。",
    "2007/05-2010/03 深圳市有棵树科技有限公司 拼多多运营",
    "工作内容: 负责规定区域的产品销售，做好产品介绍，确认订单，回款等销售相关工作；做好客户背景资料调查，竞争对手分析，产品适用性分析；按公司规定完成SalesPipeline信息记录"
  ],
  "project": "n/a",
  "certificates": "n/a"
}