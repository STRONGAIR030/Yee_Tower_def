from tkinter import E
import pygame
import math
import random

# 初始化
pygame.init()
screen = pygame.display.set_mode((1200, 1200))
pygame.display.set_caption("Yee Tower Defense")
clock = pygame.time.Clock()


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

GRID_SIZE = 128
GRID_GAP = 5
zoom = 1.0
running = True
camera_offset = [0, 0]
dragging = False
last_mouse_pos = (0, 0)


def transform_coordinates(x, y):
    """將格子座標轉換為螢幕座標"""
    screen_x = int(x * zoom - camera_offset[0])
    screen_y = int(y * zoom - camera_offset[1])
    return [screen_x, screen_y]


def zoom_coordinates(value):
    return int(value * zoom)


class Tile:
    def __init__(self, x, y, type="normal"):
        self.x = x
        self.y = y
        self.type = type
        self.can_build = True  # 是否可以建造塔防
        if type == "path":
            self.can_build = False
        self.builded = False  # 是否已經建造了塔防
        self.pos = (x * (GRID_SIZE + GRID_GAP), y * (GRID_SIZE + GRID_GAP))
        self.rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)

    def draw(self, surface, zoom):
        screen_x, screen_y = transform_coordinates(self.pos[0], self.pos[1])

        # 根據類型選擇顏色
        color = pygame.Color("#4aca8b")
        if self.type == "normal":
            color = (
                pygame.Color("#4aca8b") if not self.builded else pygame.Color("#4aca8b")
            )
        elif self.type == "path":
            color = pygame.Color("#e8f5e9")
        elif self.type == "home":
            color = pygame.Color("#0000ff")
        elif self.type == "enemy_summon":
            color = pygame.Color("#ff00ff")

        pygame.draw.rect(
            surface,
            color,
            (screen_x, screen_y, GRID_SIZE * zoom, GRID_SIZE * zoom),
            border_radius=int(GRID_SIZE * zoom / 10),  # 圓角邊框,
        )


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, target: "Enemy"):
        super().__init__()
        self.original_image = pygame.Surface((10, 10), pygame.SRCALPHA)
        self.image = self.original_image.copy()
        pygame.draw.circle(self.original_image, (255, 0, 0), (5, 5), 5)
        self.rect = self.image.get_rect(center=pos)
        self.pos = list(pos)
        self.target = target
        self.speed = 300  # 每秒移動 300 pixels

    def update(self, dt):
        target_pos = self.target.pos
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist < self.speed * dt:
            self.pos = target_pos
            self.rect.center = target_pos
        else:
            self.pos[0] += dx / dist * self.speed * dt
            self.pos[1] += dy / dist * self.speed * dt

    def draw(self, surface):
        w = zoom_coordinates(self.original_image.get_width())
        h = zoom_coordinates(self.original_image.get_height())
        scaled_image = pygame.transform.smoothscale(self.original_image, (w, h))
        sx, sy = transform_coordinates(self.pos[0], self.pos[1])
        rect = scaled_image.get_rect(center=(int(sx), int(sy)))
        surface.blit(scaled_image, rect)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, path, health=100):
        super().__init__()
        self.display_health = health  # 顯示生命值
        self.health = health  # 實際生命值
        self.original_image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.path = path
        self.current_index = 0
        self.speed = 200  # 每秒 200 px
        self.radius_ratio = 0.1  # 相對於格子 大小
        self.offset = [
            random.uniform(-0.1, 0.1) * GRID_SIZE,
            random.uniform(-0.1, 0.1) * GRID_SIZE,
        ]  # 加入隨機偏移
        self.pos = [
            path[0][0] * GRID_SIZE + GRID_SIZE / 2 + self.offset[0],
            path[0][1] * GRID_SIZE + GRID_SIZE / 2 + self.offset[1],
        ]
        self.rect.center = (self.pos[0], self.pos[1])
        pygame.draw.circle(
            self.original_image,
            (0, 255, 0),
            (25, 25),
            int(GRID_SIZE * self.radius_ratio),
        )

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
            self.rect.center = target
            self.current_index += 1
        else:
            self.pos[0] += dx / dist * self.speed * dt
            self.pos[1] += dy / dist * self.speed * dt

    def draw(self, surface):
        w = zoom_coordinates(self.original_image.get_width())
        h = zoom_coordinates(self.original_image.get_height())
        scaled_image = pygame.transform.smoothscale(self.original_image, (w, h))
        sx, sy = transform_coordinates(self.pos[0], self.pos[1])
        rect = scaled_image.get_rect(center=(int(sx), int(sy)))
        surface.blit(scaled_image, rect)


class Tower:
    def __init__(self, grid_pos):
        self.atk = 1
        self.pos = [
            grid_pos[0] * GRID_SIZE + GRID_SIZE / 2,
            grid_pos[1] * GRID_SIZE + GRID_SIZE / 2,
        ]
        self.radius = GRID_SIZE * 3.0  # 塔的攻擊範圍
        self.shoot_cooldown = 0.0  # 每秒可以射擊一次
        self.shoot_rate = 10

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
            (0, 255, 0),
            (screen_x, screen_y),
            int(GRID_SIZE / 2 * zoom),
            2,
        )
        pygame.draw.circle(
            surface, (0, 255, 0), (screen_x, screen_y), int(self.radius * zoom), 1
        )

    def shoot(self, enemies, bullets) -> bool:
        for enemy in enemies:
            dx = enemy.pos[0] - self.pos[0]
            dy = enemy.pos[1] - self.pos[1]
            dist = math.hypot(dx, dy)
            if dist <= self.radius and enemy.health > 0:
                enemy.health -= self.atk  # 對敵人造成傷害
                target = enemy
                new_bullet = Bullet([self.pos[0], self.pos[1]], target)
                bullets.add(new_bullet)
                return True  # 成功射擊

        return False  # 沒有敵人可以射擊


enemy_group = pygame.sprite.Group()
for path in [PATH_1, PATH_2]:
    enemy = Enemy(path)
    enemy_group.add(enemy)
bullets = pygame.sprite.Group()
towers = [Tower((2, 3)), Tower((4, 5))]


while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            dragging = True
            last_mouse_pos = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            dragging = False
        elif event.type == pygame.MOUSEMOTION and dragging:
            current_mouse_pos = pygame.mouse.get_pos()
            dx = last_mouse_pos[0] - current_mouse_pos[0]
            dy = last_mouse_pos[1] - current_mouse_pos[1]
            camera_offset[0] += dx
            camera_offset[1] += dy
            last_mouse_pos = current_mouse_pos
        elif event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            wordx = (mx + camera_offset[0]) / zoom
            wordy = (my + camera_offset[1]) / zoom
            zoom += event.y * 0.1
            zoom = max(0.5, min(5.0, zoom))
            camera_offset[0] = wordx * zoom - mx
            camera_offset[1] = wordy * zoom - my

    screen.fill((200, 200, 200))

    # 更新敵人
    enemy_group.update(dt)
    bullets.update(dt)
    for tower in towers:
        tower.update(dt, enemy_group, bullets)

    collided_enemies = pygame.sprite.groupcollide(bullets, enemy_group, False, False)
    for bullet, enemies in collided_enemies.items():
        for enemy in enemies:
            enemy.display_health -= 1  # 子彈擊中敵人，減少生命值
            print(f"Enemy health: {enemy.display_health} , real health: {enemy.health}")
            if enemy.display_health <= 0:
                enemy.kill()  # 如果生命值小於等於0，則移除敵人

        bullet.kill()  # 子彈擊中敵人後移除子彈

    # 繪製格子
    for x in range(10):
        for y in range(10):
            if (x, y) == HOME_PATH:
                tile_type = "home"
            elif (x, y) == ENEMY_SUMMON_PATH_1 or (x, y) == ENEMY_SUMMON_PATH_2:
                tile_type = "enemy_summon"
            elif (x, y) in PATH_1 or (x, y) in PATH_2:
                tile_type = "path"
            else:
                tile_type = "normal"
            tile = Tile(x, y, type=tile_type)
            tile.draw(screen, zoom)

    for enemy in enemy_group:
        enemy.draw(screen)

    for bullet in bullets:
        bullet.draw(screen)

    for tower in towers:
        tower.draw(screen, zoom)

    pygame.display.flip()  # 顯示整個畫面內容

pygame.quit()  # 結束遊戲
