from config import WIDTH, HEIGHT
from pgzero.builtins import Actor
from sound_manager import play_music
import pygame

background = Actor('start_bk', (WIDTH // 2, HEIGHT // 2))
intro = Actor('introduction', (70, 60))

# 按钮设置
button_pos = (WIDTH // 2, HEIGHT // 2 + 150)
cursor_pos = (WIDTH // 2, HEIGHT // 2 + 250)
start_button = Actor('start', center=button_pos)

def draw_start_screen(screen):
    # 确保主菜单音乐
    if not pygame.mixer.music.get_busy():
        play_music("menu")
    background.draw()
    start_button.draw()
    # 绘制intro图标
    intro.draw()

    # 绘制指向“玩法说明”图标的光标
    intro_cursor = Actor('cursor_click')
    intro_cursor.center = (intro.centerx + 90, intro.centery)
    intro_cursor.angle = 90
    intro_cursor.draw()

    # 指向开始按钮的光标 (原有的)
    cursor = Actor('cursor_click', center=cursor_pos)
    cursor.draw()
    # 五个字分别用不同颜色
    title = "幻影迷宫"
    colors = ["cyan", "magenta", "gold", "lime"]
    x0 = WIDTH // 2 - 360
    y0 = HEIGHT // 2 - 200
    for i, (char, color) in enumerate(zip(title, colors)):
        screen.draw.text(char, center=(x0 + i * 240, y0), fontsize=120, color=color, fontname="s")

def draw_intro_screen(screen):
    # 玩法说明界面
    background.draw()
    # 标题
    screen.draw.text("玩法说明", center=(WIDTH//2, 100), fontsize=90, color="cyan", fontname="s")
    # 说明内容（分点多色）
    tips = [
        ("1. 方向键/WASD控制角色移动", "lime"),
        ("2. 空格键释放声波攻击，攻击距离可提升", "gold"),
        ("3. J键释放大招（八方向AOE）", "magenta"),
        ("4. 按1可购买提升攻击力（单剑）/按2购买充能大招（双剑）", "orange"),
        ("5. 拾取血包可恢复生命，拾取蝙蝠提升攻击距离", "deepskyblue"),
        ("6. 迷宫共六面，寻找到钥匙后可打开Boss关的大门", "violet"),
        ("7. 躲避奶龙、鬼魂和Boss火球，生命归零游戏失败", "red"),
        ("8. 打败Boss获得胜利！", "yellow"),
        ("按空格键返回主界面", "white"),
    ]
    y = 200
    for tip, color in tips:
        screen.draw.text(tip, center=(WIDTH//2, y), fontsize=48, color=color, fontname="s")
        y += 65

def handle_start_click(pos):
    if start_button.collidepoint(pos):
        return "start"
    # 检查intro图标
    if intro.collidepoint(pos):
        return "intro"
    return None
