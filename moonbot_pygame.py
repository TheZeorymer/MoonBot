import pygame
import chess
import sys
import math
import os
import random
import threading
import json
import urllib.request
import io
import chess.pgn
import concurrent.futures
from moonbot import MoonBot  # Instead of defining MoonBot here, import it from moonbot.py

# Constants
WIDTH, HEIGHT = 480, 480
SQUARE_SIZE = WIDTH // 8
WHITE = (240, 217, 181)
BROWN = (181, 136, 99)
HIGHLIGHT = (186, 202, 68)
FPS = 30

# Piece colors
PIECE_WHITE = (60, 120, 255)  # Blue
PIECE_BLACK = (220, 40, 40)   # Red
PIECE_ACCENT = (30, 60, 120)  # Dark blue accent
PIECE_IMAGES = {}
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
PIECE_SPRITE_FILENAMES = {
    'P': 'wP.png', 'N': 'wN.png', 'B': 'wB.png', 'R': 'wR.png', 'Q': 'wQ.png', 'K': 'wK.png',
    'p': 'bP.png', 'n': 'bN.png', 'b': 'bB.png', 'r': 'bR.png', 'q': 'bQ.png', 'k': 'bK.png',
}
# Pixel art for each piece (8x8, more realistic, blue for white, red for black)
PIECE_PIXELS = {
    'P': [
        [0,0,0,1,1,0,0,0],
        [0,0,1,1,1,1,0,0],
        [0,0,1,1,1,1,0,0],
        [0,0,1,1,1,1,0,0],
        [0,0,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,0],
        [1,1,1,1,1,1,1,1],
        [0,0,1,1,1,1,0,0],
    ],
    'N': [
        [0,0,0,1,1,0,0,0],
        [0,0,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,0],
        [0,1,1,0,1,1,1,0],
        [0,1,1,1,1,1,1,0],
        [0,0,1,1,1,1,1,1],
        [0,0,1,1,1,1,1,1],
        [0,0,1,1,1,1,0,0],
    ],
    'B': [
        [0,0,0,1,1,0,0,0],
        [0,0,1,1,1,1,0,0],
        [0,0,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,0],
        [0,0,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,0],
        [1,1,1,1,1,1,1,1],
        [0,0,1,1,1,1,0,0],
    ],
    'R': [
        [1,0,1,1,1,1,0,1],
        [1,1,1,1,1,1,1,1],
        [1,1,0,1,1,0,1,1],
        [1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1],
        [0,0,1,1,1,1,0,0],
    ],
    'Q': [
        [0,1,0,1,1,0,1,0],
        [1,0,1,1,1,1,0,1],
        [1,1,1,1,1,1,1,1],
        [0,1,1,1,1,1,1,0],
        [0,1,1,1,1,1,1,0],
        [0,1,1,1,1,1,1,0],
        [1,1,1,1,1,1,1,1],
        [0,0,1,1,1,1,0,0],
    ],
    'K': [
        [0,0,1,0,0,1,0,0],
        [0,0,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,0],
        [0,0,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,0],
        [1,1,1,1,1,1,1,1],
        [0,1,1,1,1,1,1,0],
        [0,0,1,1,1,1,0,0],
    ],
}
for k in list(PIECE_PIXELS.keys()):
    PIECE_PIXELS[k.lower()] = PIECE_PIXELS[k]

def generate_piece_surface(piece, size):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    color = PIECE_WHITE if piece.isupper() else PIECE_BLACK
    accent = PIECE_ACCENT if piece.isupper() else (120,40,40)
    pixels = PIECE_PIXELS[piece]
    grid_size = len(pixels)
    px = max(size // grid_size, 1)
    offset = (size - px*grid_size) // 2
    for y in range(grid_size):
        for x in range(len(pixels[y])):
            if pixels[y][x]:
                pygame.draw.rect(surf, color, (offset + x*px, offset + y*px, px, px))
            elif (x+y)%2==0:
                pygame.draw.rect(surf, accent, (offset + x*px, offset + y*px, px, px), 1)
    return surf

def load_images():
    # Try to load PNG sprites from assets, else use pixel art
    for piece in PIECE_PIXELS:
        sprite_path = os.path.join(ASSETS_DIR, PIECE_SPRITE_FILENAMES.get(piece, ''))
        if os.path.exists(sprite_path):
            try:
                img = pygame.image.load(sprite_path).convert_alpha()
                img = pygame.transform.smoothscale(img, (SQUARE_SIZE, SQUARE_SIZE))
                PIECE_IMAGES[piece] = img
            except Exception:
                PIECE_IMAGES[piece] = generate_piece_surface(piece, SQUARE_SIZE)
        else:
            PIECE_IMAGES[piece] = generate_piece_surface(piece, SQUARE_SIZE)

# --- Common chess openings for book moves ---
OPENING_BOOK = [
    # e4 openings
    ["e2e4", "e7e5", "g1f3", "b8c6"],  # King's Knight Opening
    ["e2e4", "c7c5"],  # Sicilian Defence
    ["e2e4", "e7e6"],  # French Defence
    ["e2e4", "c7c6"],  # Caro-Kann
    ["e2e4", "d7d6"],  # Pirc Defence
    # d4 openings
    ["d2d4", "d7d5", "c2c4"],  # Queen's Gambit
    ["d2d4", "g8f6"],  # Indian Defence
    ["d2d4", "d7d5", "c2c4", "e7e6"],  # QGD
    ["d2d4", "d7d5", "c2c4", "c7c6"],  # Slav Defence
    # English
    ["c2c4"],
    # Reti
    ["g1f3"],
]

# --- NegaC* search ---
# (Cython optimization support removed)

OPENING_BOOK_DB = os.path.join(os.path.dirname(__file__), 'openings.pgn')

class OpeningBook:
    def __init__(self, pgn_path=OPENING_BOOK_DB):
        self.book = {}
        if not os.path.exists(pgn_path):
            print(f"[MoonBot] Opening book not found: {pgn_path}\nYou can download a Lichess PGN or use OpeningBook.download_lichess_book().")
            return
        with open(pgn_path, 'r', encoding='utf-8') as f:
            self._parse_pgn(f.read())

    def _parse_pgn(self, pgn_text):
        pgn_io = io.StringIO(pgn_text)
        while True:
            game = chess.pgn.read_game(pgn_io)
            if game is None:
                break
            board = game.board()
            for move in game.mainline_moves():
                fen = board.fen()
                if fen not in self.book:
                    self.book[fen] = move.uci()
                board.push(move)

    def get_move(self, fen):
        return self.book.get(fen)

    @staticmethod
    def download_lichess_book(pgn_path=OPENING_BOOK_DB):
        url = 'https://database.lichess.org/lichess_db_standard_rated_2023-12.pgn.bz2'  # Example, can be changed
        print('Downloading opening book (this may take a while)...')
        import bz2
        response = urllib.request.urlopen(url)
        decompressor = bz2.BZ2Decompressor()
        with open(pgn_path, 'w', encoding='utf-8') as out:
            for chunk in iter(lambda: response.read(1024*1024), b''):
                data = decompressor.decompress(chunk)
                out.write(data.decode('utf-8', errors='ignore'))
        print('Opening book downloaded.')

try:
    import cython
except ImportError:
    cython = None

def draw_board(win, board, selected_square=None, color_choice=0):
    for row in range(8):
        for col in range(8):
            # Flip board for black
            display_row, display_col = (row, col) if color_choice == 0 else (7-row, 7-col)
            color = WHITE if (display_row + display_col) % 2 == 0 else BROWN
            rect = pygame.Rect(display_col * SQUARE_SIZE, display_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(win, color, rect)
            if selected_square == (row, col):
                pygame.draw.rect(win, HIGHLIGHT, rect, 5)
            # Get the correct square for the board
            board_row, board_col = (row, col) if color_choice == 0 else (7-row, 7-col)
            piece = board.piece_at(chess.square(board_col, 7 - board_row))
            if piece:
                win.blit(PIECE_IMAGES[piece.symbol()], rect)

def get_square_under_mouse(pos):
    x, y = pos
    col = x // SQUARE_SIZE
    row = y // SQUARE_SIZE
    return (row, col)

def menu():
    pygame.init()
    win = pygame.display.set_mode((420, 340))
    pygame.display.set_caption("MoonBot Chess Menu")
    font = pygame.font.SysFont("arialblack", 40)
    small_font = pygame.font.SysFont("arial", 28)
    tiny_font = pygame.font.SysFont("arial", 20)
    color_choice = 0  # 0=White, 1=Black
    depth = 3
    running = True
    while running:
        win.fill((18, 22, 32))
        # Title
        pygame.draw.rect(win, (60, 120, 255), (0, 0, 420, 70), border_radius=18)
        title = font.render("MoonBot Chess", True, (255,255,255))
        win.blit(title, (60, 18))
        # Depth selection
        pygame.draw.rect(win, (40, 44, 64), (40, 90, 340, 60), border_radius=12)
        d_label = small_font.render(f"Search Depth:", True, (200,220,255))
        win.blit(d_label, (60, 105))
        minus_btn = pygame.Rect(250, 100, 36, 36)
        plus_btn = pygame.Rect(320, 100, 36, 36)
        pygame.draw.rect(win, (60,120,255) if depth>1 else (80,80,80), minus_btn, border_radius=8)
        pygame.draw.rect(win, (60,120,255) if depth<18 else (80,80,80), plus_btn, border_radius=8)
        win.blit(font.render("-", True, (255,255,255)), (255, 98))
        win.blit(font.render("+", True, (255,255,255)), (325, 98))
        win.blit(small_font.render(str(depth), True, (255,255,255)), (295, 105))
        # Color selection
        pygame.draw.rect(win, (40, 44, 64), (40, 170, 340, 60), border_radius=12)
        c_label = small_font.render("Play as:", True, (200,220,255))
        win.blit(c_label, (60, 185))
        w_box = pygame.Rect(200, 180, 70, 36)
        b_box = pygame.Rect(290, 180, 70, 36)
        pygame.draw.rect(win, (255,255,255) if color_choice==0 else (60,120,255), w_box, border_radius=8)
        pygame.draw.rect(win, (40,40,40) if color_choice==1 else (220,40,40), b_box, border_radius=8)
        win.blit(small_font.render("White", True, (0,0,0)), (210, 185))
        win.blit(small_font.render("Black", True, (255,255,255)), (300, 185))
        # Start button
        start_btn = pygame.Rect(120, 290, 180, 40)
        pygame.draw.rect(win, (100,200,100), start_btn, border_radius=12)
        win.blit(font.render("Start", True, (0,0,0)), (160, 295))
        # Footer
        win.blit(tiny_font.render("MoonBot by snave | Cython support: {}".format('ON' if cython else 'OFF'), True, (120,120,160)), (10, 330))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if minus_btn.collidepoint(x, y):
                    depth = max(1, depth-1)
                elif plus_btn.collidepoint(x, y):
                    depth = min(18, depth+1)
                elif w_box.collidepoint(x, y):
                    color_choice = 0
                elif b_box.collidepoint(x, y):
                    color_choice = 1
                elif start_btn.collidepoint(x, y):
                    running = False
    pygame.quit()
    return depth, color_choice

# Remove MoveSimulator and simulation mode from menu and main

def main():
    depth, color_choice = menu()
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("MoonBot Chess (Pygame)")
    clock = pygame.time.Clock()
    load_images()
    bot = MoonBot()
    selected = None
    running = True
    user_turn = (color_choice == 0)
    move_from = None
    move_to = None
    game_over = False
    game_over_message = None
    while running:
        clock.tick(FPS)
        draw_board(win, bot.board, selected, color_choice)
        if game_over_message:
            font = pygame.font.SysFont("arialblack", 32)
            msg = font.render(game_over_message, True, (255,80,80))
            win.blit(msg, (40, HEIGHT//2-20))
            small = pygame.font.SysFont("arial", 20)
            win.blit(small.render("Press any key or close window to exit", True, (200,200,200)), (40, HEIGHT//2+30))
        pygame.display.flip()
        if game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
            continue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and user_turn and not bot.board.is_game_over():
                pos = pygame.mouse.get_pos()
                row, col = get_square_under_mouse(pos)
                input_row, input_col = (row, col) if color_choice == 0 else (7-row, 7-col)
                square = chess.square(input_col, 7 - input_row)
                if selected is None:
                    piece = bot.board.piece_at(square)
                    if piece and ((piece.color == chess.WHITE and color_choice == 0) or (piece.color == chess.BLACK and color_choice == 1)):
                        selected = (row, col)
                        move_from = square
                else:
                    move_to = square
                    move = chess.Move(move_from, move_to)
                    if chess.square_rank(move_from) == (6 if color_choice == 0 else 1) and chess.square_rank(move_to) == (7 if color_choice == 0 else 0) and bot.board.piece_at(move_from).piece_type == chess.PAWN:
                        move = chess.Move(move_from, move_to, promotion=chess.QUEEN)
                    if move in bot.board.legal_moves:
                        bot.board.push(move)
                        user_turn = False
                    selected = None
                    move_from = None
                    move_to = None
        if not user_turn and not bot.board.is_game_over():
            pygame.display.set_caption("MoonBot is thinking...")
            draw_board(win, bot.board, None, color_choice)
            pygame.display.flip()
            bot_move = bot.get_best_move(depth)
            if bot_move:
                bot.board.push(bot_move)
            user_turn = True
            pygame.display.set_caption("MoonBot Chess (Pygame)")
        # Check for game over
        if bot.board.is_game_over():
            game_over = True
            result = bot.board.result()
            if bot.board.is_checkmate():
                if bot.board.turn == chess.WHITE:
                    game_over_message = "Black wins by checkmate!"
                else:
                    game_over_message = "White wins by checkmate!"
            elif bot.board.is_stalemate():
                game_over_message = "Draw by stalemate!"
            elif bot.board.is_insufficient_material():
                game_over_message = "Draw: Insufficient material!"
            elif bot.board.is_seventyfive_moves():
                game_over_message = "Draw: 75-move rule!"
            elif bot.board.is_fivefold_repetition():
                game_over_message = "Draw: Fivefold repetition!"
            else:
                game_over_message = f"Game over: {result}"
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
