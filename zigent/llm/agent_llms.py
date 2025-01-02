import requests
class LLM():
    def __init__(self):
        pass
    def run(self, prompt: str):
        url = f'http://43.200.7.56:8008/stream_chat?param={prompt}' 
        response = requests.get(url)
        return response.text
