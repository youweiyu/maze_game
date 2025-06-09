from config import WIDTH, HEIGHT, TILE_SIZE, PLAYER_SPEED
from pgzero.builtins import Actor, keyboard
from map_loader import get_player_start, get_wall_positions
import pygame

player_frames_left = ['bat0', 'bat1', 'bat2', 'bat3', 'bat4']
player_frames_right = ['batr0', 'batr1', 'batr2', 'batr3', 'batr4']
player_frame_index = 0
player_direction = 'left'
player = None

PLAYER_SPEED = PLAYER_SPEED  # 玩家移动速度

# --------- 声波攻击相关 ---------
wave_active = False
wave_frame = 0
wave_actor = None
wave_direction = 'left'
wave_tick = 0  #用于控制声波推进速度
wave_max_range = 1  # 新增，最大攻击距离

def attack(wave_range=1):
    global wave_active, wave_frame, wave_direction, wave_max_range
    if not wave_active:
        wave_active = True
        wave_frame = 1
        wave_direction = player_direction
        wave_max_range = wave_range  # 记录本次攻击最大距离
        update_wave_actor()

def update_wave_actor():
    global wave_actor, wave_active, wave_frame
    dx, dy = 0, 0
    if wave_direction == 'right':
        dx = TILE_SIZE * 2/3 * wave_frame
    elif wave_direction == 'left':
        dx = -TILE_SIZE * 2/3 * wave_frame
    elif wave_direction == 'up':
        dy = -TILE_SIZE * 2/3 * wave_frame
    elif wave_direction == 'down':
        dy = TILE_SIZE * 2/3 * wave_frame
    px, py = player.x, player.y
    wave_x, wave_y = px + dx, py + dy

    # 检查声波是否碰到墙
    for wx, wy in get_wall_positions():
        if abs(wave_x - wx) < TILE_SIZE // 2 and abs(wave_y - wy) < TILE_SIZE // 2:
            wave_active = False
            wave_actor = None
            return

    wave_actor = Actor(f'wave{wave_frame}', center=(wave_x, wave_y))
    wave_actor.rect = pygame.Rect(wave_actor.x - TILE_SIZE//2, wave_actor.y - TILE_SIZE//2, TILE_SIZE, TILE_SIZE)
    # 旋转图片
    if wave_direction == 'left':
        wave_actor.angle = 0
    elif wave_direction == 'up':
        wave_actor.angle = 270
    elif wave_direction == 'right':
        wave_actor.angle = 180
    elif wave_direction == 'down':
        wave_actor.angle = 90

# 新增：多方向声波
multi_wave_active = False
multi_wave_dirs = []
multi_wave_frames = {}
multi_wave_ticks = {}
multi_wave_max_range = 1

def trigger_multi_wave(wave_range=1):
    global multi_wave_active, multi_wave_dirs, multi_wave_frames, multi_wave_ticks, multi_wave_max_range
    if not multi_wave_active:
        multi_wave_active = True
        multi_wave_dirs = ['left', 'right', 'up', 'down']
        multi_wave_frames = {d: 1 for d in multi_wave_dirs}
        multi_wave_ticks = {d: 0 for d in multi_wave_dirs}
        multi_wave_max_range = wave_range

def update_wave():
    global wave_active, wave_frame, wave_actor, wave_tick, wave_max_range
    global multi_wave_active, multi_wave_dirs, multi_wave_frames, multi_wave_ticks, multi_wave_max_range
    # 普通单方向声波
    if wave_active:
        wave_tick += 1
        if wave_tick >= 10:
            wave_frame += 1
            wave_tick = 0
            if wave_frame > wave_max_range:
                wave_active = False
                wave_actor = None
            else:
                update_wave_actor()
    # 多方向声波
    if multi_wave_active:
        finished = True
        for d in multi_wave_dirs:
            multi_wave_ticks[d] += 1
            if multi_wave_ticks[d] >= 10:
                multi_wave_frames[d] += 1
                multi_wave_ticks[d] = 0
            if multi_wave_frames[d] <= multi_wave_max_range:
                finished = False
        if finished:
            multi_wave_active = False

def get_wave_actor():
    # 返回单方向声波
    if wave_active:
        return wave_actor
    # 返回多方向声波的所有actor列表
    if multi_wave_active:
        actors = []
        px, py = player.x, player.y
        for d in multi_wave_dirs:
            frame = multi_wave_frames[d]
            if frame > multi_wave_max_range:
                continue
            dx, dy = 0, 0
            if d == 'right':
                dx = TILE_SIZE * 2/3 * frame
            elif d == 'left':
                dx = -TILE_SIZE * 2/3 * frame
            elif d == 'up':
                dy = -TILE_SIZE * 2/3 * frame
            elif d == 'down':
                dy = TILE_SIZE * 2/3 * frame
            wave_x, wave_y = px + dx, py + dy
            # 检查声波是否碰到墙
            hit_wall = False
            for wx, wy in get_wall_positions():
                if abs(wave_x - wx) < TILE_SIZE // 2 and abs(wave_y - wy) < TILE_SIZE // 2:
                    hit_wall = True
                    break
            if hit_wall:
                continue
            actor = Actor(f'wave{frame}', center=(wave_x, wave_y))
            actor.rect = pygame.Rect(actor.x - TILE_SIZE//2, actor.y - TILE_SIZE//2, TILE_SIZE, TILE_SIZE)
            # 旋转图片
            if d == 'left':
                actor.angle = 0
            elif d == 'up':
                actor.angle = 270
            elif d == 'right':
                actor.angle = 180
            elif d == 'down':
                actor.angle = 90
            actors.append(actor)
        return actors if actors else None
    return None

# --------- 玩家移动与动画 ---------
def init_player():
    global player, player_frame_index, player_direction
    player_frame_index = 0
    player_direction = 'left'
    player = Actor(player_frames_left[player_frame_index])
    player.pos = get_player_start()  # 每次初始化时获取最新起始位置

def can_move_to(x, y):
    # 检查目标点是否与任何墙壁重叠，判定略微放宽
    for wx, wy in get_wall_positions():
        if abs(x - wx) < TILE_SIZE - 15 and abs(y - wy) < TILE_SIZE - 15:
            return False
    return True

def update_player(frame_count):
    global player_frame_index, player_direction

    moved = False
    new_x, new_y = player.x, player.y

    # 同时支持方向键和WASD
    if keyboard.left or keyboard.a:
        new_x -= PLAYER_SPEED
        player_direction = 'left'
        moved = True
    if keyboard.right or keyboard.d:
        new_x += PLAYER_SPEED
        player_direction = 'right'
        moved = True
    if keyboard.up or keyboard.w:
        new_y -= PLAYER_SPEED
        player_direction = 'up'
        moved = True
    if keyboard.down or keyboard.s:
        new_y += PLAYER_SPEED
        player_direction = 'down'
        moved = True

    # 边界限制
    new_x = max(0, min(WIDTH, new_x))
    new_y = max(0, min(HEIGHT, new_y))

    # 碰撞检测
    if can_move_to(new_x, new_y):
        player.x = new_x
        player.y = new_y

    # 每 5 帧更新一次动画（仅在移动时）
    if moved and frame_count % 5 == 0:
        player_frame_index = (player_frame_index + 1) % len(player_frames_left)
        if player_direction == 'left':
            player.image = player_frames_left[player_frame_index]
        else:
            player.image = player_frames_right[player_frame_index]
    else:
        # 保证静止时朝向正确
        if player_direction == 'left':
            player.image = player_frames_left[player_frame_index]
        else:
            player.image = player_frames_right[player_frame_index]

def draw_player():
    player.draw()
    # 绘制声波
    if wave_active and wave_actor:
        wave_actor.draw()
    # 新增：绘制多方向声波
    if multi_wave_active:
        actors = get_wave_actor()
        if actors:
            for a in actors:
                a.draw()

def get_player_position():
    return player.x, player.y
