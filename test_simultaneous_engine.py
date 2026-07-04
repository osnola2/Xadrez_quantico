import pytest
import chess
from backend.game import SimultaneousChessGame

def test_scenario_a_mutual_annihilation():
    """Teste do Cenário A: Dois movimentos para a mesma casa resultam em Aniquilação Mútua."""
    game = SimultaneousChessGame(room_id="test_room")
    game.board.clear()
    game.board.set_piece_at(chess.D1, chess.Piece(chess.ROOK, chess.WHITE))
    game.board.set_piece_at(chess.D8, chess.Piece(chess.ROOK, chess.BLACK))
    game.board.set_piece_at(chess.A1, chess.Piece(chess.KING, chess.WHITE))
    game.board.set_piece_at(chess.H8, chess.Piece(chess.KING, chess.BLACK))

    # Turno 1: Torre branca d1 -> d5, Torre preta d8 -> d5 (colisão na mesma casa d5!)
    game.submit_move("d1d5", chess.WHITE)
    game.submit_move("d8d5", chess.BLACK)
    result = game.resolve_turn()

    # Verificar se a casa d5 está VAZIA após a aniquilação mútua
    d5_piece = game.board.piece_at(chess.D5)
    assert d5_piece is None, "A casa d5 deveria estar vazia após a aniquilação mútua!"
    assert any("COLISÃO" in event for event in result["events"]), "Deveria haver um evento de colisão reportado."

def test_scenario_b_and_c_evasion_and_crossing():
    """Teste dos Cenários B e C: Alvo se moveu (ou cruzamento direto), ataque cai em casa vazia."""
    game = SimultaneousChessGame(room_id="test_room2")
    # Vamos limpar o tabuleiro e colocar duas Torres se encarando em e1 e e8
    game.board.clear()
    game.board.set_piece_at(chess.E1, chess.Piece(chess.ROOK, chess.WHITE))
    game.board.set_piece_at(chess.E8, chess.Piece(chess.ROOK, chess.BLACK))
    game.board.set_piece_at(chess.A1, chess.Piece(chess.KING, chess.WHITE))
    game.board.set_piece_at(chess.H8, chess.Piece(chess.KING, chess.BLACK))

    # Turno: Torre branca vai para e8 (onde a Torre preta ESTAVA), e Torre preta vai para e1 (cruzamento C / esquiva B)
    game.submit_move("e1e8", chess.WHITE)
    game.submit_move("e8e1", chess.BLACK)
    result = game.resolve_turn()

    # Verificar se a Torre branca chegou em e8 ilesa e a Torre preta chegou em e1 ilesa
    e8_piece = game.board.piece_at(chess.E8)
    e1_piece = game.board.piece_at(chess.E1)
    assert e8_piece is not None and e8_piece.color == chess.WHITE, "Torre branca deveria estar em e8"
    assert e1_piece is not None and e1_piece.color == chess.BLACK, "Torre preta deveria estar em e1"
    assert not any("COLISÃO" in event for event in result["events"]), "Não deve haver colisão em um cruzamento!"

def test_king_capture_win_condition():
    """Teste de condição de vitória: Captura direta do Rei."""
    game = SimultaneousChessGame(room_id="test_room3")
    game.board.clear()
    game.board.set_piece_at(chess.E1, chess.Piece(chess.ROOK, chess.WHITE))
    game.board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
    game.board.set_piece_at(chess.A1, chess.Piece(chess.KING, chess.WHITE))

    # Torre branca ataca e8 (captura o Rei preto). Rei preto não se move.
    game.submit_move("e1e8", chess.WHITE)
    result = game.resolve_turn()

    assert game.game_over is True, "O jogo deveria terminar ao capturar o Rei"
    assert game.winner == "white", "Brancas deveriam ser as vencedoras"
    assert "🏆 BRANCAS VENCEM" in result["events"][-1], "Mensagem de vitória deveria estar nos eventos"

if __name__ == "__main__":
    test_scenario_a_mutual_annihilation()
    test_scenario_b_and_c_evasion_and_crossing()
    test_king_capture_win_condition()
    print("[SUCESSO] TODOS OS TESTES DO MOTOR SIMULTANEO PASSARAM COM SUCESSO!")
