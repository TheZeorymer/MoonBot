import chess
import time
import argparse
import json
import numpy as np
try:
    from moonbot_engine import BitboardMoonBot
except ImportError:
    BitboardMoonBot = None

class MoonBot:
    def __init__(self):
        if BitboardMoonBot is not None:
            self.engine = BitboardMoonBot()
        else:
            self.engine = None
        self.board = chess.Board()

    def make_move(self, move_uci):
        if self.engine is not None:
            # TODO: update bitboard engine state
            pass
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                return True
            else:
                print("Illegal move.")
                return False
        except ValueError:
            print("Invalid move format.")
            return False

    def evaluate_board(self):
        # Improved evaluation: material, piece-square tables, mobility, and checkmate
        values = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0}
        # Piece-square tables (simplified, for white; black is mirrored)
        pawn_table = [
            0, 5, 5, 0, 5, 10, 50, 0,
            0, 10, -5, 0, 5, 10, 50, 0,
            0, 10, -10, 0, 10, 20, 50, 0,
            0, -20, 0, 20, 25, 30, 50, 0,
            0, -20, 0, 20, 25, 30, 50, 0,
            0, 10, -10, 0, 10, 20, 50, 0,
            0, 10, -5, 0, 5, 10, 50, 0,
            0, 5, 5, 0, 5, 10, 50, 0
        ]
        knight_table = [
            -50, -40, -30, -30, -30, -30, -40, -50,
            -40, -20, 0, 0, 0, 0, -20, -40,
            -30, 0, 10, 15, 15, 10, 0, -30,
            -30, 5, 15, 20, 20, 15, 5, -30,
            -30, 0, 15, 20, 20, 15, 0, -30,
            -30, 5, 10, 15, 15, 10, 5, -30,
            -40, -20, 0, 5, 5, 0, -20, -40,
            -50, -40, -30, -30, -30, -30, -40, -50
        ]
        bishop_table = [
            -20, -10, -10, -10, -10, -10, -10, -20,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -10, 0, 5, 10, 10, 5, 0, -10,
            -10, 5, 5, 10, 10, 5, 5, -10,
            -10, 0, 10, 10, 10, 10, 0, -10,
            -10, 10, 10, 10, 10, 10, 10, -10,
            -10, 5, 0, 0, 0, 0, 5, -10,
            -20, -10, -10, -10, -10, -10, -10, -20
        ]
        rook_table = [
            0, 0, 0, 0, 0, 0, 0, 0,
            5, 10, 10, 10, 10, 10, 10, 5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            0, 0, 0, 5, 5, 0, 0, 0
        ]
        queen_table = [
            -20, -10, -10, -5, -5, -10, -10, -20,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -10, 0, 5, 5, 5, 5, 0, -10,
            -5, 0, 5, 5, 5, 5, 0, -5,
            0, 0, 5, 5, 5, 5, 0, -5,
            -10, 5, 5, 5, 5, 5, 0, -10,
            -10, 0, 5, 0, 0, 0, 0, -10,
            -20, -10, -10, -5, -5, -10, -10, -20
        ]
        king_table = [
            20, 30, 10, 0, 0, 10, 30, 20,
            20, 20, 0, 0, 0, 0, 20, 20,
            -10, -20, -20, -20, -20, -20, -20, -10,
            -20, -30, -30, -40, -40, -30, -30, -20,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30
        ]
        tables = {
            chess.PAWN: pawn_table,
            chess.KNIGHT: knight_table,
            chess.BISHOP: bishop_table,
            chess.ROOK: rook_table,
            chess.QUEEN: queen_table,
            chess.KING: king_table
        }
        eval = 0
        for piece_type in values:
            for square in self.board.pieces(piece_type, chess.WHITE):
                eval += values[piece_type]
                eval += tables[piece_type][square]
            for square in self.board.pieces(piece_type, chess.BLACK):
                eval -= values[piece_type]
                eval -= tables[piece_type][chess.square_mirror(square)]
        # Mobility (number of legal moves)
        eval += 5 * (self.board.legal_moves.count() if self.board.turn == chess.WHITE else -self.board.legal_moves.count())
        # Checkmate/stalemate
        if self.board.is_checkmate():
            eval = -99999 if self.board.turn == chess.WHITE else 99999
        elif self.board.is_stalemate():
            eval = 0
        return eval

    def minimax(self, depth, alpha, beta, maximizing):
        if depth == 0 or self.board.is_game_over():
            return self.evaluate_board(), None
        best_move = None
        if maximizing:
            max_eval = float('-inf')
            for move in self.board.legal_moves:
                self.board.push(move)
                eval, _ = self.minimax(depth-1, alpha, beta, False)
                self.board.pop()
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in self.board.legal_moves:
                self.board.push(move)
                eval, _ = self.minimax(depth-1, alpha, beta, True)
                self.board.pop()
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def get_best_move(self, depth=3):
        if self.engine is not None:
            score, move = self.engine.negamax(depth, -100000, 100000)
            return move
        _, move = self.minimax(depth, float('-inf'), float('inf'), self.board.turn)
        return move.uci() if move else None

    def print_board(self):
        print(self.board)

    def close(self):
        pass

    def bitboard_eval(self):
        # Simple bitboard-based material evaluation in centipawns
        # (for demonstration; can be extended for more features)
        wp = self.board.pieces(chess.PAWN, chess.WHITE)
        wn = self.board.pieces(chess.KNIGHT, chess.WHITE)
        wb = self.board.pieces(chess.BISHOP, chess.WHITE)
        wr = self.board.pieces(chess.ROOK, chess.WHITE)
        wq = self.board.pieces(chess.QUEEN, chess.WHITE)
        bp = self.board.pieces(chess.PAWN, chess.BLACK)
        bn = self.board.pieces(chess.KNIGHT, chess.BLACK)
        bb = self.board.pieces(chess.BISHOP, chess.BLACK)
        br = self.board.pieces(chess.ROOK, chess.BLACK)
        bq = self.board.pieces(chess.QUEEN, chess.BLACK)
        eval = (
            100 * len(wp) + 320 * len(wn) + 330 * len(wb) + 500 * len(wr) + 900 * len(wq)
            - 100 * len(bp) - 320 * len(bn) - 330 * len(bb) - 500 * len(br) - 900 * len(bq)
        )
        return eval

    def bitboard_negamax(self, depth, alpha, beta):
        if depth == 0 or self.board.is_game_over():
            return self.bitboard_eval(), None
        best_move = None
        max_eval = float('-inf')
        for move in self.board.legal_moves:
            self.board.push(move)
            eval, _ = self.bitboard_negamax(depth-1, -beta, -alpha)
            eval = -eval
            self.board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if alpha >= beta:
                break
        return max_eval, best_move

# --- Background move generation for cache ---
def generate_move_cache(depth=9, cache_file='move_sim_cache.json', max_positions=100000):
    bot = MoonBot()
    cache = {}
    visited = set()
    q = [(bot.board.fen(), bot.board.copy())]
    count = 0
    while q and count < max_positions:
        fen, board = q.pop(0)
        if fen in visited:
            continue
        visited.add(fen)
        bot.board = board.copy()
        score, move = bot.bitboard_negamax(depth, -100000, 100000)
        if move:
            cache[fen] = {'move': move.uci(), 'cp': score}
            # Explore next positions
            board.push(move)
            q.append((board.fen(), board.copy()))
        else:
            cache[fen] = {'move': None, 'cp': score}
        count += 1
        if count % 100 == 0:
            print(f"Generated {count} positions...")
    with open(cache_file, 'w') as f:
        json.dump(cache, f)
    print(f"Move cache generated for {count} positions at depth {depth}.")

def play_cli(depth=3, play_as='white', bot_vs_bot=False):
    bot = MoonBot()
    print("Welcome to MoonBot Chess! Enter your moves in UCI format (e.g., e2e4). Type 'quit' to exit.")
    print(f"Playing as: {play_as.capitalize()} | Depth: {depth} | Bot vs Bot: {bot_vs_bot}")
    bot.print_board()
    user_is_white = (play_as.lower() == 'white')
    while not bot.board.is_game_over():
        if bot_vs_bot or (bot.board.turn == chess.WHITE and not user_is_white) or (bot.board.turn == chess.BLACK and user_is_white):
            # Bot's move
            bot_move = bot.get_best_move(depth)
            if bot_move:
                print(f"MoonBot ({'White' if bot.board.turn == chess.WHITE else 'Black'}) plays: {bot_move}")
                bot.make_move(bot_move)
                bot.print_board()
            else:
                print("MoonBot could not find a move.")
                break
            if bot.board.is_game_over():
                break
            if not bot_vs_bot:
                continue
        if not bot_vs_bot:
            user_move = input("Your move: ")
            if user_move.lower() == "quit":
                break
            if bot.make_move(user_move):
                bot.print_board()
            else:
                print("Invalid or illegal move.")
    print("Game over!")
    bot.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate-cache', action='store_true', help='Generate move cache in background (no UI)')
    parser.add_argument('--depth', type=int, default=3, help='Search depth for MoonBot')
    parser.add_argument('--play-as', type=str, default='white', choices=['white', 'black'], help='Play as white or black (CLI)')
    parser.add_argument('--bot-vs-bot', action='store_true', help='Bot plays both sides automatically')
    args = parser.parse_args()
    if args.generate_cache:
        generate_move_cache(depth=args.depth)
        exit(0)
    play_cli(depth=args.depth, play_as=args.play_as, bot_vs_bot=args.bot_vs_bot)
