from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

class LLMService:
    def __init__(self):
        self.windows_ip = "192.168.0.154"
        self.model = OllamaLLM(
            model="gemma3:12b",
            base_url=f"http://{self.windows_ip}:11434",
            num_ctx=16384
        )

        # 1. 한국어 페르소나 설정
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "너는 유능하고 친절한 한국어 AI 비서야. 모든 답변은 반드시 한국어로 작성해줘."),
            ("user", "{input}")
        ])

        self.chain = self.prompt_template | self.model

    async def get_ai_response(self, user_message: str): 
        try:
            response = await self.chain.ainvoke({"input": user_message })
            return response
        except Exception as e:
            return f"LLM Connection Error Occur : {str(e)}"