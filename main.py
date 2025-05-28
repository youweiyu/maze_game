import os
import sys
import pgzrun
import pgzero
from pgzero.builtins import Actor, keyboard
from pgzero.loaders import sounds
screen : pgzero.screen.Screen

from config import WIDTH, HEIGHT, game_state, GameState
from start_screen import draw_start_screen, handle_start_click
from player import update_player, draw_player, init_player, get_player_position
from map_loader import load_map, draw_map, get_tiles

os.environ['SDL_VIDEO_CENTERED'] = '1'

TITLE = '幻影迷宫'
WIDTH = WIDTH
HEIGHT = HEIGHT

game_state = game_state
frame_count = 0  # 帧计数器

# sounds. game_music.play(-1)  # 循环播放背景音乐

EXIT_BUTTON_POS = (WIDTH - 50, 25)
exit_button = Actor('exit', center=EXIT_BUTTON_POS)

levels = ['maps/map1.txt', 'maps/map2.txt', 'maps/map3.txt']
current_level = 0

# --------------------------辅助函数-------------------------
def load_level(level_index):
    load_map(levels[level_index])
    init_player()

def next_level():
    global current_level, game_state
    current_level += 1
    if current_level < len(levels):
        load_level(current_level)
        game_state = GameState.PLAYING
    else:
        game_state = GameState.WIN

# ---------------------------------------------------------
def draw():  # 绘制模块，每帧重复执行
    screen.clear()

    if game_state == GameState.START:
        draw_start_screen(screen)        
    elif game_state == GameState.PLAYING:
        screen.fill((255, 255, 255))
        draw_map()  # 绘制地图
        draw_player()  # 绘制玩家
    elif game_state == GameState.WIN:
        screen.fill((0, 0, 0))
        screen.draw.text('恭喜通关！', center=(WIDTH//2, HEIGHT//2), fontsize=100, color="yellow",fontname="s")

    # 始终绘制右上角退出按钮
    exit_button.draw()


# ---------------------------------------------------------
def update():  # 更新模块，每帧重复操作
    global player_frame_index, frame_count, game_state

    if game_state == GameState.START or game_state == GameState.WIN:
        return

    frame_count += 1  # 增加帧计数器
    update_player(frame_count)  # 更新玩家位置和动画

    # 出口判定：判断玩家是否在出口格子上
    player_x, player_y = get_player_position()
    tiles = get_tiles()
    
    for tile in tiles:
        if hasattr(tile, 'image') and 'out' in tile.image:
            if abs(player_x - tile.x) < 10 and abs(player_y - tile.y) < 10:
                next_level()
                break


# ---------------------------------------------------------
def on_mouse_move(pos, rel, buttons):  # 当鼠标移动时执行
    pass

# ---------------------------------------------------------
def on_mouse_down(pos, button): # 当鼠标键按下时
    global game_state, current_level
    # 检查是否点击退出按钮
    if exit_button.collidepoint(pos):
        sys.exit()

    # 处理其他鼠标点击事件
    if game_state == GameState.START:
       if handle_start_click(pos):
           current_level = 0
           load_level(current_level)  # 加载地图
           init_player()  # 初始化玩家位置
           game_state = GameState.PLAYING

pgzrun.go()