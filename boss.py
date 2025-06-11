from pgzero.builtins import Actor
from config import WIDTH, HEIGHT, TILE_SIZE
from ghost import Ghost
import pygame
import random
from sound_manager import play_sound

class Fireball:
    def __init__(self, x, y, dx, dy):
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy
        self.actor = Actor('fireball', center=(x, y))
        self.actor.rect = pygame.Rect(self.x - TILE_SIZE//2, self.y - TILE_SIZE//2, TILE_SIZE, TILE_SIZE)
        # 优化：火球角度严格朝向player
        import math
        angle = math.degrees(math.atan2(-dy, dx))
        self.actor.angle = angle
        self.blowup = False
        self.blowup_tick = 0
        self.flip_x = dx > 0
        self.sound_played = False

    def update(self):
        if self.blowup:
            self.blowup_tick += 1
            if self.blowup_tick > 10:
                self.to_remove = True
            return
        self.x += self.dx
        self.y += self.dy
        self.actor.pos = (self.x, self.y)
        self.actor.rect.topleft = (self.x - TILE_SIZE//2, self.y - TILE_SIZE//2)
        # 火球不能穿墙
        from map_loader import get_wall_positions
        for wx, wy in get_wall_positions():
            if abs(self.x - wx) < TILE_SIZE//2 and abs(self.y - wy) < TILE_SIZE//2:
                self.blowup = True
                self.blowup_tick = 0
                self.actor.image = 'blowup'
                play_sound("explosion")
                return

    def draw(self):
        if not self.sound_played and not self.blowup:
            play_sound("fireball")
            self.sound_played = True
        if self.blowup:
            self.actor.image = 'blowup'
        else:
            self.actor.image = 'fireball'
        if self.flip_x:
            self.actor._surf = pygame.transform.flip(self.actor._orig_surf, True, False)
        else:
            self.actor._surf = self.actor._orig_surf
        self.actor.draw()

def can_move_to(x, y):
    # 不能穿墙
    from map_loader import get_wall_positions
    for wx, wy in get_wall_positions():
        if abs(x - wx) < TILE_SIZE - 5 and abs(y - wy) < TILE_SIZE - 5:
            return False
    # 边界
    if not (TILE_SIZE//2 <= x <= WIDTH-TILE_SIZE//2 and TILE_SIZE//2 <= y <= HEIGHT-TILE_SIZE//2):
        return False
    return True

class Boss:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.actor = Actor('boss', center=(self.x, self.y))
        self.actor.rect = pygame.Rect(self.x - TILE_SIZE//2, self.y - TILE_SIZE//2, TILE_SIZE, TILE_SIZE)
        self.max_hp = 100
        self.hp = 100
        self.alive = True
        self.skill_tick = 0
        self.ghosts = []
        self.fireballs = []
        self.fireball_cd = 0
        self.ghost_cd = 0
        self.move_tick = 0
        self.move_dir = random.choice(['left', 'right', 'up', 'down'])
        self.blowup_tick = 0
        self.blowup_show = False
        self.hit_cooldown = 0  # 新增：受击冷却
        self.facing_right = False  # 新增：朝向

    def update(self, frame_count, player_pos):
        if not self.alive:
            return
        # 随机移动
        self.move_tick += 1
        speed = 2
        if self.move_tick > 30:
            self.move_dir = random.choice(['left', 'right', 'up', 'down'])
            self.move_tick = 0
        dx, dy = 0, 0
        if self.move_dir == 'left':
            dx = -speed
            self.facing_right = False  # 向左
        elif self.move_dir == 'right':
            dx = speed
            self.facing_right = True   # 向右
        elif self.move_dir == 'up':
            dy = -speed
        elif self.move_dir == 'down':
            dy = speed
        new_x = self.x + dx
        new_y = self.y + dy
        if can_move_to(new_x, new_y):
            self.x = new_x
            self.y = new_y
            self.actor.pos = (self.x, self.y)
            self.actor.rect.topleft = (self.x - TILE_SIZE//2, self.y - TILE_SIZE//2)
        else:
            self.move_dir = random.choice(['left', 'right', 'up', 'down'])
            self.move_tick = 0

        # 技能冷却
        self.skill_tick += 1
        # 召唤ghost
        if self.ghost_cd <= 0 and self.skill_tick % 120 == 0:
            # 让鬼魂从boss身上出来
            g = Ghost((self.x, self.y))
            g.x, g.y = self.x, self.y
            g.actor.pos = (self.x, self.y)
            g.actor.rect.topleft = (self.x - TILE_SIZE//2, self.y - TILE_SIZE//2)
            g.speed = 2
            g.alive = True
            self.ghosts.append(g)
            self.ghost_cd = 120
        else:
            self.ghost_cd = max(0, self.ghost_cd - 1)
        # 发射fireball
        if self.fireball_cd <= 0 and self.skill_tick % 60 == 0:
            px, py = player_pos
            dx = px - self.x
            dy = py - self.y
            dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
            speed_fb = 5
            # 优化：dx,dy严格指向player
            fb = Fireball(self.x, self.y, speed_fb * dx / dist, speed_fb * dy / dist)
            self.fireballs.append(fb)
            self.fireball_cd = 60
        else:
            self.fireball_cd = max(0, self.fireball_cd - 1)
        # 更新fireball
        for fb in self.fireballs[:]:
            fb.update()
            # 火球出界或被墙阻挡都移除
            if hasattr(fb, 'to_remove') and fb.to_remove:
                self.fireballs.remove(fb)
            elif not (0 <= fb.x <= WIDTH and 0 <= fb.y <= HEIGHT):
                self.fireballs.remove(fb)
        # 更新ghost
        for g in self.ghosts[:]:
            if g.alive == 'remove':
                self.ghosts.remove(g)
            else:
                g.update(player_pos)
        # blowup特效计时
        if self.blowup_show:
            self.blowup_tick += 1
            if self.blowup_tick > 15:
                self.blowup_show = False
                self.blowup_tick = 0
        # 受击冷却递减
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

    def draw(self, screen):
        if not self.alive:
            return
        if self.blowup_show:
            self.actor.image = 'boss_blowup'
            self.actor._surf = self.actor._orig_surf
        else:
            self.actor.image = 'boss'
            # 新增：向右时水平翻转
            if self.facing_right:
                self.actor._surf = pygame.transform.flip(self.actor._orig_surf, True, False)
            else:
                self.actor._surf = self.actor._orig_surf
        self.actor.draw()
        for g in self.ghosts:
            g.draw()
        for fb in self.fireballs:
            fb.draw()

_boss = None

def reset_boss():
    global _boss
    _boss = Boss()

def get_boss():
    return _boss

def update_boss(frame_count, player_pos):
    if _boss:
        _boss.update(frame_count, player_pos)

def draw_boss(screen):
    if _boss:
        _boss.draw(screen)
