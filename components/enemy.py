import math
import pygame
import random
from game_stat import GameState
from tool.tool_function import transform_coordinates
from constants import GRID_SIZE, GRID_GAP, ENEMY_COLORS
from components.Item_group import Item


# 敵人類別
class Enemy(Item):
    def __init__(self, path):
        super().__init__()  # 初始化 Item 父類別
        self.hit_box = "circle"  # 碰撞檢測方式
        self.path = path  # 敵人行走路徑
        self.offset = [  # 偏移量，用於隨機化敵人位置
            random.uniform(-0.2, 0.2) * GRID_SIZE,
            random.uniform(-0.2, 0.2) * GRID_SIZE,
        ]
        self.pos = [  # 敵人當前位置
            path[0][0] * (GRID_SIZE + GRID_GAP) + GRID_SIZE / 2 + self.offset[0],
            path[0][1] * (GRID_SIZE + GRID_GAP) + GRID_SIZE / 2 + self.offset[1],
        ]
        self.speed = 100  # 每秒移動 100 px
        self.radius_ratio = 0.1  # 半徑比例
        self.display_health = self.health = (  # 初始生命值
            100 * (GameState.total_enemy_count + 1) * 0.1  # 敵人會隨著遊戲進行而增強
        )  # 敵人生命值
        self.path_index = 0  # 當前路徑索引
        self.color = random.choice(ENEMY_COLORS)  # 隨機顏色
        self._freeze_time = 0.0  # 凍結時間

    @property
    def radius(self):  # 敵人半徑
        return self.radius_ratio * GRID_SIZE

    @property
    def freeze_time(self):  # 凍結時間屬性
        return self._freeze_time

    @freeze_time.setter  # 設置凍結時間
    def freeze_time(self, value):
        self._freeze_time = max(self._freeze_time, value)  # 確保凍結時間不會減少

    # 更新敵人
    def update(self, dt):
        if self.path_index >= len(self.path):  # 如果已經到達路徑末尾
            GameState.home_health -= 1  # 家的生命值減少
            self.display_health = 0  # 顯示生命值為 0
            super().kill()  # 移除敵人
            return 0, 0

        move_speed = self.speed * dt  # 計算移動速度
        if self.freeze_time > 0:  # 如果有凍結時間
            self._freeze_time -= dt  # 減少凍結時間
            move_speed /= 2  # 凍結時速度減半

        target = [  # 計算目標位置
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

        # 計算移動向量和速度
        if dist < self.speed * dt:
            self.pos = target
            self.path_index += 1
        else:
            self.pos[0] += dx / dist * move_speed
            self.pos[1] += dy / dist * move_speed

        return dx, dy

    # 繪製敵人
    def draw(self, surface, zoom):
        screen_x, screen_y = transform_coordinates(self.pos[0], self.pos[1])
        radius = int(self.radius * zoom)
        pygame.draw.circle(surface, self.color, (screen_x, screen_y), radius)

    # 敵人死亡處理
    def kill(self):
        GameState.money += 1  # 每殺死一個敵人獲得 1 金幣
        super().kill()


# 繼承自 Enemy 的方形敵人類別
class SqureEnemy(Enemy):
    def __init__(self, path):
        super().__init__(path)
        self.hit_box = "circle"  # 使用矩形碰撞檢測
        self.size = (
            GRID_SIZE * self.radius_ratio * 2,
            GRID_SIZE * self.radius_ratio * 2,
        )  # 矩形大小
        self.speed = self.speed * 0.7
        self.health = self.display_health = self.health * 3  # 敵人生命值
        self.rect = pygame.Rect(
            self.pos[0] - GRID_SIZE / 2 + self.offset[0],
            self.pos[1] - GRID_SIZE / 2 + self.offset[1],
            GRID_SIZE * self.radius_ratio * 2,
            GRID_SIZE * self.radius_ratio * 2,
        )
        self.rect.center = self.pos[0], self.pos[1]  # 矩形中心點

    def update(self, dt):
        super().update(dt)

        # 更新矩形位置
        self.rect.center = self.pos[0], self.pos[1]

    def draw(self, surface, zoom):
        screen_x, screen_y = transform_coordinates(self.pos[0], self.pos[1])
        pygame.draw.rect(
            surface,
            self.color,
            (
                screen_x,
                screen_y,
                self.size[0] * zoom,
                self.size[1] * zoom,
            ),
        )


# 三角形敵人類別，繼承自 Enemy
class TriangleEnemy(Enemy):
    triangle_enemy_image = None  # 靜態變量，用於存儲三角形敵人的圖片

    def __init__(self, path):
        super().__init__(path)
        self.hit_box = "circle"  # 使用圓形碰撞檢測
        self.speed = self.speed * 3
        self.health = self.display_health = self.health * 0.5
        self.image = pygame.transform.scale(self.triangle_enemy_image, self.size)
        self.rotate_deg = 0

    @property
    def size(self):
        return (
            self.radius * 2,
            self.radius * 2,
        )

    def update(self, dt):
        dx, dy = super().update(dt)
        angle = math.degrees(math.atan2(-dy, dx))  # 計算角度
        self.rotate_deg = angle

    def draw(self, surface, zoom):
        center_pox = transform_coordinates(self.pos[0], self.pos[1])

        scale_image = pygame.transform.scale(
            self.image, (int(self.size[0] * zoom), int(self.size[1] * zoom))
        )
        rotated_image = pygame.transform.rotate(scale_image, self.rotate_deg)
        image_rect = rotated_image.get_rect(center=center_pox)
        surface.blit(rotated_image, image_rect)


# 藍色三角形敵人類別，繼承自 SqureEnemy
class BlueTriangleEnemy(TriangleEnemy):
    blue_triangle_enemy_image = None

    def __init__(self, path):
        super().__init__(path)
        self.image = pygame.transform.scale(self.blue_triangle_enemy_image, self.size)
        self.color = pygame.Color("#0000ff")  # 藍色三角形敵人

    @property
    def freeze_time(self):
        return 0

    @freeze_time.setter
    def freeze_time(self, value):
        pass  # 藍色三角形敵人不會被凍結


# Boss 敵人類別，繼承自方形敵人和三角形敵人


# 方形 Boss 敵人類別，继承自方形敵人
class BossSquareEnemy(SqureEnemy):
    square_boss_sound = None  # Boss 敵人的音效

    def __init__(self, path):
        super().__init__(path)
        self.color = pygame.Color("#ff0000")  # 紅色方形敵人
        self.health = self.display_health = self.health * 10  # 增加生命值
        self.speed = self.speed * 0.8
        self.radius_ratio = 0.2  # 增加半徑比例
        self.rect.size = (
            GRID_SIZE * self.radius_ratio,
            GRID_SIZE * self.radius_ratio,
        )  # 調整矩形大小
        self.size = (
            GRID_SIZE * self.radius_ratio * 2,
            GRID_SIZE * self.radius_ratio * 2,
        )
        self.square_boss_sound.play()  # 播放 Boss 敵人音效

    def kill(self):
        GameState.money += 100  # 每殺死一個 Boss 獲得 100 金幣
        super().kill()


# Boss 三角形敵人類別，繼承自三角形敵人
class BossTriangleEnemy(TriangleEnemy):
    triangle_boss_sound = None  # Boss 敵人的音效

    def __init__(self, path):
        super().__init__(path)
        self.color = pygame.Color("#ff0000")  # 紅色三角形敵人
        self.health = self.display_health = self.health * 20  # 增加生命值
        self.speed = self.speed * 0.8
        self.radius_ratio = 0.2  # 增加半徑比例
        self.image = pygame.transform.scale(self.triangle_enemy_image, self.size)
        self.triangle_boss_sound.play()

    def kill(self):
        GameState.money += 100  # 每殺死一個 Boss 獲得 100 金幣
        super().kill()
