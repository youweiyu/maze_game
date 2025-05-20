import os
import pgzrun
import pgzero
from pgzero.builtins import Actor, keyboard
from pgzero.loaders import sounds
screen : pgzero.screen.Screen

import start_screen

os.environ['SDL_VIDEO_CENTERED'] = '1'

WIDTH = 1500   # 设置窗口的宽度
HEIGHT = 800   # 设置窗口的高度
TITLE = '幻影迷宫'

# 状态
game_state = False  # 游戏状态，初始为False

# 人物
player_frames = ['bat0', 'bat1', 'bat2', 'bat3', 'bat4']  # 人物精灵列表
player_frame_index = 0 # 人物精灵索引
player = Actor(player_frames[player_frame_index]) # 创建人物精灵
player.pos = (WIDTH // 2, HEIGHT // 2)  # 设置人物初始位置
player.speed = 5  # 设置人物移动速度

frame_count = 0  # 帧计数器

sounds. game_music.play(-1)  # 循环播放背景音乐

def draw():  # 绘制模块，每帧重复执行
    screen.clear()  
    if not game_state:
        start_screen.run()
    else:
        screen.fill((255, 255, 255))  # 填充背景颜色
        player.draw()  # 绘制人物

def update():  # 更新模块，每帧重复操作
    global player_frame_index, frame_count
    if not game_state:
        return

    frame_count += 1  # 增加帧计数器
    if frame_count % 5 == 0:  # 每5帧更新一次
        player_frame_index = (player_frame_index + 1) % len(player_frames)  # 更新人物精灵索引
        player.image = player_frames[player_frame_index]  # 更新人物精灵图像

def on_mouse_move(pos, rel, buttons):  # 当鼠标移动时执行
    pass

def on_mouse_down(): # 当鼠标键按下时
    pass

pgzrun.go()  # 开始执行游戏
