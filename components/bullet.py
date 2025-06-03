import math
import pygame
from components.animation import Animation, AnimationManager
from constants import GRID_SIZE, MAP_REAL_SIZE
from tool.tool_function import rotate_point, transform_coordinates
from typing import TYPE_CHECKING
from components.Item_group import Item

if TYPE_CHECKING:
    from components.enemy import Enemy  # 避免循環引用，僅在類型檢查時導入


# 子彈類別
class Bullet(Item):
    def __init__(self, pos, atk, angle=180):
        self.hit_box = "circle"
        self.has_target = False  # 是否有目標
        self.is_effect = False  # 是否是爆炸效果
        self.atk = atk  # 子彈傷害
        self.pos = pos
        self.speed = 500  # 每秒 500 px
        self.dircetion_angle = angle  # 子彈方向角度
        self.radius = 7  # 子彈半徑
        self.color = pygame.Color("#f6f600")  # 子彈顏色

    def update(self, dt):  # 更新子彈位置
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


def draw(self, surface, zoom):  # 繪製子彈
    screen_x, screen_y = transform_coordinates(self.pos[0], self.pos[1])
    pygame.draw.circle(
        surface,
        self.color,
        (screen_x, screen_y),
        int(self.radius * zoom),
    )


# 繪製追蹤子彈
class TrackBullet(Bullet):
    def __init__(self, pos, atk, target: "Enemy"):
        super().__init__(pos, atk)
        self.has_target = True  # 是否有目標
        self.target = target  # 目標敵人

    def update(self, dt):
        if self.target.display_health <= 0:  # 如果目標敵人已經死亡
            self.kill()  # 銷毀子彈

        # 計算子彈的移動向量
        dx = self.target.pos[0] - self.pos[0]
        dy = self.target.pos[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist < self.speed * dt:
            self.pos = self.target.pos
        else:
            self.pos[0] += dx / dist * self.speed * dt
            self.pos[1] += dy / dist * self.speed * dt

    # 繪製子彈
    def draw(self, surface, zoom):
        screen_x, screen_y = transform_coordinates(self.pos[0], self.pos[1])
        pygame.draw.circle(
            surface,
            self.color,
            (screen_x, screen_y),
            int(self.radius * zoom),
        )


# 繪製效果子彈
class EffectBullet(Bullet):
    def __init__(self, pos, atk, angle=180):
        super().__init__(pos, atk, angle)
        self.is_effect = True  # 是否是效果子彈
        self.hit_enemy = set()  # 記錄已經擊中的敵人
        self.radius = 0  # 初始半徑為 0
        self.alpha = 255  # 初始透明度
        self.color = pygame.Color("#f6f600")  # 子彈顏色

    @property
    def effect_color(self):
        return (self.color[0], self.color[1], self.color[2], self.alpha)

    def is_hitted(self, enemy: "Enemy") -> bool:  # 檢查子彈是否已經擊中過敵人
        return enemy in self.hit_enemy

    def add_hit_enemy(self, enemy: "Enemy"):  # 添加已經擊中的敵人
        if enemy not in self.hit_enemy:
            self.hit_enemy.add(enemy)


class ExplodeEffect(EffectBullet):
    explode_effect_sound = None  # 爆炸效果音效

    def __init__(self, pos, atk, range=0.8):
        super().__init__(pos, atk)
        self.radius = 0  # 爆炸效果的大小(用於繪製)
        self.range = range * GRID_SIZE  # 爆炸範圍
        self.alpha = 128  # 初始透明度
        self.color = pygame.Color("#ff0000")  # 爆炸效果顏色
        self.scale_animation = Animation(0.2, 0, self.range)
        self.alpha_animation = Animation(0.1, 128, 0, 0.2)
        self.hit_enemy = set()
        self.explode_effect_sound.play()  # 播放爆炸效果音效

    def update(self, dt):
        self.scale_animation.update(dt)  # 更新爆炸效果的大小
        self.alpha_animation.update(dt)  # 更新爆炸效果的透明度

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

    # 更新子彈
    def update(self, dt):
        # 計算選轉角度
        self.rotate_deg += 10
        if self.rotate_deg >= 360:
            self.rotate_deg = 0
        super().update(dt)  # 更新子彈位置

    # 繪製子彈
    def draw(self, surface, zoom):
        center_pox = transform_coordinates(self.pos[0], self.pos[1])

        scale_image = pygame.transform.scale(
            self.image, (int(self.size[0] * zoom), int(self.size[1] * zoom))
        )
        rotated_image = pygame.transform.rotate(scale_image, self.rotate_deg)
        image_rect = rotated_image.get_rect(center=center_pox)
        surface.blit(rotated_image, image_rect)


class Laserbullet(EffectBullet):
    laser_sound = None  # 雷射子彈的音效

    def __init__(self, pos, atk, size, angle=90):
        super().__init__(pos, atk, angle)
        self.hit_box = "polygon"  # 雷射子彈的碰撞盒為多邊形
        self.is_effect = True  # 是否是效果子彈
        self.hit_enemy = set()  # 記錄已經擊中的敵人
        self.radius = 1  # 雷射子彈的半徑
        self.size = (0.1, 0.1)
        self.original_size = size  # 原始大小
        self.alpha = 0  # 初始透明度
        self.rect_point = (
            (0, 0.5),
            (1, 0.5),
            (1, -0.5),
            (0, -0.5),
        )  # 雷射子彈的大小
        self.speed = 0  # 雷射子彈速度
        self.color = pygame.Color("#2a9aab")  # 雷射子彈顏色
        self.scale_animation1 = AnimationManager(
            [
                [0.07, 1, 0.8, 0.07],
                [0.07, 0.8, 1],
            ],
            -1,
        )
        self.alpha_animation = Animation(0.3, 0, 255)  # 雷射子彈透明度動畫
        self.kill_alpha_animation = Animation(0.2, 255, 0)  # 雷射子彈銷毀時的透明度動畫
        self.scale_animation2 = Animation(0.2, 0, size)  # 雷射子彈大小動畫
        self.kill_animation1 = Animation(0.2, 1, 0, 0.1)  # 雷射子彈銷毀時的大小動畫
        self.kill_animation2 = Animation(0.2, size, 0)  # 雷射子彈銷毀時的大小動畫
        self.kill_time = 1  # 雷射子彈持續時間
        self.laser_sound.play()  # 播放雷射子彈音效

    @property
    def polygon(self):  # 獲取雷射子彈的多邊形點
        polygon_points = []
        for point in self.rect_point:
            rotated_point = rotate_point(
                self.pos[0],
                self.pos[1],
                point[0] * self.size[0] + self.pos[0],
                point[1] * self.size[1] + self.pos[1],
                self.dircetion_angle,
            )
            polygon_points.append(rotated_point)
        return polygon_points

    def update(self, dt):  # 更新雷射子彈狀態
        self.scale_animation1.update(dt)  # 更新雷射子彈大小動畫
        self.scale_animation2.update(dt)  # 更新雷射子彈大小動畫
        self.alpha_animation.update(dt)  # 更新雷射子彈透明度動畫

        # 更新子彈的大小
        self.size = (
            self.scale_animation2.value * GRID_SIZE,
            self.scale_animation1.value * GRID_SIZE,
        )
        self.alpha = int(self.alpha_animation.value)  # 更新雷射子彈透明度
        self.kill_time -= dt  # 減少雷射子彈的持續時間
        if self.kill_time <= 0:  # 如果雷射子彈持續時間結束
            self.kill_animation1.update(dt)  # 更新銷毀動畫
            self.kill_animation2.update(dt)  # 更新銷毀動畫
            self.kill_alpha_animation.update(dt)  # 更新銷毀透明度動畫
            if self.kill_animation1.is_complete:  # 如果銷毀動畫完成
                self.kill()
            else:
                # 更新雷射子彈的大小和透明度
                self.size = (
                    self.original_size * GRID_SIZE,
                    self.kill_animation1.value * GRID_SIZE,
                )
                self.alpha = int(self.kill_alpha_animation.value)

    # 繪製雷射子彈
    def draw(self, surface, zoom):
        rect_points = []
        for point in self.polygon:
            rect_points.append(transform_coordinates(point[0], point[1]))

        pygame.draw.polygon(
            surface,
            self.effect_color,
            rect_points,
        )
