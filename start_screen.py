from config import WIDTH, HEIGHT
from pgzero.builtins import Actor

background = Actor('start_bk', (WIDTH // 2, HEIGHT // 2))

# 按钮设置
button_pos = (WIDTH // 2, HEIGHT // 2 + 100)
start_button = Actor('start_no', center=button_pos)

def draw_start_screen(screen):
    background.draw()
    start_button.draw()
    screen.draw.text('幻影迷宫', center=(WIDTH // 2, HEIGHT // 2 - 150), fontsize=60, color="white",fontname="s")

# def update_start_screen():
#     pass  # 暂时没有动画

def handle_mouse_move(pos):
    if start_button.collidepoint(pos):
        start_button.image = 'start_yes'
    else:
        start_button.image = 'start_no'

def handle_start_click(pos):
    if start_button.collidepoint(pos):
        return True
    return False
