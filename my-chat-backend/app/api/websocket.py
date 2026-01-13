from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService

router = APIRouter()

llm_instance = LLMService()

WINDOWS_IP = "192.168.0.154"

rag_instance = RAGService(WINDOWS_IP)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    pdf_files = [
        "data/jobrules.pdf",
        "data/위임전결권한규정_2024.03.04.pdf",
        "data/법인카드관리규정_제정_202403.04.pdf",
        "data/경조금지급규칙(2025년_1월_개정).pdf",
        "data/국내여비규정(2021.01월_개정).pdf",
        "data/개정취업규정_2024년_4월_개정.pdf",
        "data/급여규정(2019년_5월_개정).pdf",
        "data/승진규정_20200501_제정.pdf",
        "data/직제규정(일반직_2019년_5월 제정).pdf",
    ]
    print("read data..")
    rag_instance.ingest_multiple_pdfs(pdf_files)
    print("read finished")

    try:
        while True :
            data = await websocket.receive_text()
            print(f"Recived Message :{data}")

            # ai_reply = await llm_instance.get_ai_response(data)
            ai_reply = await rag_instance.get_rag_response(data)

            await websocket.send_text(ai_reply)
            print(f" AI answer transfer finished")

    except WebSocketDisconnect : 
        print ("Client disonnected")
