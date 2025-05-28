import random
import re
import pygame
import math
from typing import TYPE_CHECKING, List
from constants import GRID_GAP, GRID_SIZE
from tool_function import find_max_health_enemy, tile_center, transform_coordinates
from components.bullet import (
    Bullet,
    ExplodeBullet,
    ExplodeEffect,
    Laserbullet,
    StarBullet,
    TrackBullet,
)

if TYPE_CHECKING:
    from components.enemy import Enemy  # 避免循環引用，僅在類型檢查時導入


class Tower:
    def __init__(self, grid_pos):
        self.atk = 1
        self.pos = tile_center(grid_pos[0], grid_pos[1])  # 塔的位置
        self.range = 1
        self.shoot_cooldown = 0.0  # 每秒可以射擊一次
        self.shoot_rate = 5
        self.color = (0, 255, 0)  # 塔的顏色
        self.bullet = TrackBullet

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

    def shoot_bullet(self, target, bullets) -> float:
        dx = target.pos[0] - self.pos[0]
        dy = target.pos[1] - self.pos[1]
        angle = math.degrees(math.atan2(-dy, dx))  # 計算角度
        new_bullet = self.bullet([self.pos[0], self.pos[1]], self.atk, angle)
        bullets.add(new_bullet)  # 將新子彈添加到子彈組中
        return angle  # 返回子彈的角度

    def shoot_track_bullet(self, target, bullets) -> None:
        target.health -= self.atk  # 對敵人造成傷害
        new_bullet = self.bullet([self.pos[0], self.pos[1]], self.atk, target)
        bullets.add(new_bullet)  # 將新子彈添加到子彈組中

    def shoot_explode_bullet(self, target, bullets) -> None:
        target.health -= self.atk
        new_bullet = self.bullet(
            [self.pos[0], self.pos[1]], self.atk, self.explode_range, target
        )
        bullets.add(new_bullet)  # 將新子彈添加到子彈組中

    def check_enemy_in_range(self, enemies, enemy_num: int = 1) -> List["Enemy"]:
        can_shoot = []
        for enemy in enemies:
            dx = enemy.pos[0] - self.pos[0]
            dy = enemy.pos[1] - self.pos[1]
            dist = math.hypot(dx, dy)
            if dist <= self.radius and enemy.health > 0:
                can_shoot.append(enemy)
            if len(can_shoot) >= enemy_num:
                return can_shoot
        return can_shoot

    def shoot(self, enemies, bullets) -> bool:
        enemy = self.check_enemy_in_range(enemies)
        if len(enemy) != 0:
            self.shoot_track_bullet(enemy[0], bullets)
            return True

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
        can_shoot = self.check_enemy_in_range(
            enemies, enemy_num=len(enemies)
        )  # 檢查是否有敵人在射程內

        target = find_max_health_enemy(can_shoot)  # 找到生命值最高的敵人

        if target:
            self.shoot_bullet(target, bullets)  # 發射子彈
            return True  # 成功射擊

        return False  # 沒有敵人可以射擊


class SquareTower(Tower):
    def __init__(self, grid_pos):
        super().__init__(grid_pos)
        self.atk = 5  # 方形塔的攻擊力
        self.range = 1.5  # 方形塔的攻擊範圍
        self.explode_range = 0.8
        self.shoot_rate = 1
        self.color = pygame.Color("#0000b3")  # 方形塔的顏色
        self.bullet = ExplodeBullet  # 使用爆炸子彈

    def shoot(self, enemies, bullets) -> bool:
        can_shoot = self.check_enemy_in_range(enemies)

        if len(can_shoot) > 0:
            self.shoot_explode_bullet(can_shoot[0], bullets)  # 發射爆炸子彈
            return True

        return False  # 沒有敵人可以射擊


class StarTower(Tower):
    def __init__(self, grid_pos):
        super().__init__(grid_pos)
        self.atk = 10  # 星形塔的攻擊力
        self.range = 1.5  # 星形塔的攻擊範圍
        self.shoot_rate = 3
        self.bullet_num = 5
        self.color = pygame.Color("#ffcc00")  # 星形塔的顏色
        self.bullet = StarBullet  # 使用星形子彈

    def shoot_bullet(self, target, bullets):
        angle = random.uniform(0, 360)
        d_angle = 360 / self.bullet_num
        for i in range(self.bullet_num):
            new_angle = angle + i * d_angle
            new_bullet = self.bullet([self.pos[0], self.pos[1]], self.atk, new_angle)
            bullets.add(new_bullet)

    def shoot(self, enemies, bullets) -> bool:
        can_shoot = self.check_enemy_in_range(enemies)

        if len(can_shoot) > 0:
            self.shoot_bullet(can_shoot[0], bullets)  # 發射星形子彈
            return True

        return False  # 沒有敵人可以射擊


class PentagonTower(Tower):
    def __init__(self, grid_pos):
        super().__init__(grid_pos)
        self.atk = 15  # 五邊形塔的攻擊力
        self.range = 2  # 五邊形塔的攻擊範圍
        self.shoot_rate = 0.5
        self.freeze_time = 2.0
        self.color = pygame.Color("#00b300")  # 五邊形塔的顏色
        self.bullet = None  # 使用爆炸子彈

    def freeze_enemy(self, enemies):
        can_freeze = self.check_enemy_in_range(enemies, enemy_num=len(enemies))
        for enemy in can_freeze:
            enemy.freeze_time = self.freeze_time  # 設置敵人的凍結時間

    def shoot(self, enemies, bullets) -> bool:
        can_shoot = self.check_enemy_in_range(enemies)
        for enemy in can_shoot:
            if enemy.health > 0:
                enemy.health -= self.atk
                enemy.display_health -= self.atk
            print(f"health: {enemy.health}, display_health: {enemy.display_health}")

        return True  # 沒有敵人可以射擊

    def update(self, dt, enemies, bullets):
        self.freeze_enemy(enemies)  # 更新時凍結敵人
        super().update(dt, enemies, bullets)


class RatctangleTower(Tower):
    def __init__(self, grid_pos):
        super().__init__(grid_pos)
        self.atk = 8  # 長方形塔的攻擊力
        self.range = 1.5  # 長方形塔的攻擊範圍
        self.shoot_rate = 0.5
        self.color = pygame.Color("#b300b3")  # 長方形塔的顏色
        self.bullet = Laserbullet  # 使用追蹤子彈

    def shoot(self, enemies, bullets) -> bool:
        can_shoot = self.check_enemy_in_range(enemies)

        if len(can_shoot) > 0:
            self.shoot_bullet(can_shoot[0], bullets)  # 發射追蹤子彈
            return True

        return False  # 沒有敵人可以射擊
