from calendar import c
import re
from tokenize import group
from typing import List
import pygame
import math
import random

# 初始化
pygame.init()
screen = pygame.display.set_mode((1200, 1200))
pygame.display.set_caption("Tower Defense - Enemies on Grid Path")
clock = pygame.time.Clock()

GRID_SIZE = 64
ZOOM = 1.0
camera_offset = [0, 0]
dragging = False
last_mouse_pos = (0, 0)

# 路徑節點（格子座標）
HOME_PATH = (5, 4)
ENEMY_SUMMON_PATH_1 = (1, 1)
ENEMY_SUMMON_PATH_2 = (8, 8)
PATH_1 = [
    ENEMY_SUMMON_PATH_1,
    (2, 1),
    (3, 1),
    (4, 1),
    (5, 1),
    (5, 2),
    (6, 2),
    (7, 2),
    (8, 2),
    (8, 3),
    (8, 4),
    (8, 5),
    (7, 5),
    (6, 5),
    (6, 4),
    HOME_PATH,
]

PATH_2 = [
    ENEMY_SUMMON_PATH_2,
    (8, 7),
    (7, 7),
    (6, 7),
    (6, 8),
    (5, 8),
    (4, 8),
    (3, 8),
    (3, 7),
    (3, 6),
    (2, 6),
    (1, 6),
    (1, 5),
    (1, 4),
    (2, 4),
    (3, 4),
    (4, 4),
    HOME_PATH,
]


def check_hit(pos, radius, enemise):
    for enemy in enemise:
        dx = enemy.pos[0] - pos[0]
        dy = enemy.pos[1] - pos[1]
        dist = math.hypot(dx, dy)
        if dist <= radius:
            return True
    return False


class BoxItem:
    def __init__(self, pos, size, radius, box: "ItemBox" = None):
        self.box: "ItemBox" = box
        self.pos = pos
        self.size = size
        self.radius = radius
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])

    def draw(self, surface, zoom, offset):
        pass

    def update(self, dt):
        pass

    def kill(self):
        if self.box is not None:
            self.box.remove(self)
        else:
            print("No group to remove from")
        print("Item killed")
        # 在這裡可以添加更多邏輯，例如增加分數或播放音效


class ItemBox:
    def __init__(self):
        self.box: List["BoxItem"] = []

    def add(self, item: "BoxItem"):
        self.box.append(item)
        item.box = self

    def remove(self, item: "BoxItem"):
        if item not in self.box:
            print("Item not found in box")
            return
        self.box.remove(item)

    def update(self, dt):
        for item in self.box:
            item.update(dt)

    def __len__(self):
        return len(self.box)

    def __iter__(self):
        return iter(self.box)


class Bullet(BoxItem):
    def __init__(self, pos, target):
        super().__init__(pos, (10, 10), 5)
        self.pos = pos
        self.target = target
        self.speed = 300  # 每秒移動 300 pixels

    def update(self, dt):
        target_pos = self.target.pos
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist < self.speed * dt:
            self.pos = target_pos
        else:
            self.pos[0] += dx / dist * self.speed * dt
            self.pos[1] += dy / dist * self.speed * dt

        if check_hit(self.pos, 5, [self.target]):
            self.target.health -= 1
            print(
                f"Enemy health: {self.target.health} tset_health: {self.target.test_health}"
            )
            self.kill()
        if self.target.health <= 0:
            self.target.kill()

    def draw(self, surface, zoom, offset):
        screen_x = int(self.pos[0] * zoom + offset[0])
        screen_y = int(self.pos[1] * zoom + offset[1])
        pygame.draw.circle(surface, (255, 255, 0), (screen_x, screen_y), int(5 * zoom))


# 敵人類別
class Enemy(BoxItem):
    def __init__(self, path):
        self.health = 100
        self.test_health = 100
        self.path = path
        self.current_index = 0
        self.speed = 200  # 每秒 100 px
        self.radius_ratio = 0.1  # 相對於格子大小
        self.offset = [
            random.uniform(-0.1, 0.1) * GRID_SIZE,
            random.uniform(-0.1, 0.1) * GRID_SIZE,
        ]  # 加入隨機偏移
        self.pos = [
            path[0][0] * GRID_SIZE + GRID_SIZE / 2 + self.offset[0],
            path[0][1] * GRID_SIZE + GRID_SIZE / 2 + self.offset[1],
        ]
        self.size = (GRID_SIZE, GRID_SIZE)
        self.radius = int(GRID_SIZE * self.radius_ratio)

    def update(self, dt):
        if self.current_index >= len(self.path) - 1:
            self.current_index = 0
        target = [
            self.path[self.current_index + 1][0] * GRID_SIZE
            + GRID_SIZE / 2
            + self.offset[0],
            self.path[self.current_index + 1][1] * GRID_SIZE
            + GRID_SIZE / 2
            + self.offset[1],
        ]
        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist < self.speed * dt:
            self.pos = target
            self.current_index += 1
        else:
            self.pos[0] += dx / dist * self.speed * dt
            self.pos[1] += dy / dist * self.speed * dt

    def draw(self, surface, zoom, offset):
        radius = int(GRID_SIZE * self.radius_ratio * zoom)
        screen_x = int(self.pos[0] * zoom + offset[0])
        screen_y = int(self.pos[1] * zoom + offset[1])
        pygame.draw.circle(surface, (255, 100, 100), (screen_x, screen_y), radius)


class Tower:
    def __init__(self, grid_pos):
        self.pos = [
            grid_pos[0] * GRID_SIZE + GRID_SIZE / 2,
            grid_pos[1] * GRID_SIZE + GRID_SIZE / 2,
        ]
        self.radius = GRID_SIZE * 3  # 塔的攻擊範圍
        self.shoot_cooldown = 0.0  # 每秒可以射擊一次
        self.shoot_rate = 10

    def update(self, dt, enemies, bullets):
        self.shoot_cooldown += dt
        if self.shoot_cooldown >= 1 / self.shoot_rate:
            shoot = self.shoot(enemies=enemies, bullets=bullets)
            if shoot:
                self.shoot_cooldown = 0.0

    def draw(self, surface, zoom, offset):
        screen_x = int(self.pos[0] * zoom + offset[0])
        screen_y = int(self.pos[1] * zoom + offset[1])
        pygame.draw.circle(
            surface,
            (0, 255, 0),
            (screen_x, screen_y),
            int(GRID_SIZE / 2 * zoom),
            2,
        )
        pygame.draw.circle(
            surface, (0, 255, 0), (screen_x, screen_y), int(self.radius * zoom), 1
        )

    def shoot(self, enemies: "ItemBox", bullets: "ItemBox") -> bool:
        for enemy in enemies:
            dx = enemy.pos[0] - self.pos[0]
            dy = enemy.pos[1] - self.pos[1]
            dist = math.hypot(dx, dy)
            if dist <= self.radius and enemy.test_health > 0:
                target = enemy
                enemy.test_health -= 1
                new_bullet = Bullet([self.pos[0], self.pos[1]], target)
                bullets.add(new_bullet)
                return True  # 成功射擊

        return False  # 沒有敵人可以射擊


# 建立多個敵人
enemies = ItemBox()
towers = [Tower((2, 3)), Tower((4, 5))]
bullets = ItemBox()
enemy_cooldown = 0.0
enemy_spawn_rate = 1.0  # 每秒生成一個敵人

running = True
while running:
    dt = clock.tick(60) / 1000
    enemy_cooldown += dt
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                dragging = True
                last_mouse_pos = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False
        elif event.type == pygame.MOUSEMOTION and dragging:
            current = pygame.mouse.get_pos()
            # 滑鼠移動的距離 = 相機偏移量
            dx = last_mouse_pos[0] - current[0]
            dy = last_mouse_pos[1] - current[1]
            camera_offset[0] -= dx
            camera_offset[1] -= dy
            last_mouse_pos = current
        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_x = (mouse_x - camera_offset[0]) / ZOOM
            world_y = (mouse_y - camera_offset[1]) / ZOOM
            ZOOM += event.y * 0.1
            ZOOM = max(0.1, min(10, ZOOM))
            camera_offset[0] = -(world_x * ZOOM - mouse_x)
            camera_offset[1] = -(world_y * ZOOM - mouse_y)

    if len(enemies) < 5 and enemy_cooldown >= enemy_spawn_rate:  # 限制最多10個敵人
        new_enemy = Enemy(random.choice([PATH_1, PATH_2]))
        enemies.add(new_enemy)
        enemy_cooldown = 0.0

    for enemy in enemies:
        enemy.update(dt)

    for tower in towers:
        tower.update(dt, enemies, bullets)

    for bullet in bullets:
        bullet.update(dt)

    screen.fill((30, 30, 30))

    # 畫格線
    for y in range(13):
        for x in range(13):
            rect = pygame.Rect(
                x * GRID_SIZE * ZOOM + camera_offset[0],
                y * GRID_SIZE * ZOOM + camera_offset[1],
                GRID_SIZE * ZOOM,
                GRID_SIZE * ZOOM,
            )
            pygame.draw.rect(screen, (50, 50, 50), rect, 1)

    # 畫路徑
    # for i in range(len(path) - 1):
    #     start = (
    #         path[i][0] * GRID_SIZE * ZOOM + GRID_SIZE * ZOOM / 2 + camera_offset[0],
    #         path[i][1] * GRID_SIZE * ZOOM + GRID_SIZE * ZOOM / 2 + camera_offset[1],
    #     )
    #     end = (
    #         path[i + 1][0] * GRID_SIZE * ZOOM + GRID_SIZE * ZOOM / 2 + camera_offset[0],
    #         path[i + 1][1] * GRID_SIZE * ZOOM + GRID_SIZE * ZOOM / 2 + camera_offset[1],
    #     )
    #     pygame.draw.line(screen, (200, 200, 0), start, end, 5)

    for enemy in enemies:
        enemy.draw(screen, ZOOM, camera_offset)

    for tower in towers:
        tower.draw(screen, ZOOM, camera_offset)

    for bullet in bullets:
        bullet.draw(screen, ZOOM, camera_offset)

    pygame.display.flip()

pygame.quit()
