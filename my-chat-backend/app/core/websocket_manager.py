from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, webSocket: WebSocket):
        await webSocket.accept()
        self.active_connections.append(webSocket)
        print(f"New Connection : {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"disconnect. remain connection : {len(self.active_connections)}")
    
