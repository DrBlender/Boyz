from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()

# CORS für Frontend-Zugriff
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections = []
        self.players = {}
        self.current_question = None
        self.buzzer_pressed = None

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.players[websocket] = {"name": username, "score": 0}
        await self.broadcast(f"{username} ist beigetreten!")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            username = self.players.pop(websocket, {}).get("name", "Unbekannt")
            asyncio.create_task(self.broadcast(f"{username} hat das Spiel verlassen."))

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def send_question(self, question: str):
        self.current_question = question
        self.buzzer_pressed = None
        await self.broadcast(f"FRAGE: {question}")

    async def buzzer(self, websocket: WebSocket):
        if not self.buzzer_pressed:
            self.buzzer_pressed = websocket
            await websocket.send_text("Du hast zuerst gedrückt!")
            await self.broadcast(f"{self.players[websocket]['name']} hat den Buzzer gedrückt!")
        else:
            await websocket.send_text("Jemand war schneller!")

manager = ConnectionManager()

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket, username)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "buzzer":
                await manager.buzzer(websocket)
            elif data.startswith("answer:") and websocket == manager.buzzer_pressed:
                answer = data.split(":", 1)[1]
                await manager.broadcast(f"{manager.players[websocket]['name']} hat geantwortet: {answer}")
            elif data == "start_round":
                await manager.send_question("Was passiert als Nächstes?")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
