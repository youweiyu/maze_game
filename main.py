import os
import pgzrun
import pgzero
from pgzero.builtins import Actor, keyboard
from pgzero.loaders import sounds
screen : pgzero.screen.Screen

from config import WIDTH, HEIGHT
from game_state import game_state
from start_screen import draw_start_screen, update_start_screen, handle_mouse_move, handle_start_click
os.environ['SDL_VIDEO_CENTERED'] = '1'

TITLE = '幻影迷宫'
WIDTH = WIDTH
HEIGHT = HEIGHT

game_state = game_state

# 人物
player_frames = ['bat0', 'bat1', 'bat2', 'bat3', 'bat4']  # 人物精灵列表
player_frame_index = 0 # 人物精灵索引
player = Actor(player_frames[player_frame_index]) # 创建人物精灵
player.pos = (WIDTH // 2, HEIGHT // 2)  # 设置人物初始位置
player.speed = 5  # 设置人物移动速度

frame_count = 0  # 帧计数器

# sounds. game_music.play(-1)  # 循环播放背景音乐

def draw():  # 绘制模块，每帧重复执行
    screen.clear()

    if game_state == 'start':
        draw_start_screen(screen)        
    elif game_state == 'playing':
        screen.fill((255, 255, 255))  # 填充背景颜色
        player.draw()  # 绘制人物

def update():  # 更新模块，每帧重复操作
    global player_frame_index, frame_count, game_state

    if game_state == 'start':
        return

    frame_count += 1  # 增加帧计数器
    if frame_count % 5 == 0:  # 每5帧更新一次
        player_frame_index = (player_frame_index + 1) % len(player_frames)  # 更新人物精灵索引
        player.image = player_frames[player_frame_index]  # 更新人物精灵图像

def on_mouse_move(pos, rel, buttons):  # 当鼠标移动时执行
    global game_state
    if game_state == 'start':
        handle_mouse_move(pos)

def on_mouse_down(pos,button): # 当鼠标键按下时
    global game_state
    if game_state == 'start':
       if handle_start_click(pos):
           game_state = 'playing'

pgzrun.go()  # 开始执行游戏
