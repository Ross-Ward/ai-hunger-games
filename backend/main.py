from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .game_engine import GameEngine
import asyncio
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

game_engine = GameEngine()

@app.get("/")
def read_root():
    return {"message": "AI Hunger Games Backend Online", "status": "Ready"}

@app.post("/spawn")
def spawn_agents(count: int = 5):
    game_engine.spawn_agents(count)
    return {"message": f"Spawned {count} agents", "agents": [a.to_dict() for a in game_engine.agents]}

@app.post("/start_round")
async def start_round_endpoint(question: str):
    result = await game_engine.start_round(question)
    return result

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "start_round":
                question = message.get("question")
                if question:
                    # Run the round logic
                    result = await game_engine.start_round(question)
                    # Send updates back
                    await websocket.send_json({
                        "type": "round_update",
                        "data": result,
                        "logs": game_engine.logs[-10:] # Send last 10 logs
                    })
            elif message.get("action") == "get_state":
                 await websocket.send_json({
                        "type": "state_update",
                        "agents": [a.to_dict() for a in game_engine.agents],
                        "logs": game_engine.logs[-20:]
                    })

    except WebSocketDisconnect:
        print("Client disconnected")
