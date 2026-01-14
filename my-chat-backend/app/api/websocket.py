from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import ConnectionManager
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
import asyncio
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json

# C#의 public class WSMessage와 매칭됨
class WSMessage(BaseModel):
    type: str
    chatId: int
    payload: str
router = APIRouter()

llm_instance = LLMService()

WINDOWS_IP = "192.168.0.181"

rag_instance = RAGService(WINDOWS_IP)

webSocketManager = ConnectionManager()

gpuSemaphore = asyncio.Semaphore(2) # Maximum User 

PROMPT_DATABASE = {
    1:  "당신은 규정 전문가입니다. 아래 제공된 [문맥]을 바탕으로 답변하십시오.\n"
        "반드시 답변 끝에 '참조 문서' 섹션을 만들어 사용한 문서의 이름과 페이지를 명시하세요.\n\n"
        "### 답변 규칙:\n"
        "1. 질문과 관련된 조항(예: 제10조)이 문맥에 조금이라도 언급된다면 그 내용을 바탕으로 상세히 설명해.\n"
        "2. 여러 문서에 내용이 흩어져 있다면 이를 종합해서 대답해.\n"
        "3. 문서 번호나 조항 제목(【 】)이 보이면 반드시 언급해줘.\n"
        "4. 만약 정말로 내용이 없다면, 관련된 유사한 조항이라도 찾아서 안내해줘.\n\n"
        "5. 답변 본문에서도 가능하면 '[문서명, p.00]' 형태로 출처를 언급하세요.\n",
        
    2:  "당신은 규정 전문가입니다. 아래 제공된 [문맥]을 바탕으로 답변하십시오.\n"
        "반드시 답변 끝에 '참조 문서' 섹션을 만들어 사용한 문서의 이름과 페이지를 명시하세요.\n\n"
        "### 답변 규칙:\n"
        "1. **유사 정보 검색**: 질문에 정확히 일치하는 규정이 없더라도, 질문의 키워드와 관련된 가장 근접한 규정이나 유사한 사례를 찾아 안내하십시오.\n"
        "2. **논리적 유추**: 직접적인 언급이 없다면 ""규정상 명시되어 있지 않으나, [관련 규정]의 취지로 보아 다음과 같이 해석될 여지가 있습니다""라고 답변하십시오.\n"
        "3. **구조화**: 답변은 [요약] - [상세 내용] - [근거 조항] 순서로 작성하십시오.\n"
        "4. **출처 명시**: 답변 끝에 반드시 참고한 문서명과 페이지를 나열하십시오.\n"
        "5. **문의처 안내**: 해결이 어려운 경우 ""더 자세한 확인을 위해 [인사/총무]팀에 문의하십시오""라는 문구로 마무리하십시오.\n",
        
    3:  "당신은 규정 전문가입니다. 아래 제공된 [문맥]을 바탕으로 답변하십시오.\n"
        "### 답변 규칙:\n"
        "반드시 답변 끝에 '참조 문서' 섹션을 만들어 사용한 문서의 이름과 페이지를 명시하세요.\n\n"
        "1. **종합 분석**: 질문과 관련된 내용이 여러 문서에 걸쳐 있다면, 이를 하나로 합쳐서 일관성 있게 설명하십시오."
        "2. **조건과 예외**: 답변 시 반드시 '지원 대상', '지급 기준', '예외 사항'을 구분하여 불렛 포인트(•)로 일목요연하게 정리하십시오."
        "3. **최신성 우선**: 문서 간에 내용이 다를 경우, 최신 날짜가 포함된 문서의 규정을 우선하여 답변하십시오."
        "4. **직관적 가이드**: 절차를 묻는 질문에는 1단계, 2단계와 같이 순서를 매겨 답변하십시오."
        "5. **정보 부재 시**: 관련 내용이 전혀 없을 경우에만 ""현재 데이터베이스 내에서는 확인되지 않습니다""라고 답하고, 대신 관련 있을 법한 부서명을 추천하십시오."

}


pdf_files = [
    "private_data/jobrules.pdf",
    "private_data/위임전결권한규정_2024.03.04.pdf",
    "private_data/법인카드관리규정_제정_202403.04.pdf",
    "private_data/경조금지급규칙(2025년_1월_개정).pdf",
    "private_data/국내여비규정(2021.01월_개정).pdf",
    "private_data/개정취업규정_2024년_4월_개정.pdf",
    "private_data/급여규정(2019년_5월_개정).pdf",
    "private_data/승진규정_20200501_제정.pdf",
    "private_data/직제규정(일반직_2019년_5월 제정).pdf",
    "private_data/근로기준법(법률)(제20520호)(20251023).pdf",
]
print("read data..")
rag_instance.ingest_multiple_pdfs(pdf_files)
print("read finished")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
#    await websocket.accept()
    await webSocketManager.connect(websocket)

    # pdf_files = [
    #     "private_data/jobrules.pdf",
    #     "private_data/위임전결권한규정_2024.03.04.pdf",
    #     "private_data/법인카드관리규정_제정_202403.04.pdf",
    #     "private_data/경조금지급규칙(2025년_1월_개정).pdf",
    #     "private_data/국내여비규정(2021.01월_개정).pdf",
    #     "private_data/개정취업규정_2024년_4월_개정.pdf",
    #     "private_data/급여규정(2019년_5월_개정).pdf",
    #     "private_data/승진규정_20200501_제정.pdf",
    #     "private_data/직제규정(일반직_2019년_5월 제정).pdf",
    # ]
    # print("read data..")
    # rag_instance.ingest_multiple_pdfs(pdf_files)
    # print("read finished")

    try:
        while True :
            # data = await websocket.receive_text()
            # print(f"Recived Message :{data}")
            try:
                raw_data = await websocket.receive_json()
                print(raw_data)
            except json.JSONDecodeError:
                print(f"JSON 형식이 아닙니다. {raw_data}")
                continue
                
            try: 
                message = WSMessage(**raw_data)

            except Exception as e :
                print("Data Fail")
                continue

            if message.type == "SET_PROMPT":
                print(f"SET PROMPT: {message.chatId}")
            elif message.type == "SEND_MESSAGE":
                print(f"Recived Message : {message.payload}")
                systemPrompt = PROMPT_DATABASE.get(message.chatId)
                async with gpuSemaphore:
                # 2. 제너레이터로부터 조각(chunk)을 하나씩 꺼내서 즉시 전송
                    async for chunk in rag_instance.get_rag_response_stream(message.payload, systemPrompt):
                        if chunk:
                            await websocket.send_json({
                                "type" : "AI_RESPONSE",
                                "chatId": message.chatId,
                                "payload": chunk
                        })
                        print(chunk, end="", flush=True) # 서버 로그에서도 실시간 확인 가능
            # 3. 스트리밍 종료 알림
            # await websocket.send_text("[END]")
            # print("\nAI answer transfer finished")

    except WebSocketDisconnect : 
        print("Invaild Data")
        webSocketManager.disconnect(websocket)