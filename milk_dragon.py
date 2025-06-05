from pgzero.builtins import Actor
import random
from player import can_move_to
from map_loader import get_tiles
import pygame
from config import TILE_SIZE, Dragon_SPEED

WALK_FRAMES = [f'walk_{i}' for i in range(9)]
DRAGON_SPEED = Dragon_SPEED
TILE_SIZE = TILE_SIZE
milk_dragons = []

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

        if can_move_to(new_x, new_y):
            self.x = new_x
            self.y = new_y
            self.actor.pos = (self.x, self.y)
            self.actor.rect.topleft = (self.x - TILE_SIZE//2, self.y - TILE_SIZE//2)  # Update rect position
        else:
            self.direction = random.choice(['left', 'right', 'up', 'down'])
            self.move_tick = 0

    def draw(self):
        if not self.alive:
            self.actor.image = 'blowup'
        if self.facing_right:
            self.actor._surf = pygame.transform.flip(self.actor._orig_surf, True, False)
        else:
            self.actor._surf = self.actor._orig_surf
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
    for _ in range(n):
        # 随机选择未用过的地面格
        available = [pos for pos in ground_positions if pos not in used]
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
