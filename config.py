from enum import Enum, auto

class GameState(Enum):
    START = auto()
    PLAYING = auto()
    WIN = auto()
    GAME_OVER = auto()

game_state = GameState.START

WIDTH = 1500
HEIGHT = 800
TILE_SIZE = 50
Dragon_SPEED = 2  # 奶龙移动速度
PLAYER_SPEED = 4  # 玩家移动速度

# 地图字符说明
MAP_CHARACTERS = {
    'W': 'brick',  # 墙壁

    'G': 'map0',   # 绿色地面
    'a': 'grass_start',  # 绿色起始点
    'b': 'grass_out_close' ,  # 绿色出口关闭态
    'g': 'grass_out_open',  # 绿色出口1
    'j': 'grass_out_open',  # 绿色出口2 


    'Y': 'map1',   # 黄色地面
    'c': 'yellow_start',  # 黄色起始点
    'd': 'yellow_out_close',  # 黄色出口关闭态
    'h': 'yellow_out_open',  # 黄色出口1 
    'l': 'yellow_out_open',  # 黄色出口2


    'I': 'map2',   # 冰地面
    'e': 'ice_start',  # 冰起始点
    'f': 'ice_out_close',  # 冰出口关闭态
    'i': 'ice_out_open',  # 冰出口1
    'n': 'ice_out_open',  # 冰出口2

}

# 跳转关系
# 1，2为绿 3,4为黄 5,6为冰
# 起始点记录 1(2,2) 2(2,8) 3(8,29) 4(15,2) 5(15,28) 6(2,4)
EXIT_JUMP = {
    1 :{ 'g': 3, 'j': 5 },  
    2 :{ 'g': 4, 'j': 6 },
    3 :{ 'h': 2, 'l': 6 },
    4 :{ 'h': 1, 'l': 5 },
    5 :{ 'i': 2, 'f': 7 },
    6 :{ 'i': 1, 'n': 3 },
}
