import os
import requests

# Directory to save sprites
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
os.makedirs(ASSETS_DIR, exist_ok=True)

# Piece names and URLs (using Wikimedia Commons open PNGs)
PIECE_URLS = {
    'wK': 'https://upload.wikimedia.org/wikipedia/commons/3/3b/Chess_klt60.png',
    'wQ': 'https://upload.wikimedia.org/wikipedia/commons/4/49/Chess_qlt60.png',
    'wR': 'https://upload.wikimedia.org/wikipedia/commons/5/5c/Chess_rlt60.png',
    'wB': 'https://upload.wikimedia.org/wikipedia/commons/9/9b/Chess_blt60.png',
    'wN': 'https://upload.wikimedia.org/wikipedia/commons/2/28/Chess_nlt60.png',
    'wP': 'https://upload.wikimedia.org/wikipedia/commons/0/04/Chess_plt60.png',
    'bK': 'https://upload.wikimedia.org/wikipedia/commons/e/e3/Chess_kdt60.png',
    'bQ': 'https://upload.wikimedia.org/wikipedia/commons/a/af/Chess_qdt60.png',
    'bR': 'https://upload.wikimedia.org/wikipedia/commons/a/a0/Chess_rdt60.png',
    'bB': 'https://upload.wikimedia.org/wikipedia/commons/8/81/Chess_bdt60.png',
    'bN': 'https://upload.wikimedia.org/wikipedia/commons/f/f1/Chess_ndt60.png',
    'bP': 'https://upload.wikimedia.org/wikipedia/commons/c/cd/Chess_pdt60.png',
}

def download_sprites():
    for name, url in PIECE_URLS.items():
        out_path = os.path.join(ASSETS_DIR, f'{name}.png')
        if not os.path.exists(out_path):
            print(f'Downloading {name}...')
            try:
                headers = {'User-Agent': 'MoonBotChess/1.0 (https://github.com/yourusername/moonbot)'}
                r = requests.get(url, timeout=10, headers=headers)
                r.raise_for_status()
                with open(out_path, 'wb') as f:
                    f.write(r.content)
            except Exception as e:
                print(f'Failed to download {name}: {e}')
        else:
            print(f'{name} already exists.')

if __name__ == '__main__':
    download_sprites()
