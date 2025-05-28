from config import WIDTH, HEIGHT, TILE_SIZE
from pgzero.builtins import Actor, keyboard
from map_loader import get_player_start, get_wall_positions

player_frames_left = ['bat0', 'bat1', 'bat2', 'bat3', 'bat4']
player_frames_right = ['batr0', 'batr1', 'batr2', 'batr3', 'batr4']
player_frame_index = 0
player_direction = 'left'
player = None

PLAYER_SPEED = 4

def init_player():
    global player, player_frame_index, player_direction
    player_frame_index = 0
    player_direction = 'left'
    player = Actor(player_frames_left[player_frame_index])
    player.pos = get_player_start()  # 每次初始化时获取最新起始位置

def can_move_to(x, y):
    # 检查目标点是否与任何墙壁重叠
    for wx, wy in get_wall_positions():
        if abs(x - wx) < TILE_SIZE - 5 and abs(y - wy) < TILE_SIZE - 5:
            return False
    return True

def update_player(frame_count):
    global player_frame_index, player_direction

    moved = False
    new_x, new_y = player.x, player.y

    if keyboard.left:
        new_x -= PLAYER_SPEED
        player_direction = 'left'
        moved = True
    if keyboard.right:
        new_x += PLAYER_SPEED
        player_direction = 'right'
        moved = True
    if keyboard.up:
        new_y -= PLAYER_SPEED
        moved = True
    if keyboard.down:
        new_y += PLAYER_SPEED
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

def get_player_position():
    return player.x, player.y
