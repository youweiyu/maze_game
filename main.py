import os
import sys
import random
import pgzrun
import pgzero, pygame
from pgzero.builtins import Actor, keyboard, keys
from pgzero.loaders import sounds
screen : pgzero.screen.Screen

from config import WIDTH, HEIGHT, game_state, GameState, EXIT_JUMP, TILE_SIZE
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

levels = ['maps/map1.txt', 'maps/map2.txt', 'maps/map3.txt', 'maps/map4.txt', 'maps/map5.txt', 'maps/map6.txt']
current_level = 0

player_lives = 3  # 初始三条命
max_lives = 4     # 生命上限
blood_pos = None  # 当前关卡的血包位置
coin_positions = []  # 当前关卡金币位置列表
collected_coins = 0  # 总金币数

# --------------------------辅助函数-------------------------
def load_level(level_index):
    global blood_pos, coin_positions
    load_map(levels[level_index])
    init_player()
    spawn_dragons(n=10)  # 每关生成n只怪物，可调整数量

    # 随机生成一个血包
    tiles = get_tiles()
    walkable_tiles = [t for t in tiles if hasattr(t, 'char') and t.char in ('G', 'Y', 'I')]
    if walkable_tiles:
        blood_tile = random.choice(walkable_tiles)
        blood_pos = (blood_tile.x, blood_tile.y)
    else:
        blood_pos = None

    # 随机生成10个金币
    coin_positions = []
    if walkable_tiles:
        coin_tiles = random.sample(walkable_tiles, min(10, len(walkable_tiles)))
        for t in coin_tiles:
            coin_positions.append((t.x, t.y))

# ---------------------------------------------------------
def draw():  # 绘制模块，每帧重复执行
    global game_state, current_level, player_lives, blood_pos, coin_positions, collected_coins
    screen.clear()

    if game_state == GameState.START:
        draw_start_screen(screen)        
    elif game_state == GameState.PLAYING:
        screen.fill((255, 255, 255))
        draw_map()  # 绘制地图

        # 先绘制血包和金币（确保在地图之上，玩家之下）
        if blood_pos:
            blood_actor = Actor('blood', center=blood_pos)
            blood_actor.draw()
        for pos in coin_positions:
            coin_actor = Actor('coin', center=pos)
            coin_actor.draw()

        draw_player()  # 绘制玩家和声波
        draw_dragons()  # 绘制怪物

        # 顶部显示6个小图标
        icon_y = 25
        icon_size = 60
        gap = 30
        total_width = 6 * icon_size + 5 * gap
        start_x = WIDTH // 2 - total_width // 2 + icon_size // 2
        for i in range(6):
            icon_name = f"side{i+1}"
            icon_x = start_x + i * (icon_size + gap)
            if current_level == i:
                # 当前关卡：正常大小
                icon = Actor(icon_name, center=(icon_x, icon_y))
            else:
                # 其他关卡：缩小为40x40
                icon = Actor(icon_name, center=(icon_x, icon_y))
                icon._surf = pygame.transform.smoothscale(icon._orig_surf, (40, 40))
            icon.draw()

        # 左上角显示生命
        for i in range(player_lives):
            life_icon = Actor('bat', center=(50 + i * 80, 25))
            life_icon.draw()

        # 左下角显示金币数
        coin_icon = Actor('coin', center=(70, HEIGHT - 25))
        coin_icon.draw()
        screen.draw.text(f" X {collected_coins}", midleft=(90, HEIGHT - 25), fontsize=50, color="gold", fontname="s")

    elif game_state == GameState.WIN:
        screen.fill((0, 0, 0))
        screen.draw.text('恭喜通关！', center=(WIDTH//2, HEIGHT//2), fontsize=100, color="yellow",fontname="s")

    # 始终绘制右上角退出按钮
    exit_button.draw()


# ---------------------------------------------------------
def update():  # 更新模块，每帧重复操作
    global player_frame_index, frame_count, game_state, current_level, player_lives, blood_pos, coin_positions, collected_coins
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

    # 玩家拾取血包
    player_x, player_y = get_player_position()
    if blood_pos:
        if abs(player_x - blood_pos[0]) < TILE_SIZE//2 and abs(player_y - blood_pos[1]) < TILE_SIZE//2:
            if player_lives < max_lives:
                player_lives += 1
            blood_pos = None

    # 玩家拾取金币
    new_coin_positions = []
    for pos in coin_positions:
        if abs(player_x - pos[0]) < TILE_SIZE//2 and abs(player_y - pos[1]) < TILE_SIZE//2:
            collected_coins += 1
        else:
            new_coin_positions.append(pos)
    coin_positions = new_coin_positions

    # 出口判定：判断玩家是否在出口格子上
    player_x, player_y = get_player_position()
    tiles = get_tiles()
    for tile in tiles:
        if hasattr(tile, 'char'):
            jump_dict = EXIT_JUMP.get(current_level + 1, {})
            if tile.char in jump_dict:
                if abs(player_x - tile.x) < 10 and abs(player_y - tile.y) < 10:
                    current_level = jump_dict[tile.char] - 1
                    load_level(current_level)
                    game_state = GameState.PLAYING
                    break

    player_x, player_y = get_player_position()
    for dragon in milk_dragons:
        if dragon.alive and abs(dragon.x - player_x) < TILE_SIZE//2 and abs(dragon.y - player_y) < TILE_SIZE//2:
            player_lives -= 1
            dragon.alive = False
            dragon.blowup_tick = 0
            if player_lives <= 0:
                game_state = GameState.GAME_OVER
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
