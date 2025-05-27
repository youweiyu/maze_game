from pgzero.builtins import Actor
from config import TILE_SIZE

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

            if char == 'W':
                tiles.append(Actor("brick", (x, y)))
            elif char == ' ':
                tiles.append(Actor("map0", (x, y)))
            elif char == 'S':
                tiles.append(Actor("grass_start", (x, y)))
                player_start_pos = (x, y)
            elif char == 'E':
                tiles.append(Actor("out", (x, y)))

def draw_map():
    for tile in tiles:
        tile.draw()

def get_player_start():
    return player_start_pos
