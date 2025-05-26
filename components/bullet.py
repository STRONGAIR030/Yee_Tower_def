import math
import pygame
from tool_function import transform_coordinates
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from components.enemy import Enemy  # 避免循環引用，僅在類型檢查時導入
    from components.Item_group import Item  # 假設有一個 Item_group 模組定義了 Item 類別


class Bullet:
    def __init__(self, pos, atk, target: "Enemy"):
        self.pos = pos
        self.target = target
        self.speed = 500  # 每秒 500 px
        self.radius = 5  # 子彈半徑
        self.color = pygame.Color("#f6f600")  # 子彈顏色

    def update(self, dt):
        dx = self.target.pos[0] - self.pos[0]
        dy = self.target.pos[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist < self.speed * dt:
            self.pos = self.target.pos
        else:
            self.pos[0] += dx / dist * self.speed * dt
            self.pos[1] += dy / dist * self.speed * dt

    def draw(self, surface, zoom):
        screen_x, screen_y = transform_coordinates(self.pos[0], self.pos[1])
        pygame.draw.circle(
            surface,
            self.color,
            (screen_x, screen_y),
            int(self.radius * zoom),
        )
