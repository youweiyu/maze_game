from config import WIDTH, HEIGHT
from pgzero.builtins import Actor, keyboard
from map_loader import get_player_start

player_frames = ['bat0', 'bat1', 'bat2', 'bat3', 'bat4']
player_frame_index = 0
player = Actor(player_frames[player_frame_index])

player.pos = get_player_start()  # 从地图加载器获取玩家起始位置
PLAYER_SPEED = 4

def update_player(frame_count):
    global player_frame_index

    moved = False

    if keyboard.left:
        player.x -= PLAYER_SPEED
        moved = True
    if keyboard.right:
        player.x += PLAYER_SPEED
        moved = True
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
        player_frame_index = (player_frame_index + 1) % len(player_frames)
        player.image = player_frames[player_frame_index]

def draw_player():
    player.draw()
