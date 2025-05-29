import math
import pygame
import random
from tool.tool_function import transform_coordinates
from constants import GRID_SIZE, GRID_GAP, ENEMY_COLORS
from components.Item_group import Item


class Enemy(Item):
    def __init__(self, path):
        super().__init__()
        self.hit_box = "circle"  # 碰撞檢測方式
        self.path = path  # 敵人行走路徑
        self.offset = [
            random.uniform(-0.2, 0.2) * GRID_SIZE,
            random.uniform(-0.2, 0.2) * GRID_SIZE,
        ]
        self.pos = [
            path[0][0] * (GRID_SIZE + GRID_GAP) + GRID_SIZE / 2 + self.offset[0],
            path[0][1] * (GRID_SIZE + GRID_GAP) + GRID_SIZE / 2 + self.offset[1],
        ]
        self.speed = 300  # 每秒移動 100 px
        self.radius_ratio = 0.1  # 半徑比例
        self.radius = GRID_SIZE * self.radius_ratio
        self.display_health = 1  # 敵人生命值
        self.health = 1  # 敵人生命值
        self.path_index = 0  # 當前路徑索引
        self.color = random.choice(ENEMY_COLORS)  # 隨機顏色
        self._freeze_time = 0.0  # 凍結時間

    @property
    def freeze_time(self):
        return self._freeze_time

    @freeze_time.setter
    def freeze_time(self, value):
        self._freeze_time = max(self._freeze_time, value)  # 確保凍結時間不會減少

    def update(self, dt):
        move_speed = self.speed * dt
        if self.freeze_time > 0:
            self._freeze_time -= dt
            move_speed /= 2

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
            self.pos[0] += dx / dist * move_speed
            self.pos[1] += dy / dist * move_speed

    def draw(self, surface, zoom):
        screen_x, screen_y = transform_coordinates(self.pos[0], self.pos[1])
        radius = int(self.radius * zoom)
        pygame.draw.circle(surface, self.color, (screen_x, screen_y), radius)
