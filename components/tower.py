import random
import pygame
import math
from typing import TYPE_CHECKING, List
from constants import GRID_GAP, GRID_SIZE
from tool.tool_function import (
    find_max_health_enemy,
    get_price,
    tile_center,
    transform_coordinates,
)
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


class DrawImage:
    def __init__(self, item_image, size, zoom):
        self.image = item_image
        self.size = (size * zoom, size * zoom)  # 圖片大小
        self.image = pygame.transform.scale(self.image, self.size)

    def draw_image(self, surface, pos, zoom):
        center_pox = transform_coordinates(pos[0], pos[1])
        scale_image = pygame.transform.scale(
            self.image, (int(self.size[0] * zoom), int(self.size[1] * zoom))
        )
        image_rect = scale_image.get_rect(center=center_pox)
        surface.blit(scale_image, image_rect)


class Tower:
    def __init__(self, grid_pos):
        self.level = 1
        self.atk = 1
        self.pos = tile_center(grid_pos[0], grid_pos[1])  # 塔的位置
        self._range = 1
        self.shoot_cooldown = 0.0  # 每秒可以射擊一次
        self._shoot_rate = 1
        self._max_shoot_rate = 10
        self._max_range = 3
        self._price = 1
        self.color = (0, 255, 0)  # 塔的顏色
        self.bullet = TrackBullet

    @property
    def price(self):
        return get_price(self.level, self._price)

    @property
    def shoot_rate(self):
        return self._shoot_rate

    @shoot_rate.setter
    def shoot_rate(self, value):
        self._shoot_rate = min(value, self._max_shoot_rate)  # 確保射擊速率不超過最大值

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self, value):
        self._range = min(value, self._max_range)  # 確保射程不超過最大值

    @property
    def radius(self):
        return GRID_SIZE * (self.range + 0.5) + GRID_GAP * self.range

    def update(self, dt, enemies, bullets):
        self.shoot_cooldown += dt
        if self.shoot_cooldown >= 1 / self.shoot_rate:
            shoot = self.shoot(enemies=enemies, bullets=bullets)
            if shoot:
                self.shoot_cooldown = 0.0

    def draw_range(self, surface, zoom):
        screen_x, screen_y = transform_coordinates(self.pos[0], self.pos[1])
        pygame.draw.circle(
            surface,
            self.color,
            (screen_x, screen_y),
            int(self.radius * zoom),
            1,
        )

    def draw(self, surface, zoom):
        screen_x, screen_y = transform_coordinates(self.pos[0], self.pos[1])
        pygame.draw.circle(
            surface,
            self.color,
            (screen_x, screen_y),
            int(GRID_SIZE / 2 * zoom * 0.8),
        )
        self.draw_range(surface, zoom)  # 繪製射程範圍

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

    def upgrade(self):
        self.atk += 1
        self.range += 0.1
        self.shoot_rate += 0.1


# 三角塔(狙擊塔)
class TriangleTower(Tower, DrawImage):
    triangle_tower_image = None  # 靜態變量，用於存儲三角塔的圖片

    def __init__(self, grid_pos):
        Tower.__init__(self, grid_pos)
        DrawImage.__init__(self, self.triangle_tower_image, GRID_SIZE, 1)
        self.atk = 5  # 三角塔的攻擊力更高
        self._range = 3  # 三角塔的攻擊範圍更大
        self._shoot_rate = 0.2
        self._max_shoot_rate = 3
        self._max_range = 6
        self._price = 5  # 三角塔的價格
        self.color = pygame.Color("#b30000")  # 三角塔的顏色
        self.bullet = TrackBullet  # 使用追蹤子彈

    def upgrade(self):
        self.atk += 5
        self.range += 0.5
        self.shoot_rate += 0.2

    def shoot(self, enemies, bullets) -> bool:
        can_shoot = self.check_enemy_in_range(
            enemies, enemy_num=len(enemies)
        )  # 檢查是否有敵人在射程內

        target = find_max_health_enemy(can_shoot)  # 找到生命值最高的敵人

        if target:
            self.shoot_track_bullet(target, bullets)  # 發射子彈
            return True  # 成功射擊

        return False  # 沒有敵人可以射擊

    def draw(self, surface, zoom):
        self.draw_image(surface, self.pos, zoom)  # 繪製塔的圖片
        self.draw_range(surface, zoom)  # 繪製射程範圍


class SquareTower(Tower):
    def __init__(self, grid_pos):
        super().__init__(grid_pos)
        self.atk = 2  # 方形塔的攻擊力
        self._range = 2  # 方形塔的攻擊範圍
        self._explode_range = 0.5
        self._shoot_rate = 0.8
        self._price = 15
        self.color = pygame.Color("#ff0000")  # 方形塔的顏色
        self.bullet = ExplodeBullet  # 使用爆炸子彈

        self._max_explode_range = 1.5
        self._max_shoot_rate = 2
        self._max_range = 3

    @property
    def explode_range(self):
        return self._explode_range

    @explode_range.setter
    def explode_range(self, value):
        self._explode_range = min(value, self._max_explode_range)

    def upgrade(self):
        self.atk += 2.5
        self.range += 0.1
        self.shoot_rate += 0.2
        self.explode_range += 0.1

    def shoot(self, enemies, bullets) -> bool:
        can_shoot = self.check_enemy_in_range(enemies)

        if len(can_shoot) > 0:
            self.shoot_explode_bullet(can_shoot[0], bullets)  # 發射爆炸子彈
            return True

        return False  # 沒有敵人可以射擊

    def draw(self, surface, zoom):
        screen_x, screen_y = transform_coordinates(self.pos[0], self.pos[1])
        rect = pygame.Rect(
            screen_x - GRID_SIZE * zoom / 2,
            screen_y - GRID_SIZE * zoom / 2,
            GRID_SIZE * zoom * 0.8,
            GRID_SIZE * zoom * 0.8,
        )
        rect.center = (screen_x, screen_y)  # 確保矩形中心在塔的位置
        pygame.draw.rect(
            surface,
            self.color,
            rect,
        )
        self.draw_range(surface, zoom)


class StarTower(Tower, DrawImage):
    star_tower_image = None  # 靜態變量，用於存儲星形塔的圖片

    def __init__(self, grid_pos):
        Tower.__init__(self, grid_pos)
        DrawImage.__init__(self, self.star_tower_image, GRID_SIZE, 1)
        self.atk = 1  # 星形塔的攻擊力
        self._range = 0.8  # 星形塔的攻擊範圍
        self._shoot_rate = 1
        self._bullet_num = 5
        self._price = 5
        self.color = pygame.Color("#ffcc00")  # 星形塔的顏色
        self.bullet = StarBullet  # 使用星形子彈

        self._max_bullet_num = 10  # 星形塔的子彈數量上限
        self._max_range = 4
        self._max_shoot_rate = 2

    @property
    def bullet_num(self):
        return self._bullet_num

    @bullet_num.setter
    def bullet_num(self, value):
        self._bullet_num = min(value, self._max_bullet_num)

    def upgrade(self):
        self.atk += 1
        self.range += 0.2
        self.shoot_rate += 0.1
        self.bullet_num += 0.3

    def shoot_bullet(self, target, bullets):
        angle = random.uniform(0, 360)
        d_angle = 360 / int(self.bullet_num)
        for i in range(int(self.bullet_num)):
            new_angle = angle + i * d_angle
            new_bullet = self.bullet([self.pos[0], self.pos[1]], self.atk, new_angle)
            bullets.add(new_bullet)

    def shoot(self, enemies, bullets) -> bool:
        can_shoot = self.check_enemy_in_range(enemies)

        if len(can_shoot) > 0:
            self.shoot_bullet(can_shoot[0], bullets)  # 發射星形子彈
            return True

        return False  # 沒有敵人可以射擊

    def draw(self, surface, zoom):
        self.draw_image(surface, self.pos, zoom)
        self.draw_range(surface, zoom)  # 繪製射程範圍


class PentagonTower(Tower, DrawImage):
    pentagon_tower_image = None  # 靜態變量，用於存儲五邊形塔的圖片

    def __init__(self, grid_pos):
        Tower.__init__(self, grid_pos)
        DrawImage.__init__(self, self.pentagon_tower_image, GRID_SIZE, 0.9)
        self.atk = 0.2  # 五邊形塔的攻擊力
        self._range = 0.8  # 五邊形塔的攻擊範圍
        self._shoot_rate = 0.8
        self._freeze_time = 2.0
        self._price = 20
        self.color = pygame.Color("#00b300")  # 五邊形塔的顏色
        self.bullet = None  # 使用爆炸子彈

        self._max_range = 3
        self._max_shoot_rate = 1.5
        self._max_freeze_time = 5.0  # 五邊形塔的凍結時間上限

    @property
    def freeze_time(self):
        return self._freeze_time

    @freeze_time.setter
    def freeze_time(self, value):
        self._freeze_time = min(
            value, self._max_freeze_time
        )  # 確保凍結時間不超過最大值

    def upgrade(self):
        self.atk += 0.5
        self.range += 0.2
        self.shoot_rate += 0.1
        self.freeze_time += 0.5

    def freeze_enemy(self, enemies):
        can_freeze = self.check_enemy_in_range(enemies, enemy_num=len(enemies))
        for enemy in can_freeze:
            enemy.freeze_time = self.freeze_time  # 設置敵人的凍結時間

    def shoot(self, enemies, bullets) -> bool:
        can_shoot = self.check_enemy_in_range(enemies, enemy_num=len(enemies))
        for enemy in can_shoot:
            if enemy.health > 0:
                enemy.health -= self.atk
                enemy.display_health -= self.atk

        if len(can_shoot) > 0:
            return True
        return False

    def update(self, dt, enemies, bullets):
        self.freeze_enemy(enemies)  # 更新時凍結敵人
        super().update(dt, enemies, bullets)

    def draw(self, surface, zoom):
        self.draw_image(surface, self.pos, zoom)
        self.draw_range(surface, zoom)  # 繪製射程範圍


class RatctangleTower(Tower, DrawImage):
    ractangle_tower_image = None  # 靜態變量，用於存儲長方形塔的圖片

    def __init__(self, grid_pos):
        Tower.__init__(self, grid_pos)
        DrawImage.__init__(self, self.ractangle_tower_image, GRID_SIZE, 1.1)
        self.atk = 10  # 長方形塔的攻擊力
        self._range = 1.5  # 長方形塔的攻擊範圍
        self._shoot_rate = 0.5
        self._price = 20
        self.color = pygame.Color("#b300b3")  # 長方形塔的顏色
        self.bullet = Laserbullet  # 使用追蹤子彈

        self._max_range = 3
        self._max_shoot_rate = 2

    @property
    def laser_size(self):
        return self._range + 0.8

    def upgrade(self):
        self.atk += 4
        self.range += 0.1
        self.shoot_rate += 0.1

    def shoot_laser(self, target, bullets) -> None:
        dx = target.pos[0] - self.pos[0]
        dy = target.pos[1] - self.pos[1]
        angle = math.degrees(math.atan2(-dy, dx))  # 計算角度
        new_bullet = self.bullet(
            [self.pos[0], self.pos[1]], self.atk, self.laser_size, angle
        )
        bullets.add(new_bullet)  # 將新子彈添加到子彈組中

    def shoot(self, enemies, bullets) -> bool:
        can_shoot = self.check_enemy_in_range(enemies)

        if len(can_shoot) > 0:
            self.shoot_laser(can_shoot[0], bullets)  # 發射追蹤子彈
            return True

        return False  # 沒有敵人可以射擊

    def draw(self, surface, zoom):
        self.draw_image(surface, self.pos, zoom)
        self.draw_range(surface, zoom)
