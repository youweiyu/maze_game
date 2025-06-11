from pgzero.builtins import Actor
from config import TILE_SIZE, MAP_CHARACTERS

# 地图 Actor 列表
tiles = []
player_start_pos = (0, 0)
wall_positions = set()  # 新增：存储所有墙壁格子的中心坐标

def load_map(filename):
    global tiles, player_start_pos, wall_positions
    tiles = []
    wall_positions = set()

    with open(filename, 'r') as f:
        lines = [line.rstrip('\n') for line in f]

    for row, line in enumerate(lines):
        for col, char in enumerate(line):
            x = col * TILE_SIZE + TILE_SIZE // 2
            y = row * TILE_SIZE + TILE_SIZE // 2

            if char in MAP_CHARACTERS:
                tile = Actor(MAP_CHARACTERS[char], (x, y))
                tile.char = char   # ★★★ 关键：保存原始地图字符
                tiles.append(tile)
                # 如果是起点，记录玩家起始位置
                if MAP_CHARACTERS[char].endswith('_start'):
                    player_start_pos = (x, y)
                # 如果是墙壁，记录位置
                if MAP_CHARACTERS[char] == 'brick':
                    wall_positions.add((x, y))
            # 其他字符忽略

def draw_map():
    for tile in tiles:
        tile.draw()

def get_player_start():
    return player_start_pos

def get_wall_positions():
    return wall_positions

def get_tiles():
    return tiles

# 代码无需更改，道具生成已由主逻辑level_item_cache控制
