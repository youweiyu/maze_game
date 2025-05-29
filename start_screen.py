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
    # 五个字分别用不同颜色
    title = "幻影迷宫"
    colors = ["cyan", "magenta", "gold", "lime"]
    x0 = WIDTH // 2 - 360
    y0 = HEIGHT // 2 - 200
    for i, (char, color) in enumerate(zip(title, colors)):
        screen.draw.text(char, center=(x0 + i * 240, y0), fontsize=120, color=color, fontname="s")

# def update_start_screen():
#     pass  # 暂时没有动画

# def handle_mouse_move(pos):
#     pass

def handle_start_click(pos):
    if start_button.collidepoint(pos):
        return True
    return False
