import math
import pygame
import random
from tool_function import transform_coordinates
from constants import GRID_SIZE, GRID_GAP, ENEMY_COLORS
from components.Item_group import Item


class Enemy(Item):
    def __init__(self, path):
        super().__init__()
        self.path = path  # 敵人行走路徑
        self.offset = [
            random.uniform(-0.2, 0.2) * GRID_SIZE,
            random.uniform(-0.2, 0.2) * GRID_SIZE,
        ]
        self.pos = [
            path[0][0] * (GRID_SIZE + GRID_GAP) + GRID_SIZE / 2 + self.offset[0],
            path[0][1] * (GRID_SIZE + GRID_GAP) + GRID_SIZE / 2 + self.offset[1],
        ]
        self.speed = 200  # 每秒移動 100 px
        self.radius_ratio = 0.1  # 半徑比例
        self.radius = GRID_SIZE * self.radius_ratio
        self.display_health = 100  # 敵人生命值
        self.health = 100  # 敵人生命值
        self.path_index = 0  # 當前路徑索引
        self.color = random.choice(ENEMY_COLORS)  # 隨機顏色

    def update(self, dt):
        if self.path_index >= len(self.path):
            self.path_index = 0  # 重置路徑索引

        target = [
            self.path[self.path_index][0] * (GRID_SIZE + GRID_GAP)
            + GRID_SIZE / 2
            + self.offset[0],
            self.path[self.path_index][1] * (GRID_SIZE + GRID_GAP)
            + GRID_SIZE / 2
            + self.offset[1],
        ]

        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]
        dist = math.hypot(dx, dy)

        if dist < self.speed * dt:
            self.pos = target
            self.path_index += 1
        else:
            self.pos[0] += dx / dist * self.speed * dt
            self.pos[1] += dy / dist * self.speed * dt

    def draw(self, surface, zoom):
        screen_x, screen_y = transform_coordinates(self.pos[0], self.pos[1])
        radius = int(self.radius * zoom)
        pygame.draw.circle(surface, self.color, (screen_x, screen_y), radius)
