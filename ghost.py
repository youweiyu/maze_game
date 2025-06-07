from pgzero.builtins import Actor
from config import TILE_SIZE
from map_loader import get_tiles
import pygame
import random

class Ghost:
    def __init__(self, player_pos):
        # 在出口处生成
        self.x, self.y = self._get_exit_pos()
        self.actor = Actor('ghost', center=(self.x, self.y))
        self.actor.rect = pygame.Rect(self.x - TILE_SIZE//2, self.y - TILE_SIZE//2, TILE_SIZE, TILE_SIZE)
        self.speed = 1.5
        self.alive = True
        self.blowup_tick = 0

    def _get_exit_pos(self):
        # 在所有出口格中随机选一个
        exit_chars = {'g', 'j', 'h', 'l', 'i', 'n'}
        exits = []
        for tile in get_tiles():
            if hasattr(tile, 'char') and tile.char in exit_chars:
                exits.append((tile.x, tile.y))
        if exits:
            return random.choice(exits)
        # 没有出口则放左上角
        return (TILE_SIZE, TILE_SIZE)

    def update(self, player_pos):
        if not self.alive:
            self.blowup_tick += 1
            if self.blowup_tick > 15:
                self.alive = 'remove'
            return
        px, py = player_pos
        dx = px - self.x
        dy = py - self.y
        dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        move_x = self.speed * dx / dist
        move_y = self.speed * dy / dist
        self.x += move_x
        self.y += move_y
        self.actor.pos = (self.x, self.y)
        self.actor.rect.topleft = (self.x - TILE_SIZE//2, self.y - TILE_SIZE//2)

    def draw(self):
        if not self.alive:
            self.actor.image = 'blowup'
        else:
            self.actor.image = 'ghost'
        self.actor.draw()
