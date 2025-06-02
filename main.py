import os
import sys
import pgzrun
import pgzero, pygame
from pgzero.builtins import Actor, keyboard, keys
from pgzero.loaders import sounds
screen : pgzero.screen.Screen

from config import WIDTH, HEIGHT, game_state, GameState
from start_screen import draw_start_screen, handle_start_click
from player import update_player, draw_player, init_player, get_player_position, attack, update_wave, get_wave_actor
from map_loader import load_map, draw_map, get_tiles
from milk_dragon import spawn_dragons, update_dragons, draw_dragons, get_milk_dragons

os.environ['SDL_VIDEO_CENTERED'] = '1'

TITLE = '幻影迷宫'
WIDTH = WIDTH
HEIGHT = HEIGHT
clock = pygame.time.Clock()

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
    spawn_dragons(n=10)  # 每关生成n只怪物，可调整数量

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
        draw_player()  # 绘制玩家和声波
        draw_dragons()  # 绘制怪物

        # # ====== 临时画出碰撞框 ======
        # wave = get_wave_actor()
        # if wave and hasattr(wave, "rect"):
        #     screen.draw.rect(wave.rect, (255, 0, 0))  # 红色：声波
        # for dragon in get_milk_dragons():
        #     # 确保rect已同步
        #     if hasattr(dragon.actor, "rect"):
        #         screen.draw.rect(dragon.actor.rect, (0, 255, 0))  # 绿色：奶龙
        # # ===========================
        
    elif game_state == GameState.WIN:
        screen.fill((0, 0, 0))
        screen.draw.text('恭喜通关！', center=(WIDTH//2, HEIGHT//2), fontsize=100, color="yellow",fontname="s")

    # 始终绘制右上角退出按钮
    exit_button.draw()


# ---------------------------------------------------------
def update():  # 更新模块，每帧重复操作
    global player_frame_index, frame_count, game_state
    milk_dragons = get_milk_dragons()  # 获取当前奶龙列表
    if game_state == GameState.START or game_state == GameState.WIN:
        return

    frame_count += 1  # 增加帧计数器
    update_player(frame_count)  # 更新玩家位置和动画
    update_wave()  # 更新声波动画
    update_dragons(frame_count)  # 更新怪物状态

    # 冲击波攻击奶龙
    wave = get_wave_actor()
    if wave:
        for dragon in milk_dragons:
            if dragon.alive and wave.colliderect(dragon.actor):
                dragon.alive = False
                dragon.blowup_tick = 0

    # 移除已爆炸完成的奶龙
    milk_dragons[:] = [d for d in milk_dragons if d.alive != 'remove']

    # 出口判定：判断玩家是否在出口格子上
    player_x, player_y = get_player_position()
    tiles = get_tiles()
    
    for tile in tiles:
        if hasattr(tile, 'image') and 'out' in tile.image:
            if abs(player_x - tile.x) < 10 and abs(player_y - tile.y) < 10:
                next_level()
                break

    clock.tick(60)


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

# ---------------------------------------------------------
def on_key_down(key):
    if game_state == GameState.PLAYING and key == keys.SPACE:
        attack()

pgzrun.go()