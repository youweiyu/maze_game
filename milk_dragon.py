from pgzero.builtins import Actor
import random
from player import get_player_position
from map_loader import get_tiles
import pygame
from config import TILE_SIZE, Dragon_SPEED

WALK_FRAMES = [f'walk_{i}' for i in range(9)]
DRAGON_SPEED = Dragon_SPEED
TILE_SIZE = TILE_SIZE
milk_dragons = []

def can_move_to_strict(x, y):
    # 更严格的判定，中心点和墙中心距离需大于TILE_SIZE*0.8
    from map_loader import get_wall_positions
    for wx, wy in get_wall_positions():
        if abs(x - wx) < TILE_SIZE * 0.8 and abs(y - wy) < TILE_SIZE * 0.8:
            return False
    # 边界
    if not (TILE_SIZE//2 <= x <= 1500-TILE_SIZE//2 and TILE_SIZE//2 <= y <= 800-TILE_SIZE//2):
        return False
    return True

class MilkDragon:
    def __init__(self, pos):
        self.x, self.y = pos
        self.frame_index = 0
        self.actor = Actor(WALK_FRAMES[self.frame_index], center=pos)
        self.direction = 'left'  # 初始向左
        self.move_tick = 0
        self.facing_right = False  # 初始朝左
        self.alive = True
        self.blowup_tick = 0
        self.actor.rect = pygame.Rect(self.x - TILE_SIZE//2, self.y - TILE_SIZE//2, TILE_SIZE, TILE_SIZE)

    def update(self, frame_count):
        if not self.alive:
            self.blowup_tick += 1
            if self.blowup_tick > 15:  # 爆炸特效持续15帧
                self.alive = 'remove'
            return
        # 动画帧切换
        if frame_count % 8 == 0:
            self.frame_index = (self.frame_index + 1) % len(WALK_FRAMES)
            self.actor.image = WALK_FRAMES[self.frame_index]

        # 随机游走
        self.move_tick += 1
        if self.move_tick > 50:
            self.direction = random.choice(['left', 'right', 'up', 'down'])
            self.move_tick = 0

        dx, dy = 0, 0
        if self.direction == 'left':
            dx = -DRAGON_SPEED
            self.facing_right = False
        elif self.direction == 'right':
            dx = DRAGON_SPEED
            self.facing_right = True
        elif self.direction == 'up':
            dy = -DRAGON_SPEED
        elif self.direction == 'down':
            dy = DRAGON_SPEED

        new_x = self.x + dx
        new_y = self.y + dy

        # 更严格的移动判定，且提前预测新rect
        new_rect = pygame.Rect(new_x - TILE_SIZE//2, new_y - TILE_SIZE//2, TILE_SIZE, TILE_SIZE)
        can_move = can_move_to_strict(new_x, new_y)
        if can_move:
            # 再判断新rect与所有墙rect是否重叠
            from map_loader import get_wall_positions
            wall_hit = False
            for wx, wy in get_wall_positions():
                wall_rect = pygame.Rect(wx - TILE_SIZE//2, wy - TILE_SIZE//2, TILE_SIZE, TILE_SIZE)
                if new_rect.colliderect(wall_rect):
                    wall_hit = True
                    break
            if not wall_hit:
                self.x = new_x
                self.y = new_y
                self.actor.pos = (self.x, self.y)
                self.actor.rect.topleft = (self.x - TILE_SIZE//2, self.y - TILE_SIZE//2)
            else:
                self.direction = random.choice(['left', 'right', 'up', 'down'])
                self.move_tick = 0
        else:
            self.direction = random.choice(['left', 'right', 'up', 'down'])
            self.move_tick = 0

        # 每帧都同步rect
        self.actor.rect.topleft = (self.x - TILE_SIZE//2, self.y - TILE_SIZE//2)

    def draw(self):
        if not self.alive:
            self.actor.image = 'blowup'
        if self.facing_right:
            self.actor._surf = pygame.transform.flip(self.actor._orig_surf, True, False)
        else:
            self.actor._surf = self.actor._orig_surf
        self.actor.rect.topleft = (self.x - TILE_SIZE//2, self.y - TILE_SIZE//2)
        self.actor.draw()


def get_ground_positions():
    # 只选择地面tile
    ground_types = ['map0', 'map1', 'map2']
    positions = []
    for tile in get_tiles():
        if hasattr(tile, 'image') and tile.image in ground_types:
            positions.append((tile.x, tile.y))
    return positions

def spawn_dragons(n=1):
    global milk_dragons
    milk_dragons = []
    ground_positions = get_ground_positions()
    if not ground_positions:
        return
    used = set()
    # 获取玩家出生点，避免奶龙出生太近
    px, py = get_player_position()
    min_dist = TILE_SIZE * 4  # 距离玩家出生点至少3格
    for _ in range(n):
        # 只选距离玩家出生点较远的地面格
        available = [pos for pos in ground_positions if pos not in used and ((pos[0] - px) ** 2 + (pos[1] - py) ** 2) ** 0.5 > min_dist]
        if not available:
            break
        pos = random.choice(available)
        used.add(pos)
        milk_dragons.append(MilkDragon(pos))

def update_dragons(frame_count):
    for dragon in milk_dragons:
        dragon.update(frame_count)

def draw_dragons():
    for dragon in milk_dragons:
        dragon.draw()

def  get_milk_dragons():
    global milk_dragons
    return milk_dragons
