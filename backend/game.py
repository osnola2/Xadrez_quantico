import chess
from typing import Optional, Tuple, List, Dict, Any
import asyncio

class SimultaneousChessGame:
    def __init__(self, room_id: str, turn_duration_seconds: int = 120):
        self.room_id = room_id
        self.board = chess.Board()
        self.turn_duration = turn_duration_seconds
        self.timer_seconds = turn_duration_seconds
        
        self.white_move_uci: Optional[str] = None
        self.black_move_uci: Optional[str] = None
        
        self.white_ready: bool = False
        self.black_ready: bool = False
        
        self.game_over: bool = False
        self.winner: Optional[str] = None
        self.reason: Optional[str] = None
        self.history: List[Dict[str, Any]] = []
        self.last_moves: Dict[str, str] = {"white": None, "black": None}
        self.round_number: int = 1

    def get_state(self) -> Dict[str, Any]:
        return {
            "room_id": self.room_id,
            "fen": self.board.fen(),
            "timer_seconds": self.timer_seconds,
            "turn_duration": self.turn_duration,
            "white_ready": self.white_ready,
            "black_ready": self.black_ready,
            "game_over": self.game_over,
            "winner": self.winner,
            "reason": self.reason,
            "round_number": self.round_number,
            "history": self.history,
            "last_moves": self.last_moves
        }

    def is_valid_move(self, uci: str, color: bool) -> bool:
        """
        Verifica se um movimento UCI é pseudo-legal para a cor especificada no estado atual.
        No xadrez simultâneo, movimentos pseudo-legais são permitidos (incluindo mover para xeque
        ou capturar o Rei oponente).
        """
        try:
            move = chess.Move.from_uci(uci)
        except ValueError:
            return False

        piece = self.board.piece_at(move.from_square)
        if piece is None or piece.color != color:
            return False

        # Autocompletar promoção de peão para a checagem, caso não venha do frontend
        if piece.piece_type == chess.PAWN:
            if (color == chess.WHITE and chess.square_rank(move.to_square) == 7) or \
               (color == chess.BLACK and chess.square_rank(move.to_square) == 0):
                if move.promotion is None:
                    move = chess.Move(move.from_square, move.to_square, promotion=chess.QUEEN)

        # Para checar pseudo-legalidade, a casa de destino pode mudar (ficar vazia ou ser ocupada por inimigo)
        target_square = move.to_square
        original_target_piece = self.board.piece_at(target_square)
        enemy_color = not color

        # Como cada jogador só faz UMA jogada por turno, peças aliadas NÃO PODEM sair da frente
        # no mesmo turno em que você move outra peça. Logo, fogo amigo é impossível/ilegal.
        if original_target_piece and original_target_piece.color == color:
            return False
        
        old_turn = self.board.turn
        self.board.turn = color

        is_pseudo_legal = False
        
        # Teste 1: Casa de destino VAZIA
        self.board.remove_piece_at(target_square)
        if move in self.board.pseudo_legal_moves:
            is_pseudo_legal = True
            
        # Teste 2: Casa de destino INIMIGA
        if not is_pseudo_legal:
            self.board.set_piece_at(target_square, chess.Piece(chess.QUEEN, enemy_color))
            if move in self.board.pseudo_legal_moves:
                is_pseudo_legal = True

        # Restaura o tabuleiro
        if original_target_piece:
            self.board.set_piece_at(target_square, original_target_piece)
        else:
            self.board.remove_piece_at(target_square)
            
        self.board.turn = old_turn

        return is_pseudo_legal

    def resign(self, is_white: bool):
        self.game_over = True
        self.winner = "black" if is_white else "white"
        resigner = "Brancas" if is_white else "Pretas"
        self.reason = f"O jogador de {resigner} desistiu da partida."
        self.history.append({
            "round": self.round_number,
            "events": [f"🏳️ {resigner} desistiram da partida!"],
            "fen_after": self.board.fen()
        })

    def reset(self):
        self.board.reset()
        self.timer_seconds = self.turn_duration
        self.white_move_uci = None
        self.black_move_uci = None
        self.white_ready = False
        self.black_ready = False
        self.game_over = False
        self.winner = None
        self.reason = None
        self.history = []
        self.last_moves = {"white": None, "black": None}
        self.round_number = 1

    def submit_move(self, uci: str, color: bool) -> Tuple[bool, str]:
        if self.game_over:
            return False, "O jogo já terminou."

        if not self.is_valid_move(uci, color):
            return False, "Movimento inválido para esta peça no tabuleiro atual."

        if color == chess.WHITE:
            self.white_move_uci = uci
            self.white_ready = True
        else:
            self.black_move_uci = uci
            self.black_ready = True

        return True, "Jogada submetida com sucesso."

    def check_kings_alive(self) -> Tuple[bool, bool]:
        white_king = bool(self.board.pieces(chess.KING, chess.WHITE))
        black_king = bool(self.board.pieces(chess.KING, chess.BLACK))
        return white_king, black_king

    def get_san_safe(self, move: chess.Move, color: bool) -> str:
        if not move:
            return ""
        old_turn = self.board.turn
        self.board.turn = color
        try:
            san = self.board.san(move)
        except Exception:
            piece = self.board.piece_at(move.from_square)
            if piece:
                p_sym = "" if piece.piece_type == chess.PAWN else piece.symbol().upper()
                san = f"{p_sym}{chess.square_name(move.from_square)}-{chess.square_name(move.to_square)}"
            else:
                san = move.uci()
        self.board.turn = old_turn
        return san

    def resolve_turn(self) -> Dict[str, Any]:
        """
        Executa a resolução simultânea do turno com base no algoritmo aprovado:
        1. Remove as peças em movimento de suas origens (tratando Esquivas e Cruzamentos).
        2. Aplica colisões na mesma casa (Cenário A: Aniquilação Mútua).
        3. Pousa as peças em destinos diferentes (capturando peças paradas se houver).
        4. Verifica promoção de peões e captura de Reis.
        """
        events: List[str] = []
        w_uci = self.white_move_uci
        b_uci = self.black_move_uci

        w_move = chess.Move.from_uci(w_uci) if w_uci else None
        b_move = chess.Move.from_uci(b_uci) if b_uci else None

        w_san = self.get_san_safe(w_move, chess.WHITE) if w_move else ""
        b_san = self.get_san_safe(b_move, chess.BLACK) if b_move else ""

        w_piece = self.board.piece_at(w_move.from_square) if w_move else None
        b_piece = self.board.piece_at(b_move.from_square) if b_move else None

        # Passo 1: Salvar últimos movimentos
        self.last_moves = {
            "white": w_uci if w_uci else None,
            "black": b_uci if b_uci else None,
            "white_san": w_san,
            "black_san": b_san
        }

        # Passo 2: Remover peças em movimento de suas origens
        if w_move and w_piece:
            self.board.remove_piece_at(w_move.from_square)
        if b_move and b_piece:
            self.board.remove_piece_at(b_move.from_square)

        # Passo 2 & 3: Resolver destinos
        if w_move and b_move and w_move.to_square == b_move.to_square and w_piece and b_piece:
            w_is_pawn = (w_piece.piece_type == chess.PAWN)
            b_is_pawn = (b_piece.piece_type == chess.PAWN)
            
            w_is_diagonal = w_is_pawn and (chess.square_file(w_move.from_square) != chess.square_file(w_move.to_square))
            w_is_vertical = w_is_pawn and (chess.square_file(w_move.from_square) == chess.square_file(w_move.to_square))
            
            b_is_diagonal = b_is_pawn and (chess.square_file(b_move.from_square) != chess.square_file(b_move.to_square))
            b_is_vertical = b_is_pawn and (chess.square_file(b_move.from_square) == chess.square_file(b_move.to_square))

            if w_is_diagonal and b_is_vertical:
                events.append(f"⚔️ Emboscada! O Peão branco atacou na diagonal e capturou o Peão preto que avançava para {chess.square_name(w_move.to_square)}!")
                if chess.square_rank(w_move.to_square) == 7:
                    prom_type = w_move.promotion if w_move.promotion else chess.QUEEN
                    w_piece = chess.Piece(prom_type, chess.WHITE)
                    events.append(f"👑 Peão branco promovido em {chess.square_name(w_move.to_square)}!")
                self.board.set_piece_at(w_move.to_square, w_piece)
                
            elif b_is_diagonal and w_is_vertical:
                events.append(f"⚔️ Emboscada! O Peão preto atacou na diagonal e capturou o Peão branco que avançava para {chess.square_name(b_move.to_square)}!")
                if chess.square_rank(b_move.to_square) == 0:
                    prom_type = b_move.promotion if b_move.promotion else chess.QUEEN
                    b_piece = chess.Piece(prom_type, chess.BLACK)
                    events.append(f"👑 Peão preto promovido em {chess.square_name(b_move.to_square)}!")
                self.board.set_piece_at(b_move.to_square, b_piece)
                
            else:
                # Cenário A: Colisão na mesma casa -> Aniquilação Mútua!
                self.board.remove_piece_at(w_move.to_square)
                events.append(f"💥 COLISÃO EM {chess.square_name(w_move.to_square).upper()}! Ambas as peças ({w_piece.symbol()} branca e {b_piece.symbol()} preta) colidiram e foram aniquiladas!")
        else:
            # Movimento Branco
            if w_move and w_piece:
                captured = self.board.piece_at(w_move.to_square)
                is_pawn_forward = (w_piece.piece_type == chess.PAWN and chess.square_file(w_move.from_square) == chess.square_file(w_move.to_square))
                is_pawn_diagonal = (w_piece.piece_type == chess.PAWN and chess.square_file(w_move.from_square) != chess.square_file(w_move.to_square))

                if is_pawn_forward and captured:
                    events.append(f"🛡️ Bloqueio! O Peão branco tentou avançar, mas colidiu com a peça em {chess.square_name(w_move.to_square)} e recuou!")
                    self.board.set_piece_at(w_move.from_square, w_piece)
                elif is_pawn_diagonal and not captured:
                    events.append(f"💨 Vento! O Peão branco atacou {chess.square_name(w_move.to_square)} em vão e recuou!")
                    self.board.set_piece_at(w_move.from_square, w_piece)
                else:
                    if captured:
                        events.append(f"⚔️ Brancas capturaram {captured.symbol()} em {chess.square_name(w_move.to_square)}!")
                    
                    if w_piece.piece_type == chess.PAWN and chess.square_rank(w_move.to_square) == 7:
                        prom_type = w_move.promotion if w_move.promotion else chess.QUEEN
                        w_piece = chess.Piece(prom_type, chess.WHITE)
                        events.append(f"👑 Peão branco promovido em {chess.square_name(w_move.to_square)}!")

                    self.board.set_piece_at(w_move.to_square, w_piece)

            # Movimento Preto
            if b_move and b_piece:
                captured = self.board.piece_at(b_move.to_square)
                is_pawn_forward = (b_piece.piece_type == chess.PAWN and chess.square_file(b_move.from_square) == chess.square_file(b_move.to_square))
                is_pawn_diagonal = (b_piece.piece_type == chess.PAWN and chess.square_file(b_move.from_square) != chess.square_file(b_move.to_square))

                if is_pawn_forward and captured:
                    events.append(f"🛡️ Bloqueio! O Peão preto tentou avançar, mas colidiu com a peça em {chess.square_name(b_move.to_square)} e recuou!")
                    self.board.set_piece_at(b_move.from_square, b_piece)
                elif is_pawn_diagonal and not captured:
                    events.append(f"💨 Vento! O Peão preto atacou {chess.square_name(b_move.to_square)} em vão e recuou!")
                    self.board.set_piece_at(b_move.from_square, b_piece)
                else:
                    if captured:
                        events.append(f"⚔️ Pretas capturaram {captured.symbol()} em {chess.square_name(b_move.to_square)}!")
                    
                    if b_piece.piece_type == chess.PAWN and chess.square_rank(b_move.to_square) == 0:
                        prom_type = b_move.promotion if b_move.promotion else chess.QUEEN
                        b_piece = chess.Piece(prom_type, chess.BLACK)
                        events.append(f"👑 Peão preto promovido em {chess.square_name(b_move.to_square)}!")

                    self.board.set_piece_at(b_move.to_square, b_piece)

        # Passo 4: Verificar condição de vitória por queda do Rei
        white_king, black_king = self.check_kings_alive()
        if not white_king and not black_king:
            self.game_over = True
            self.winner = "empate"
            self.reason = "Aniquilação mútua dos Reis! Ambos os Reis foram destruídos na mesma rodada!"
            events.append("👑💥 AMBOS OS REIS CAÍRAM! O jogo terminou em empate!")
        elif not black_king:
            self.game_over = True
            self.winner = "white"
            self.reason = "O Rei Preto foi capturado ou aniquilado!"
            events.append("🏆 BRANCAS VENCEM! O Rei Preto foi destruído!")
        elif not white_king:
            self.game_over = True
            self.winner = "black"
            self.reason = "O Rei Branco foi capturado ou aniquilado!"
            events.append("🏆 PRETAS VENCEM! O Rei Branco foi destruído!")

        # Registro do Histórico
        round_info = {
            "round": self.round_number,
            "white_move": w_uci,
            "black_move": b_uci,
            "white_san": w_san,
            "black_san": b_san,
            "events": events,
            "fen_after": self.board.fen()
        }
        self.history.append(round_info)
        self.round_number += 1

        # Resetar escolhas para o próximo turno
        self.white_move_uci = None
        self.black_move_uci = None
        self.white_ready = False
        self.black_ready = False
        self.timer_seconds = self.turn_duration

        return {
            "fen": self.board.fen(),
            "white_move_uci": w_uci,
            "black_move_uci": b_uci,
            "white_move_san": w_san,
            "black_move_san": b_san,
            "events": events,
            "game_over": self.game_over,
            "winner": self.winner,
            "reason": self.reason
        }
