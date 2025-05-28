from pgzero.builtins import Actor
from config import TILE_SIZE, MAP_CHARACTERS

# 地图 Actor 列表
tiles = []
player_start_pos = (0, 0)

def load_map(filename):
    global tiles, player_start_pos
    tiles = []

    with open(filename, 'r') as f:
        lines = [line.rstrip('\n') for line in f]

    for row, line in enumerate(lines):
        for col, char in enumerate(line):
            x = col * TILE_SIZE + TILE_SIZE // 2
            y = row * TILE_SIZE + TILE_SIZE // 2

            if char in MAP_CHARACTERS:
                tiles.append(Actor(MAP_CHARACTERS[char], (x, y)))
                # 如果是起点，记录玩家起始位置
                if MAP_CHARACTERS[char].endswith('_start'):
                    player_start_pos = (x, y)

def draw_map():
    for tile in tiles:
        tile.draw()

def get_player_start():
    return player_start_pos
