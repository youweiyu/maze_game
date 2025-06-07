import os
import sys
import time
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
from ghost import Ghost
from boss import Boss, update_boss, draw_boss, get_boss, reset_boss

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

levels = ['maps/map1.txt', 'maps/map2.txt', 'maps/map3.txt', 'maps/map4.txt', 'maps/map5.txt', 'maps/map6.txt', 'maps/boss.txt']
current_level = 0

player_lives = 3  # 初始三条命
max_lives = 5     # 生命上限
blood_pos = None  # 当前关卡的血包位置
coin_positions = []  # 当前关卡金币位置列表
collected_coins = 0  # 总金币数
wave_range = 1  # 声波攻击距离，初始为1，最大4
bat_wave_pos = None  # 当前关卡bat_wave道具位置
ghost = None  # 新增：鬼魂对象
player_attack_damage = 5  # 玩家攻击伤害

win_time = None  # 记录胜利/失败时刻
lose_time = None

def load_level(level_index):
    global blood_pos, coin_positions, bat_wave_pos, ghost
    load_map(levels[level_index])
    init_player()
    if level_index == 6:  # boss关卡
        reset_boss()
        # boss出生在地图中心
        blood_pos = None
        coin_positions.clear()
        bat_wave_pos = None
        ghost = None
    else:
        spawn_dragons(n=10)
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

        # 随机生成一个bat_wave道具
        if walkable_tiles:
            bat_wave_tile = random.choice(walkable_tiles)
            bat_wave_pos = (bat_wave_tile.x, bat_wave_tile.y)
        else:
            bat_wave_pos = None

        # 生成鬼魂
        ghost = Ghost(get_player_position())

def draw():
    global game_state, current_level, player_lives, blood_pos, coin_positions, collected_coins, bat_wave_pos
    screen.clear()
    if game_state == GameState.START:
        draw_start_screen(screen)
    elif game_state == GameState.PLAYING:
        screen.fill((255, 255, 255))
        draw_map()
        # 先绘制血包、bat_wave和金币
        if blood_pos:
            blood_actor = Actor('blood', center=blood_pos)
            blood_actor.draw()
        if bat_wave_pos:
            bat_wave_actor = Actor('bat_wave', center=bat_wave_pos)
            bat_wave_actor.draw()
        for pos in coin_positions:
            coin_actor = Actor('coin', center=pos)
            coin_actor.draw()
        draw_player()
        draw_dragons()
        # 绘制鬼魂
        if ghost and ghost.alive != 'remove':
            ghost.draw()
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

        if current_level == 6:
            draw_boss(screen)
            # boss血条
            boss = get_boss()
            if boss:
                bar_w = 600
                bar_h = 30
                bar_x = WIDTH // 2 - bar_w // 2
                bar_y = HEIGHT - 80
                pygame.draw.rect(screen.surface, (80, 80, 80), (bar_x, bar_y, bar_w, bar_h), border_radius=10)
                hp = max(0, boss.hp)
                hp_w = int(bar_w * hp / boss.max_hp)
                pygame.draw.rect(screen.surface, (255, 0, 0), (bar_x, bar_y, hp_w, bar_h), border_radius=10)
                screen.draw.text(f"Boss HP: {hp}", center=(WIDTH//2, bar_y + bar_h//2), fontsize=32, color="white")

    elif game_state == GameState.WIN:
        bg = Actor('start_bk', center=(WIDTH//2, HEIGHT//2))
        bg.draw()
        win_img = Actor('youwin', center=(WIDTH//2, HEIGHT//2))
        win_img.draw()
    elif game_state == GameState.GAME_OVER:
        screen.fill((0, 0, 0))
        screen.draw.text('You Lose!', center=(WIDTH//2, HEIGHT//2), fontsize=100, color="red", fontname="s")

    # 始终绘制右上角退出按钮
    exit_button.draw()


# ---------------------------------------------------------
def update():  # 更新模块，每帧重复操作
    global player_frame_index, frame_count, game_state, current_level, player_lives, blood_pos, coin_positions, collected_coins, bat_wave_pos, wave_range, ghost
    global win_time, lose_time
    milk_dragons = get_milk_dragons()
    if game_state == GameState.START:
        win_time = None
        lose_time = None
        return
    if game_state == GameState.WIN:
        if win_time is None:
            win_time = time.time()
        elif time.time() - win_time > 5:
            game_state = GameState.START
            win_time = None
        return
    if game_state == GameState.GAME_OVER:
        if lose_time is None:
            lose_time = time.time()
        elif time.time() - lose_time > 5:
            game_state = GameState.START
            lose_time = None
        return
    frame_count += 1
    update_player(frame_count)
    update_wave()
    update_dragons(frame_count)
    # 更新鬼魂
    if ghost and ghost.alive != 'remove':
        ghost.update(get_player_position())

    if current_level == 6:
        update_boss(frame_count, get_player_position())
        boss = get_boss()
        # 冲击波攻击boss
        wave = get_wave_actor()
        if boss and wave and boss.alive:
            # 增加受击冷却，防止一次攻击掉多次血
            if not getattr(boss, 'hit_cooldown', 0):
                if wave.colliderect(boss.actor):
                    boss.hp -= player_attack_damage
                    boss.hit_cooldown = 15  # 10帧内不能再次受击
                    if boss.hp <= 0:
                        boss.alive = False
                        game_state = GameState.WIN
            else:
                boss.hit_cooldown -= 1
        # 冲击波攻击boss召唤的ghost
        if boss:
            for g in boss.ghosts:
                if g.alive and wave and wave.colliderect(g.actor):
                    g.alive = False
                    g.blowup_tick = 0
        # 玩家碰撞fireball
        if boss:
            for fb in boss.fireballs:
                if abs(fb.x - get_player_position()[0]) < TILE_SIZE//2 and abs(fb.y - get_player_position()[1]) < TILE_SIZE//2:
                    player_lives -= 1
                    boss.fireballs.remove(fb)
                    if player_lives <= 0:
                        game_state = GameState.GAME_OVER
        # 玩家碰撞ghost
        if boss:
            for g in boss.ghosts:
                if g.alive and abs(g.x - get_player_position()[0]) < TILE_SIZE//2 and abs(g.y - get_player_position()[1]) < TILE_SIZE//2:
                    player_lives -= 1
                    g.alive = False
                    g.blowup_tick = 0
                    if player_lives <= 0:
                        game_state = GameState.GAME_OVER
        # 玩家碰撞boss本体
        if boss and boss.alive:
            px, py = get_player_position()
            if abs(boss.x - px) < TILE_SIZE//2 and abs(boss.y - py) < TILE_SIZE//2:
                if not boss.blowup_show:  # 防止多次触发
                    player_lives -= 1
                    boss.hp -= 10
                    boss.blowup_show = True
                    boss.blowup_tick = 0
                    if player_lives <= 0:
                        game_state = GameState.GAME_OVER
                    if boss.hp <= 0:
                        boss.alive = False
                        game_state = GameState.WIN
        return

    # 冲击波攻击奶龙
    wave = get_wave_actor()
    if wave:
        for dragon in milk_dragons:
            if dragon.alive and wave.colliderect(dragon.actor):
                dragon.alive = False
                dragon.blowup_tick = 0
        # 鬼魂不会被攻击

    # 移除已爆炸完成的奶龙
    milk_dragons[:] = [d for d in milk_dragons if d.alive != 'remove']

    player_x, player_y = get_player_position()
    # 玩家拾取血包
    if blood_pos:
        if abs(player_x - blood_pos[0]) < TILE_SIZE//2 and abs(player_y - blood_pos[1]) < TILE_SIZE//2:
            if player_lives < max_lives:
                player_lives += 1
            blood_pos = None

    # 玩家拾取bat_wave道具
    if bat_wave_pos:
        if abs(player_x - bat_wave_pos[0]) < TILE_SIZE//2 and abs(player_y - bat_wave_pos[1]) < TILE_SIZE//2:
            if wave_range < 4:
                wave_range += 1
            bat_wave_pos = None

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

    # 玩家碰撞鬼魂
    if ghost and ghost.alive and ghost.alive != 'remove':
        px, py = get_player_position()
        if abs(ghost.x - px) < TILE_SIZE//2 and abs(ghost.y - py) < TILE_SIZE//2:
            player_lives -= 1
            ghost.alive = False
            ghost.blowup_tick = 0
            if player_lives <= 0:
                game_state = GameState.GAME_OVER

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

    # -----------测试阶段：点击顶部关卡图标切换关卡-----------
    icon_y = 25
    icon_size = 60
    gap = 30
    total_width = 6 * icon_size + 5 * gap
    start_x = WIDTH // 2 - total_width // 2 + icon_size // 2
    for i in range(6):
        icon_x = start_x + i * (icon_size + gap)
        # 以图标中心为圆心，半径30像素为点击区域
        if (pos[0] - icon_x) ** 2 + (pos[1] - icon_y) ** 2 < 30 ** 2:
            current_level = i
            load_level(current_level)
            game_state = GameState.PLAYING
            return
    # ------------------------------------------------------

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
        attack(wave_range)  # 传递当前wave_range

pgzrun.go()
