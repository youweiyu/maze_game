from enum import Enum, auto

class GameState(Enum):
    START = auto()
    PLAYING = auto()
    WIN = auto()

game_state = GameState.START

WIDTH = 1500
HEIGHT = 800
TILE_SIZE = 50

# 地图字符说明
MAP_CHARACTERS = {
    'W': 'brick',  # 墙壁

    'G': 'map0',   # 绿色地面
    'a': 'grass_start',  # 绿色起始点
    'b': 'grass_out' ,  # 绿色出口

    'Y': 'map1',   # 黄色地面
    'c': 'yellow_start',  # 黄色起始点
    'd': 'yellow_out',  # 黄色出口

    'I': 'map2',   # 冰地面
    'e': 'ice_start',  # 冰起始点
    'f': 'ice_out',  # 冰出口
}