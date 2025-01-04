from openai import OpenAI
from typing import Any
from pydantic import Field
api_key = ""
base_url = "http://43.200.7.56:8008/v1"
model_name = "glm-4-flash"

class LLM():
    api_key: str = Field(default=api_key)
    base_url: str = Field(default=base_url)
    model_name: str = Field(default=model_name)
    client: OpenAI = Field(default=None, exclude=True)
    def __init__(self, api_key: str = api_key, base_url: str = base_url, model_name: str = model_name, **data: Any):
        super().__init__(**data)
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
    def run(self, prompt: str):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
