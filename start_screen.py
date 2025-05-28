from config import WIDTH, HEIGHT
from pgzero.builtins import Actor

background = Actor('start_bk', (WIDTH // 2, HEIGHT // 2))

# 按钮设置
button_pos = (WIDTH // 2, HEIGHT // 2 + 150)
cursor_pos = (WIDTH // 2, HEIGHT // 2 + 250)
start_button = Actor('start', center=button_pos)

def draw_start_screen(screen):
    background.draw()
    start_button.draw()

    cursor = Actor('cursor_click', center=cursor_pos)
    cursor.draw()
    screen.draw.text('幻 影 迷 宫', center=(WIDTH // 2, HEIGHT // 2 - 200), fontsize=120, color="white", fontname="s")

# def update_start_screen():
#     pass  # 暂时没有动画

# def handle_mouse_move(pos):
#     pass

def handle_start_click(pos):
    if start_button.collidepoint(pos):
        return True
    return False
