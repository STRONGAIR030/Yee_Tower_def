import math
import pygame
from components.animation import Animation
from constants import GRID_SIZE, MAP_REAL_SIZE
from tool_function import transform_coordinates
from typing import Dict, TYPE_CHECKING
from components.Item_group import Item

if TYPE_CHECKING:
    from components.enemy import Enemy  # 避免循環引用，僅在類型檢查時導入


class Bullet(Item):
    def __init__(self, pos, atk, angle=180):
        self.has_target = False  # 是否有目標
        self.is_effect = False  # 是否是爆炸效果
        self.atk = atk  # 子彈傷害
        self.pos = pos
        self.speed = 500  # 每秒 500 px
        self.dircetion_angle = angle  # 子彈方向角度
        self.radius = 7  # 子彈半徑
        self.color = pygame.Color("#f6f600")  # 子彈顏色

    def update(self, dt):
        dx = math.cos(math.radians(self.dircetion_angle)) * self.speed * dt
        dy = -math.sin(math.radians(self.dircetion_angle)) * self.speed * dt
        self.pos[0] += dx
        self.pos[1] += dy

        # 檢查是否超出邊界
        if (
            self.pos[0] < 0
            or self.pos[0] > MAP_REAL_SIZE[0]
            or self.pos[1] < 0
            or self.pos[1] > MAP_REAL_SIZE[1]
        ):
            self.kill()


def draw(self, surface, zoom):
    screen_x, screen_y = transform_coordinates(self.pos[0], self.pos[1])
    pygame.draw.circle(
        surface,
        self.color,
        (screen_x, screen_y),
        int(self.radius * zoom),
    )


class TrackBullet(Bullet):
    def __init__(self, pos, atk, target: "Enemy"):
        super().__init__(pos, atk)
        self.has_target = True  # 是否有目標
        self.target = target

    def update(self, dt):
        if self.target.display_health <= 0:
            self.kill()
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


def ease_in_out(t):  # 慢 -> 快 -> 慢
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - 2 * (1 - t) * (1 - t)


class ExplodeEffect(Bullet):
    def __init__(self, pos, atk, range=0.8):
        super().__init__(pos, atk)
        self.is_effect = True  # 爆炸效果
        self.radius = 0  # 爆炸效果的大小(用於繪製)
        self.range = range * GRID_SIZE  # 爆炸範圍
        self.alpha = 128  # 初始透明度
        self.color = pygame.Color("#ff0000")  # 爆炸效果顏色
        self.scale_animation = Animation(0.2, 0, self.range)
        self.alpha_animation = Animation(0.1, 128, 0, 0.2)
        self.hit_enemy = set()

    @property
    def effect_color(self):
        return (self.color[0], self.color[1], self.color[2], self.alpha)

    def is_hitted(self, enemy: "Enemy") -> bool:
        return enemy in self.hit_enemy

    def add_hit_enemy(self, enemy: "Enemy"):
        if enemy not in self.hit_enemy:
            self.hit_enemy.add(enemy)

    def update(self, dt):
        self.scale_animation.update(dt)
        self.alpha_animation.update(dt)

        # 更新爆炸效果的半徑和透明度
        self.radius = self.scale_animation.value
        self.alpha = int(self.alpha_animation.value)

        if self.alpha_animation.is_complete:
            self.kill()

    def draw(self, surface, zoom):
        screen_x, screen_y = transform_coordinates(self.pos[0], self.pos[1])
        scaled_radius = int(self.radius * zoom)

        # 繪製爆炸效果
        pygame.draw.circle(
            surface,
            self.effect_color,
            (screen_x, screen_y),
            scaled_radius,
        )
        # 設置透明度


class ExplodeBullet(TrackBullet):
    def __init__(self, pos, atk, range, target: "Enemy"):
        super().__init__(pos, atk, target)
        self.color = pygame.Color("#ff0000")
        self.explode_range = range  # 爆炸範圍

    def kill(self):
        # 在子彈被銷毀時，創建爆炸效果
        explode_effect = ExplodeEffect(self.pos, self.atk, self.explode_range)
        explode_effect.color = self.color
        self.group.add(explode_effect)  # 將爆炸效果添加到組中
        super().kill()  # 調用父類的 kill 方法


class StarBullet(Bullet):
    star_bullet_image = None

    def __init__(self, pos, atk, angle=90):
        super().__init__(pos, atk, angle)
        self.radius = 20  # 星形子彈的半徑
        self.speed = 100
        self.size = (self.radius * 2.5, self.radius * 2.5)  # 星形子彈的大小
        self.image = pygame.transform.scale(self.star_bullet_image, self.size)
        self.color = pygame.Color("#000000")
        self.rotate_deg = 0

    def update(self, dt):
        self.rotate_deg += 10
        if self.rotate_deg >= 360:
            self.rotate_deg = 0
        super().update(dt)

    def draw(self, surface, zoom):
        center_pox = transform_coordinates(self.pos[0], self.pos[1])

        scale_image = pygame.transform.smoothscale(
            self.image, (int(self.size[0] * zoom), int(self.size[1] * zoom))
        )
        rotated_image = pygame.transform.rotate(scale_image, self.rotate_deg)
        image_rect = rotated_image.get_rect(center=center_pox)
        surface.blit(rotated_image, image_rect)
