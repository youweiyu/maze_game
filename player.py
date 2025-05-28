from config import WIDTH, HEIGHT
from pgzero.builtins import Actor, keyboard
from map_loader import get_player_start

player_frames_left = ['bat0', 'bat1', 'bat2', 'bat3', 'bat4']
player_frames_right = ['batr0', 'batr1', 'batr2', 'batr3', 'batr4']
player_frame_index = 0
player_direction = 'left'  # 初始朝向
player = None  # 初始化为None

PLAYER_SPEED = 4

def init_player():
    global player, player_frame_index, player_direction
    player_frame_index = 0
    player_direction = 'left'
    player = Actor(player_frames_left[player_frame_index])
    player.pos = get_player_start()  # 每次初始化时获取最新起始位置

def update_player(frame_count):
    global player_frame_index, player_direction

    moved = False

    if keyboard.left:
        player.x -= PLAYER_SPEED
        moved = True
        player_direction = 'left'
    if keyboard.right:
        player.x += PLAYER_SPEED
        moved = True
        player_direction = 'right'
    if keyboard.up:
        player.y -= PLAYER_SPEED
        moved = True
    if keyboard.down:
        player.y += PLAYER_SPEED
        moved = True

    # 边界限制
    player.x = max(0, min(WIDTH, player.x))
    player.y = max(0, min(HEIGHT, player.y))

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
