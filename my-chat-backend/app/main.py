from fastapi import FastAPI
from app.api import websocket # get websocket router

app = FastAPI(title="My AI Chat Backend")

app.include_router(websocket.router)

#if Program recived HTTP "GET" Request Excute Root Function
@app.get("/")
async def root():
    return {"message" : "AI Chat Backend Server is Running!"}