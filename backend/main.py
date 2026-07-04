import asyncio
from typing import Dict, Set, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.models import PlayerColor, MessageType, WSMessage
from backend.game import SimultaneousChessGame
import os

app = FastAPI(title="Xadrez Quântico e Simultâneo")

# Montar pasta estática do frontend se existir
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
async def get_index():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Bem-vindo ao Xadrez Quântico e Simultâneo API. Acesse /static/index.html"}

class RoomManager:
    def __init__(self):
        self.games: Dict[str, SimultaneousChessGame] = {}
        self.connections: Dict[str, Dict[WebSocket, PlayerColor]] = {}
        self.timer_tasks: Dict[str, asyncio.Task] = {}

    def get_or_create_game(self, room_id: str) -> SimultaneousChessGame:
        if room_id not in self.games:
            self.games[room_id] = SimultaneousChessGame(room_id=room_id, turn_duration_seconds=20)
            self.connections[room_id] = {}
            # Iniciar task de cronômetro da sala
            self.timer_tasks[room_id] = asyncio.create_task(self.room_loop(room_id))
        return self.games[room_id]

    async def connect(self, room_id: str, websocket: WebSocket, color_str: str):
        await websocket.accept()
        game = self.get_or_create_game(room_id)
        
        try:
            color = PlayerColor(color_str.lower())
        except ValueError:
            color = PlayerColor.SPECTATOR

        self.connections[room_id][websocket] = color

        # Enviar estado inicial para o jogador que acabou de conectar
        await websocket.send_json({
            "type": MessageType.GAME_STATE,
            "data": game.get_state()
        })

        # Avisar outros que alguém entrou
        await self.broadcast(room_id, {
            "type": MessageType.PLAYER_JOINED,
            "data": {"color": color.value, "message": f"Jogador ({color.value}) entrou na sala."}
        })

    def disconnect(self, room_id: str, websocket: WebSocket):
        if room_id in self.connections:
            if websocket in self.connections[room_id]:
                del self.connections[room_id][websocket]

    async def broadcast(self, room_id: str, message: dict):
        if room_id not in self.connections:
            return
        dead_sockets = []
        for ws in self.connections[room_id].keys():
            try:
                await ws.send_json(message)
            except Exception:
                dead_sockets.append(ws)
        for ws in dead_sockets:
            self.disconnect(room_id, ws)

    async def room_loop(self, room_id: str):
        """
        Loop principal da sala que controla o tempo e dispara a resolução se ambos jogarem
        ou o tempo acabar.
        """
        while room_id in self.games:
            game = self.games[room_id]
            if game.game_over:
                await asyncio.sleep(1)
                continue

            await asyncio.sleep(1)
            game.timer_seconds -= 1

            # Transmitir tick do cronômetro
            await self.broadcast(room_id, {
                "type": MessageType.TIMER_TICK,
                "data": {
                    "timer_seconds": game.timer_seconds,
                    "white_ready": game.white_ready,
                    "black_ready": game.black_ready
                }
            })

            # Verificar condição de resolução (tempo zerou OU ambos submeteram)
            if game.timer_seconds <= 0 or (game.white_ready and game.black_ready):
                result = game.resolve_turn()
                await self.broadcast(room_id, {
                    "type": MessageType.TURN_RESOLVED,
                    "data": result
                })
                if game.game_over:
                    await self.broadcast(room_id, {
                        "type": MessageType.GAME_OVER,
                        "data": {
                            "winner": game.winner,
                            "reason": game.reason
                        }
                    })

manager = RoomManager()

@app.websocket("/ws/game/{room_id}/{color}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, color: str):
    await manager.connect(room_id, websocket, color)
    game = manager.get_or_create_game(room_id)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            msg_data = data.get("data", {})

            if msg_type == MessageType.SUBMIT_MOVE:
                uci = msg_data.get("uci")
                color_enum = manager.connections[room_id].get(websocket, PlayerColor.SPECTATOR)
                
                if color_enum == PlayerColor.SPECTATOR:
                    await websocket.send_json({
                        "type": MessageType.ERROR,
                        "data": {"message": "Espectadores não podem submeter jogadas."}
                    })
                    continue

                is_white = (color_enum == PlayerColor.WHITE)
                success, reason = game.submit_move(uci, is_white)
                
                if success:
                    # Avisar apenas que o jogador submeteu (sem vazar a jogada!)
                    await manager.broadcast(room_id, {
                        "type": MessageType.MOVE_SUBMITTED,
                        "data": {
                            "color": color_enum.value,
                            "white_ready": game.white_ready,
                            "black_ready": game.black_ready
                        }
                    })
                    # Se após submeter ambos estão prontos, o loop do cronômetro ou a checagem imediata resolve
                    if game.white_ready and game.black_ready:
                        result = game.resolve_turn()
                        await manager.broadcast(room_id, {
                            "type": MessageType.TURN_RESOLVED,
                            "data": result
                        })
                        if game.game_over:
                            await manager.broadcast(room_id, {
                                "type": MessageType.GAME_OVER,
                                "data": {
                                    "winner": game.winner,
                                    "reason": game.reason
                                }
                            })
                else:
                    await websocket.send_json({
                        "type": MessageType.ERROR,
                        "data": {"message": reason}
                    })
    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)
