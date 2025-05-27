import pygame
import math
from constants import GRID_GAP, GRID_SIZE
from tool_function import find_max_health_enemy, tile_center, transform_coordinates
from components.bullet import (
    Bullet,
    ExplodeBullet,
    ExplodeEffect,
    StarBullet,
    TrackBullet,
)


class Tower:
    def __init__(self, grid_pos):
        self.atk = 1
        self.pos = tile_center(grid_pos[0], grid_pos[1])  # 塔的位置
        self.range = 1
        self.shoot_cooldown = 0.0  # 每秒可以射擊一次
        self.shoot_rate = 10
        self.color = (0, 255, 0)  # 塔的顏色
        self.bullet = ExplodeBullet

    @property
    def radius(self):
        return GRID_SIZE * (self.range + 0.5) + GRID_GAP * self.range

    def update(self, dt, enemies, bullets):
        self.shoot_cooldown += dt
        if self.shoot_cooldown >= 1 / self.shoot_rate:
            shoot = self.shoot(enemies=enemies, bullets=bullets)
            if shoot:
                self.shoot_cooldown = 0.0

    def draw(self, surface, zoom):
        screen_x, screen_y = transform_coordinates(self.pos[0], self.pos[1])
        pygame.draw.circle(
            surface,
            self.color,
            (screen_x, screen_y),
            int(GRID_SIZE / 2 * zoom),
            2,
        )
        pygame.draw.circle(
            surface, self.color, (screen_x, screen_y), int(self.radius * zoom), 1
        )

    def shoot_bullet(self, target, bullets) -> None:
        dx = target.pos[0] - self.pos[0]
        dy = target.pos[1] - self.pos[1]
        angle = math.degrees(math.atan2(-dy, dx))  # 計算角度
        new_bullet = self.bullet([self.pos[0], self.pos[1]], self.atk, angle)
        bullets.add(new_bullet)  # 將新子彈添加到子彈組中

    def shoot_track_bullet(self, target, bullets) -> None:
        target.health -= self.atk  # 對敵人造成傷害
        new_bullet = self.bullet([self.pos[0], self.pos[1]], self.atk, 10, target)
        bullets.add(new_bullet)  # 將新子彈添加到子彈組中

    def shoot(self, enemies, bullets) -> bool:
        for enemy in enemies:
            dx = enemy.pos[0] - self.pos[0]
            dy = enemy.pos[1] - self.pos[1]
            dist = math.hypot(dx, dy)
            if dist <= self.radius and enemy.health > 0:
                self.shoot_track_bullet(enemy, bullets)  # 發射子彈
                return True  # 成功射擊

        return False  # 沒有敵人可以射擊


# 三角塔(狙擊塔)
class TriangleTower(Tower):
    def __init__(self, grid_pos):
        super().__init__(grid_pos)
        self.atk = 20  # 三角塔的攻擊力更高
        self.range = 2  # 三角塔的攻擊範圍更大
        self.shoot_rate = 0.5
        self.color = pygame.Color("#b30000")  # 三角塔的顏色
        self.bullet = StarBullet  # 使用星形子彈

    def shoot(self, enemies, bullets) -> bool:
        can_shoot = []
        for enemy in enemies:
            dx = enemy.pos[0] - self.pos[0]
            dy = enemy.pos[1] - self.pos[1]
            dist = math.hypot(dx, dy)
            if dist <= self.radius and enemy.health > 0:
                can_shoot.append(enemy)

        target = find_max_health_enemy(can_shoot)  # 找到生命值最高的敵人

        if target:
            self.shoot_bullet(target, bullets)  # 發射子彈
            return True  # 成功射擊

        return False  # 沒有敵人可以射擊
