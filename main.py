import os
import sys
import time
import random
import pgzrun
import pgzero, pygame
from pgzero.builtins import Actor, keys
from pgzero.loaders import sounds
screen : pgzero.screen.Screen

from config import WIDTH, HEIGHT, game_state, GameState, EXIT_JUMP, TILE_SIZE
from start_screen import draw_start_screen, handle_start_click, draw_intro_screen
from player import update_player, draw_player, init_player, get_player_position, attack, update_wave, get_wave_actor, trigger_multi_wave
from map_loader import load_map, draw_map, get_tiles
from milk_dragon import spawn_dragons, update_dragons, draw_dragons, get_milk_dragons, milk_dragons
from ghost import Ghost
from boss import update_boss, draw_boss, get_boss, reset_boss

os.environ['SDL_VIDEO_CENTERED'] = '1'

TITLE = '幻影迷宫'
WIDTH = WIDTH
HEIGHT = HEIGHT
clock = pygame.time.Clock()

game_state = game_state
frame_count = 0  # 帧计数器

# sounds. game_music.play(-1)  # 循环播放背景音乐

EXIT_BUTTON_POS = (WIDTH - 60, 25)
exit_button = Actor('exit', center=EXIT_BUTTON_POS)

# 新增暂停按钮
STOP_BTN_POS = (WIDTH - 180, 25)
stop_btn = Actor('stop', center=STOP_BTN_POS)

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
player_attack_damage = 1  # 玩家攻击伤害

win_time = None  # 记录胜利/失败时刻
lose_time = None

# 新增：用于记录每关道具生成状态
level_item_cache = {}
ghost_hurt_cooldown = 0  # 新增：鬼魂碰撞冷却
key_pos = None  # 钥匙位置
has_key = False  # 是否已获得钥匙

# 新增：攻击按钮和大招按钮
ATTACK_BTN_POS = (25, 160)
POWER_BTN_POS = (25, 320)
attack_btn = Actor('attack', center=ATTACK_BTN_POS)
power_btn = Actor('power', center=POWER_BTN_POS)
power_ready = False  # 是否可以释放大招

# 新增：攻击力购买状态和等级
attack_bought = False
attack_level = 1
attack_show_tick = 0  # “已购买”提示计时

# 新增：大招购买状态和次数
power_bought = False
power_count = 0
power_show_tick = 0  # “已购买”提示计时

player_invincible_tick = 0  # 新增：玩家无敌帧计数

def reset_game_state():
    global player_lives, collected_coins, wave_range, current_level, blood_pos, coin_positions, bat_wave_pos, ghost, ghost_hurt_cooldown
    global key_pos, has_key, level_item_cache, power_bought, attack_bought, player_attack_damage, attack_level, attack_show_tick, power_count, power_show_tick
    player_lives = 3
    collected_coins = 0
    wave_range = 1
    current_level = 0
    blood_pos = None
    coin_positions.clear()
    bat_wave_pos = None
    ghost = None
    key_pos = None
    has_key = False
    level_item_cache.clear()
    milk_dragons = get_milk_dragons()
    milk_dragons.clear()
    reset_boss()
    ghost_hurt_cooldown = 0
    power_bought = False
    attack_bought = False
    player_attack_damage = 1
    attack_level = 1
    attack_show_tick = 0
    power_count = 0
    power_show_tick = 0

def load_level(level_index):
    global blood_pos, coin_positions, bat_wave_pos, ghost, key_pos, level_item_cache
    load_map(levels[level_index])
    if level_index == 6:  # boss关卡
        milk_dragons.clear()
        reset_boss()
        blood_pos = None
        coin_positions.clear()
        bat_wave_pos = None
        ghost = None
        key_pos = None
        init_player()
    else:
        # --------- 只生成一次道具，缓存到level_item_cache ----------
        if level_index not in level_item_cache:
            tiles = get_tiles()
            walkable_tiles = [t for t in tiles if hasattr(t, 'char') and t.char in ('G', 'Y', 'I')]
            # 随机生成一个血包
            if walkable_tiles:
                blood_tile = random.choice(walkable_tiles)
                _blood_pos = (blood_tile.x, blood_tile.y)
            else:
                _blood_pos = None
            # 随机生成10个金币
            _coin_positions = []
            if walkable_tiles:
                coin_tiles = random.sample(walkable_tiles, min(15, len(walkable_tiles)))
                for t in coin_tiles:
                    _coin_positions.append((t.x, t.y))
            # 随机生成一个bat_wave道具
            if walkable_tiles:
                bat_wave_tile = random.choice(walkable_tiles)
                _bat_wave_pos = (bat_wave_tile.x, bat_wave_tile.y)
            else:
                _bat_wave_pos = None
            # 钥匙位置直接取地图中k字符
            key_tile = next((t for t in tiles if hasattr(t, 'char') and t.char == 'k'), None)
            _key_pos = (key_tile.x, key_tile.y) if key_tile else None
            # 存储副本，避免引用同一个对象
            level_item_cache[level_index] = {
                'blood_pos': _blood_pos,
                'coin_positions': list(_coin_positions),
                'bat_wave_pos': _bat_wave_pos,
                'key_pos': _key_pos
            }
        # 读取缓存（只生成一次道具）
        item = level_item_cache[level_index]
        # 关键：每次进入关卡都要拷贝一份道具状态，不能直接引用缓存
        blood_pos = item['blood_pos']
        coin_positions.clear()
        coin_positions.extend(item['coin_positions'])
        bat_wave_pos = item['bat_wave_pos']
        key_pos = item.get('key_pos', None)
        init_player()
        ghost = Ghost(get_player_position())
        spawn_dragons(n=10)

def draw():
    global game_state, current_level, player_lives, blood_pos, coin_positions, collected_coins, bat_wave_pos, key_pos, has_key
    global power_bought, attack_bought, attack_level, attack_show_tick, power_count, power_show_tick
    screen.clear()
    if game_state == GameState.START:
        draw_start_screen(screen)
    elif getattr(GameState, "INTRO", None) and game_state == GameState.INTRO:
        draw_intro_screen(screen)
    elif getattr(GameState, "PAUSE", None) and game_state == GameState.PAUSE:
        # 暂停时先绘制游戏画面
        screen.fill((255, 255, 255))
        draw_map()
        if blood_pos:
            blood_actor = Actor('blood', center=blood_pos)
            blood_actor.draw()
        if bat_wave_pos:
            bat_wave_actor = Actor('bat_wave', center=bat_wave_pos)
            bat_wave_actor.draw()
        if key_pos and not has_key:
            key_actor = Actor('key', center=key_pos)
            key_actor.draw()
        for pos in coin_positions:
            coin_actor = Actor('coin', center=pos)
            coin_actor.draw()
        tiles = get_tiles()
        for tile in tiles:
            if hasattr(tile, 'char') and tile.char == 'f':
                door_img = 'ice_out_open' if has_key else 'ice_out_close'
                door_actor = Actor(door_img, center=(tile.x, tile.y))
                door_actor.draw()
        draw_player()
        if current_level != 6:
            draw_dragons()
        if ghost and ghost.alive != 'remove':
            ghost.draw()
        icon_y = 25
        icon_size = 60
        gap = 30
        total_width = 6 * icon_size + 5 * gap
        start_x = WIDTH // 2 - total_width // 2 + icon_size // 2
        for i in range(6):
            icon_name = f"side{i+1}"
            icon_x = start_x + i * (icon_size + gap)
            if current_level == i:
                icon = Actor(icon_name, center=(icon_x, icon_y))
            else:
                icon = Actor(icon_name, center=(icon_x, icon_y))
                icon._surf = pygame.transform.smoothscale(icon._orig_surf, (40, 40))
            icon.draw()
        for i in range(player_lives):
            life_icon = Actor('bat', center=(50 + i * 80, 25))
            life_icon.draw()
        coin_icon = Actor('coin', center=(70, HEIGHT - 25))
        coin_icon.draw()
        screen.draw.text(f" X {collected_coins}", midleft=(90, HEIGHT - 25), fontsize=50, color="gold", fontname="s")
        if current_level == 6:
            draw_boss(screen)
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
        screen.draw.text("消耗5", center=(ATTACK_BTN_POS[0], ATTACK_BTN_POS[1]-50), fontsize=17, color="gold", fontname="s")
        screen.draw.text("消耗5", center=(POWER_BTN_POS[0], POWER_BTN_POS[1]-50), fontsize=17, color="gold", fontname="s")
        attack_btn.draw()
        power_btn.draw()
        screen.draw.text(f"Lv.{attack_level}", center=(ATTACK_BTN_POS[0], ATTACK_BTN_POS[1]+45), fontsize=28, color="gold", fontname="s")
        screen.draw.text(f"{power_count}", center=(POWER_BTN_POS[0], POWER_BTN_POS[1]+45), fontsize=28, color="gold", fontname="s")
        screen.draw.text("J释放", center=(POWER_BTN_POS[0], POWER_BTN_POS[1]+80), fontsize=24, color="gold", fontname="s")
        if attack_show_tick > 0:
            screen.draw.text("已购买", center=(ATTACK_BTN_POS[0]+80, ATTACK_BTN_POS[1]), fontsize=32, color="#1a67aa", fontname="s")
        if power_show_tick > 0:
            screen.draw.text("已购买", center=(POWER_BTN_POS[0]+80, POWER_BTN_POS[1]), fontsize=32, color="#1a67aa", fontname="s")
        # 在游戏画面上覆盖暂停提示
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 120))  # 半透明黑色遮罩
        screen.surface.blit(s, (0, 0))
        screen.draw.text("游戏已暂停", center=(WIDTH//2, HEIGHT//2-40), fontsize=80, color="yellow", fontname="s")
        screen.draw.text("按空格键继续游戏", center=(WIDTH//2, HEIGHT//2+40), fontsize=50, color="white", fontname="s")
    elif game_state == GameState.PLAYING:
        screen.fill((255, 255, 255))
        # 1. 先绘制地图底层
        draw_map()
        # 2. 再绘制血包、bat_wave、钥匙、金币
        if blood_pos:
            blood_actor = Actor('blood', center=blood_pos)
            blood_actor.draw()
        if bat_wave_pos:
            bat_wave_actor = Actor('bat_wave', center=bat_wave_pos)
            bat_wave_actor.draw()
        if key_pos and not has_key:
            key_actor = Actor('key', center=key_pos)
            key_actor.draw()
        for pos in coin_positions:
            coin_actor = Actor('coin', center=pos)
            coin_actor.draw()
        # 3. 再绘制门（f门），保证门在底层
        tiles = get_tiles()
        for tile in tiles:
            if hasattr(tile, 'char') and tile.char == 'f':
                door_img = 'ice_out_open' if has_key else 'ice_out_close'
                door_actor = Actor(door_img, center=(tile.x, tile.y))
                door_actor.draw()
        # 4. 再绘制人物、奶龙、鬼魂等
        draw_player()
        if current_level != 6:
            draw_dragons()
        if ghost and ghost.alive != 'remove':
            ghost.draw()
        # 5. 顶部UI等
        icon_y = 25
        icon_size = 60
        gap = 30
        total_width = 6 * icon_size + 5 * gap
        start_x = WIDTH // 2 - total_width // 2 + icon_size // 2
        for i in range(6):
            icon_name = f"side{i+1}"
            icon_x = start_x + i * (icon_size + gap)
            if current_level == i:
                icon = Actor(icon_name, center=(icon_x, icon_y))
            else:
                icon = Actor(icon_name, center=(icon_x, icon_y))
                icon._surf = pygame.transform.smoothscale(icon._orig_surf, (40, 40))
            icon.draw()
        for i in range(player_lives):
            life_icon = Actor('bat', center=(50 + i * 80, 25))
            life_icon.draw()
        coin_icon = Actor('coin', center=(70, HEIGHT - 25))
        coin_icon.draw()
        screen.draw.text(f" X {collected_coins}", midleft=(90, HEIGHT - 25), fontsize=50, color="gold", fontname="s")
        if current_level == 6:
            draw_boss(screen)
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
        # 左侧按钮
        # “消耗5”/“消耗20”一行，字体小一点
        screen.draw.text("消耗5", center=(ATTACK_BTN_POS[0], ATTACK_BTN_POS[1]-50), fontsize=17, color="gold", fontname="s")
        screen.draw.text("消耗5", center=(POWER_BTN_POS[0], POWER_BTN_POS[1]-50), fontsize=17, color="gold", fontname="s")
        attack_btn.draw()
        power_btn.draw()
        # 攻击力等级
        screen.draw.text(f"Lv.{attack_level}", center=(ATTACK_BTN_POS[0], ATTACK_BTN_POS[1]+45), fontsize=28, color="gold", fontname="s")
        # 大招次数和提示
        screen.draw.text(f"{power_count}", center=(POWER_BTN_POS[0], POWER_BTN_POS[1]+45), fontsize=28, color="gold", fontname="s")
        screen.draw.text("J释放", center=(POWER_BTN_POS[0], POWER_BTN_POS[1]+80), fontsize=24, color="gold", fontname="s")
        # “已购买”蓝色提示，出现一会儿后消失
        if attack_show_tick > 0:
            screen.draw.text("已购买", center=(ATTACK_BTN_POS[0]+80, ATTACK_BTN_POS[1]), fontsize=32, color="#1a67aa", fontname="s")
        if power_show_tick > 0:
            screen.draw.text("已购买", center=(POWER_BTN_POS[0]+80, POWER_BTN_POS[1]), fontsize=32, color="#1a67aa", fontname="s")
    elif game_state == GameState.WIN:
        bg = Actor('start_bk', center=(WIDTH//2, HEIGHT//2))
        bg.draw()
        win_img = Actor('youwin', center=(WIDTH//2, HEIGHT//2))
        win_img.draw()
        # 新增：胜利时提示
        screen.draw.text("按空格键返回主界面", center=(WIDTH//2, HEIGHT//2+200), fontsize=60, color="white", fontname="s")
    elif game_state == GameState.GAME_OVER:
        screen.fill((0, 0, 0))
        bg = Actor('start_bk', center=(WIDTH//2, HEIGHT//2))
        bg.draw()
        screen.draw.text('You Lose!', center=(WIDTH//2, HEIGHT//2), fontsize=100, color="red", fontname="s")
        # 新增：失败时提示
        screen.draw.text("按空格键返回主界面", center=(WIDTH//2, HEIGHT//2+120), fontsize=60, color="white", fontname="s")

    # 始终绘制右上角退出按钮和暂停按钮
    exit_button.draw()
    stop_btn.draw()


# ---------------------------------------------------------
def update():  # 更新模块，每帧重复操作
    global player_frame_index, frame_count, game_state, current_level, player_lives, blood_pos, coin_positions, collected_coins, bat_wave_pos, wave_range, ghost, ghost_hurt_cooldown
    global win_time, lose_time, key_pos, has_key, attack_show_tick, power_show_tick
    global player_invincible_tick

    # 1. 先处理游戏状态（START/WIN/GAME_OVER/INTRO/PAUSE），如需 return 则直接返回
    if game_state == GameState.START:
        win_time = None
        lose_time = None
        reset_game_state()
        return
    if getattr(GameState, "INTRO", None) and game_state == GameState.INTRO:
        return
    if getattr(GameState, "PAUSE", None) and game_state == GameState.PAUSE:
        return
    # 修改：WIN和GAME_OVER状态下不再自动返回主界面
    if game_state == GameState.WIN:
        return
    if game_state == GameState.GAME_OVER:
        return

    # 2. 递增帧数，更新玩家、声波、怪物、鬼魂
    frame_count += 1
    update_player(frame_count)
    update_wave()
    if current_level != 6:
        update_dragons(frame_count)
    if ghost and ghost.alive != 'remove':
        ghost.update(get_player_position())

    # 新增：已购买提示倒计时
    if attack_show_tick > 0:
        attack_show_tick -= 1
    if power_show_tick > 0:
        power_show_tick -= 1

    # 新增：无敌帧倒计时
    if player_invincible_tick > 0:
        player_invincible_tick -= 1

    # 3. boss关卡判定
    if current_level == 6:
        update_boss(frame_count, get_player_position())
        boss = get_boss()
        wave = get_wave_actor()
        if boss and wave and boss.alive:
            bx, by = boss.x, boss.y
            # 修复：支持wave为list和单个actor
            if boss.hit_cooldown <= 0:
                hit = False
                if isinstance(wave, list):
                    for w in wave:
                        if ((w.x - bx) ** 2 + (w.y - by) ** 2) ** 0.5 < 3 * TILE_SIZE:
                            hit = True
                            break
                else:
                    if ((wave.x - bx) ** 2 + (wave.y - by) ** 2) ** 0.5 < 3 * TILE_SIZE:
                        hit = True
                if hit:
                    boss.hp -= player_attack_damage
                    boss.hit_cooldown = 25
                    if boss.hp <= 0:
                        boss.alive = False
                        game_state = GameState.WIN
            else:
                boss.hit_cooldown -= 1
        if boss:
            for g in boss.ghosts:
                # 修复：支持wave为list和单个actor
                if g.alive and wave:
                    if isinstance(wave, list):
                        for w in wave:
                            if w.colliderect(g.actor):
                                g.alive = False
                                g.blowup_tick = 0
                                break
                    else:
                        if wave.colliderect(g.actor):
                            g.alive = False
                            g.blowup_tick = 0
        if boss:
            for fb in boss.fireballs:
                # 只在火球未爆炸时判定伤害
                if not getattr(fb, 'blowup', False):
                    if abs(fb.x - get_player_position()[0]) < TILE_SIZE//2 and abs(fb.y - get_player_position()[1]) < TILE_SIZE//2:
                        player_lives -= 1
                        # 新增：火球爆炸特效
                        fb.blowup = True
                        fb.blowup_tick = 0
                        # boss.fireballs.remove(fb)  # 不要立即移除，等爆炸动画
                        if player_lives <= 0:
                            game_state = GameState.GAME_OVER
        if boss:
            for g in boss.ghosts:
                if g.alive and abs(g.x - get_player_position()[0]) < TILE_SIZE//2 and abs(g.y - get_player_position()[1]) < TILE_SIZE//2:
                    player_lives -= 1
                    g.alive = False
                    g.blowup_tick = 0
                    if player_lives <= 0:
                        game_state = GameState.GAME_OVER
        # 玩家碰到boss掉血并显示爆炸特效（扩大判定范围）
        if boss and boss.alive and not boss.blowup_show:
            px, py = get_player_position()
            # 判定范围扩大到TILE_SIZE
            if player_invincible_tick == 0 and abs(boss.x - px) < 2.5 * TILE_SIZE and abs(boss.y - py) < 2.5 * TILE_SIZE:
                player_lives -= 1
                boss.hp -= 10
                boss.blowup_show = True
                boss.blowup_tick = 0
                # 新增：玩家爆炸特效
                if not hasattr(boss, 'player_blowup_tick'):
                    boss.player_blowup_tick = 0
                boss.player_blowup_tick = 15  # 显示15帧
                player_invincible_tick = 120  # 2秒无敌
                if player_lives <= 0:
                    game_state = GameState.GAME_OVER
                if boss.hp <= 0:
                    boss.alive = False
                    game_state = GameState.WIN
        return

    # 4. 普通关卡判定
    # 玩家拾取血包
    player_x, player_y = get_player_position()
    if blood_pos:
        if abs(player_x - blood_pos[0]) < TILE_SIZE//2 and abs(player_y - blood_pos[1]) < TILE_SIZE//2:
            if player_lives < max_lives:
                player_lives += 1
            # 关键：同步缓存，防止再次进入关卡血包又出现
            for k, v in level_item_cache.items():
                if v['blood_pos'] == blood_pos:
                    v['blood_pos'] = None
            blood_pos = None

    # 玩家拾取bat_wave道具
    if bat_wave_pos:
        if abs(player_x - bat_wave_pos[0]) < TILE_SIZE//2 and abs(player_y - bat_wave_pos[1]) < TILE_SIZE//2:
            if wave_range < 4:
                wave_range += 1
            for k, v in level_item_cache.items():
                if v['bat_wave_pos'] == bat_wave_pos:
                    v['bat_wave_pos'] = None
            bat_wave_pos = None

    # 玩家拾取钥匙
    if key_pos and not has_key:
        if abs(player_x - key_pos[0]) < TILE_SIZE//2 and abs(player_y - key_pos[1]) < TILE_SIZE//2:
            has_key = True
            for k, v in level_item_cache.items():
                if v['key_pos'] == key_pos:
                    v['key_pos'] = None
            key_pos = None

    # 玩家拾取金币
    new_coin_positions = []
    for pos in coin_positions:
        if abs(player_x - pos[0]) < TILE_SIZE//2 and abs(player_y - pos[1]) < TILE_SIZE//2:
            collected_coins += 1
            # 关键：同步缓存，防止再次进入关卡金币又出现
            for k, v in level_item_cache.items():
                if pos in v['coin_positions']:
                    v['coin_positions'].remove(pos)
        else:
            new_coin_positions.append(pos)
    coin_positions = new_coin_positions

    # 出口判定
    tiles = get_tiles()
    for tile in tiles:
        if hasattr(tile, 'char'):
            jump_dict = EXIT_JUMP.get(current_level + 1, {})
            # 新增：boss关卡门需要钥匙
            if tile.char in jump_dict:
                # 判断是否为boss关卡入口
                is_boss_entry = (jump_dict[tile.char] - 1 == 6)
                if abs(player_x - tile.x) < 10 and abs(player_y - tile.y) < 10:
                    if is_boss_entry and not has_key:
                        # 没有钥匙不能进boss关卡
                        continue
                    current_level = jump_dict[tile.char] - 1
                    load_level(current_level)
                    game_state = GameState.PLAYING
                    break

    # 声波攻击奶龙（修正判定，确保用rect）
    wave = get_wave_actor()
    milk_dragons = get_milk_dragons()
    # 移除已爆炸完成的奶龙
    milk_dragons[:] = [d for d in milk_dragons if d.alive != 'remove']
    # 支持多方向声波
    if wave:
        if isinstance(wave, list):
            for dragon in milk_dragons:
                if dragon.alive and hasattr(dragon.actor, 'rect'):
                    for w in wave:
                        if hasattr(w, 'rect') and w.rect.colliderect(dragon.actor.rect):
                            dragon.alive = False
                            dragon.blowup_tick = 0
                            break
        else:
            for dragon in milk_dragons:
                if dragon.alive and hasattr(dragon.actor, 'rect') and wave.rect.colliderect(dragon.actor.rect):
                    dragon.alive = False
                    dragon.blowup_tick = 0

    # 玩家碰撞奶龙
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
        if ghost_hurt_cooldown == 0 and abs(ghost.x - px) < TILE_SIZE//2 and abs(ghost.y - py) < TILE_SIZE//2:
            player_lives -= 1
            ghost.alive = False
            ghost.blowup_tick = 0
            ghost_hurt_cooldown = 30  # 0.5秒冷却（假设60fps）
            if player_lives <= 0:
                game_state = GameState.GAME_OVER
    if ghost_hurt_cooldown > 0:
        ghost_hurt_cooldown -= 1

    clock.tick(60)

# ---------------------------------------------------------
def on_mouse_move(pos, rel, buttons):  # 当鼠标移动时执行
    pass

# ---------------------------------------------------------
def on_mouse_down(pos, button):
    global game_state, current_level, collected_coins, power_bought, attack_bought, player_attack_damage, attack_level, attack_show_tick, power_count, power_show_tick
    # 检查是否点击退出按钮
    if exit_button.collidepoint(pos):
        sys.exit()
    # 检查是否点击暂停按钮
    if stop_btn.collidepoint(pos):
        if game_state == GameState.PLAYING:
            game_state = GameState.PAUSE
        return
    # 攻击按钮
    if attack_btn.collidepoint(pos):
        if collected_coins >= 5:
            collected_coins -= 5
            attack_bought = True
            attack_level += 1
            player_attack_damage += 0.5
            attack_show_tick = 60  # 显示1秒（假设60fps）
        return
    # 大招按钮
    if power_btn.collidepoint(pos):
        # 购买大招时消耗5金币，释放时不再消耗
        if not power_bought and collected_coins >= 5:
            collected_coins -= 5
            power_bought = True
            power_count += 1
            power_show_tick = 60
        elif power_bought:
            power_count += 1
            power_show_tick = 60
        return
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
        result = handle_start_click(pos)
        if result == "start":
            current_level = 0
            load_level(current_level)  # 加载地图
            game_state = GameState.PLAYING
        elif result == "intro":
            game_state = GameState.INTRO
        return
    # ---------------------------------------------------------

# ---------------------------------------------------------
def trigger_power():
    global power_count
    if not power_bought or power_count <= 0:
        return  # 未购买或无次数不能释放
    power_count -= 1
    # 普通关卡和boss关卡都触发八方向AOE
    trigger_multi_wave(wave_range)

def trigger_boss_wave():
    # boss关卡，j键/大招按钮触发八方向声波
    trigger_multi_wave(wave_range)

def on_key_down(key):
    global collected_coins, power_bought, power_count, current_level, game_state
    global win_time
    if game_state == GameState.PLAYING and key == keys.SPACE:
        attack(wave_range)
    # 按J释放大招（需有次数）
    if game_state == GameState.PLAYING and key == keys.J:
        if power_bought and power_count > 0:
            trigger_power()
    # 在玩法说明界面按空格返回主界面
    if getattr(GameState, "INTRO", None) and game_state == GameState.INTRO and key == keys.SPACE:
        game_state = GameState.START
    # 在暂停界面按空格恢复游戏
    if getattr(GameState, "PAUSE", None) and game_state == GameState.PAUSE and key == keys.SPACE:
        game_state = GameState.PLAYING
    # 在胜利或失败界面按空格返回主界面
    if game_state in (GameState.WIN, GameState.GAME_OVER) and key == keys.SPACE:
        game_state = GameState.START
    #---------------------------------------------------------------------------
    # 测试：按P直接进入boss关
    if key == keys.P:
        current_level = 6
        load_level(current_level)
        game_state = GameState.PLAYING
    # 测试：按O直接获胜
    if key == keys.O:
        game_state = GameState.WIN
        win_time = time.time()    

# 游戏启动--------------------------------------------------
pgzrun.go()
