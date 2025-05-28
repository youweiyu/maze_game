import os
import pgzrun
import pgzero
from pgzero.builtins import Actor, keyboard
from pgzero.loaders import sounds
screen : pgzero.screen.Screen

from config import WIDTH, HEIGHT, game_state
from start_screen import draw_start_screen, handle_start_click
from player import update_player, draw_player, init_player
from map_loader import load_map, draw_map

os.environ['SDL_VIDEO_CENTERED'] = '1'

TITLE = '幻影迷宫'
WIDTH = WIDTH
HEIGHT = HEIGHT

game_state = game_state
frame_count = 0  # 帧计数器

# sounds. game_music.play(-1)  # 循环播放背景音乐

# ---------------------------------------------------------
def draw():  # 绘制模块，每帧重复执行
    screen.clear()

    if game_state == 'start':
        draw_start_screen(screen)        
    elif game_state == 'playing':
        screen.fill((255, 255, 255))  # 填充背景颜色
        draw_map()  # 绘制地图
        draw_player()  # 绘制玩家


# ---------------------------------------------------------
def update():  # 更新模块，每帧重复操作
    global player_frame_index, frame_count, game_state

    if game_state == 'start':
        return

    frame_count += 1  # 增加帧计数器
    update_player(frame_count)  # 更新玩家位置和动画


# ---------------------------------------------------------
def on_mouse_move(pos, rel, buttons):  # 当鼠标移动时执行
    pass

# ---------------------------------------------------------
def on_mouse_down(pos,button): # 当鼠标键按下时
    global game_state
    if game_state == 'start':
       if handle_start_click(pos):
           load_map('maps/map1.txt')  # 加载地图
           init_player()  # 初始化玩家位置
           game_state = 'playing'

pgzrun.go()