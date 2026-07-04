from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class PlayerColor(str, Enum):
    WHITE = "white"
    BLACK = "black"
    SPECTATOR = "spectator"

class MessageType(str, Enum):
    JOIN = "join"
    PLAYER_JOINED = "player_joined"
    SUBMIT_MOVE = "submit_move"
    MOVE_SUBMITTED = "move_submitted"
    TIMER_TICK = "timer_tick"
    TURN_RESOLVED = "turn_resolved"
    GAME_OVER = "game_over"
    ERROR = "error"
    GAME_STATE = "game_state"
    RESIGN = "resign"
    RESTART = "restart"

class WSMessage(BaseModel):
    type: MessageType
    data: Dict[str, Any]

class JoinData(BaseModel):
    room_id: str
    color: Optional[PlayerColor] = None
    player_name: str = "Anônimo"

class SubmitMoveData(BaseModel):
    uci: str  # ex: "e2e4", "g1f3"

class TurnResolvedData(BaseModel):
    fen: str
    white_move_uci: Optional[str]
    black_move_uci: Optional[str]
    events: List[str]  # Lista de eventos (ex: "💥 Colisão em d5!", "Rei capturado!")
    game_over: bool
    winner: Optional[str]
    reason: Optional[str]
