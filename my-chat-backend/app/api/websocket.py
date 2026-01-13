from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import ConnectionManager
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
import asyncio

router = APIRouter()

llm_instance = LLMService()

WINDOWS_IP = "192.168.0.181"

rag_instance = RAGService(WINDOWS_IP)

webSocketManager = ConnectionManager()

gpuSemaphore = asyncio.Semaphore(2) # Maximum User 

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
            data = await websocket.receive_text()
            print(f"Recived Message :{data}")

            # 1. 스트리밍 시작 알림 (프론트엔드 UI 처리용 선택 사항)
            # await websocket.send_text("[START]") 

            print("AI answer streaming started...")
            
            async with gpuSemaphore:
            # 2. 제너레이터로부터 조각(chunk)을 하나씩 꺼내서 즉시 전송
                async for chunk in rag_instance.get_rag_response_stream(data):
                    if chunk:
                        await websocket.send_text(chunk)
                    # print(chunk, end="", flush=True) # 서버 로그에서도 실시간 확인 가능
            # 3. 스트리밍 종료 알림
            # await websocket.send_text("[END]")
            print("\nAI answer transfer finished")

    except WebSocketDisconnect : 
        webSocketManager.disconnect(websocket)