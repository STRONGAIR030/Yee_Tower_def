import pygame
import random
from components.bullet import StarBullet
from components.tower_list import TowerList
from constants import (
    PATH_1,
    PATH_2,
    HOME_PATH,
    ENEMY_SUMMON_PATH_1,
    ENEMY_SUMMON_PATH_2,
)
from components.enemy import (
    BlueTriangleEnemy,
    BossSquareEnemy,
    BossTriangleEnemy,
    Enemy,
    SqureEnemy,
    TriangleEnemy,
)
from game_stat import GameState
from components.tower import (
    PentagonTower,
    RatctangleTower,
    SquareTower,
    StarTower,
    Tower,
    TriangleTower,
)
from components.Item_group import ItemGroup
from tool.tool_function import check_hit_group, check_hit_radius_group, load_image
from components.tile import Tile


# 初始化
pygame.init()
screen = pygame.display.set_mode((1200, 1200))
pygame.display.set_caption("Yee Tower Defense")
clock = pygame.time.Clock()

StarBullet.star_bullet_image = load_image("star_bullet.png")  # 載入星形子彈圖片
TriangleEnemy.triangle_enemy_image = load_image(
    "triangle_enemy.png"
)  # 載入三角形敵人圖片
BlueTriangleEnemy.blue_triangle_enemy_image = load_image(
    "blue_triangle_enemy.png"
)  # 載入藍色三角形敵人圖片
TriangleTower.triangle_tower_image = load_image("triangle_tower.png")
RatctangleTower.ractangle_tower_image = load_image("ractangle_tower.png")
PentagonTower.pentagon_tower_image = load_image("pentagon_tower.png")
StarTower.star_tower_image = load_image("star_bullet.png")

tower_buy_list = TowerList()

enemy_group = ItemGroup()  # 敵人群組
bullets = ItemGroup()  # 子彈群組
towers = [
    # Tower((2, 3)),
    # Tower((4, 5)),
    # TriangleTower((0, 7)),
    # SquareTower((4, 7)),
    # StarTower((5, 5)),
    # PentagonTower((6, 6)),
    # RatctangleTower((6, 1)),
]  # 塔的列表
tile_list = []
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
        tile_list.append(tile)


while GameState.running:
    dt = clock.tick(60) / 1000
    GameState.enemy_summon_cooldown += dt  # 更新敵人生成冷卻時間
    GameState.mouse_pos = pygame.mouse.get_pos()  # 更新滑鼠位置

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            GameState.right_click = True
        else:
            GameState.right_click = False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            GameState.left_click = True
        else:
            GameState.left_click = False

        if event.type == pygame.QUIT:
            GameState.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            GameState.dragging = True
            last_mouse_pos = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            GameState.dragging = False
        elif event.type == pygame.MOUSEMOTION and GameState.dragging:
            dx = last_mouse_pos[0] - GameState.mouse_pos[0]
            dy = last_mouse_pos[1] - GameState.mouse_pos[1]
            GameState.camera_offset[0] += dx
            GameState.camera_offset[1] += dy
            last_mouse_pos = GameState.mouse_pos
        elif event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            wordx = (mx + GameState.camera_offset[0]) / GameState.zoom
            wordy = (my + GameState.camera_offset[1]) / GameState.zoom
            GameState.zoom += event.y * 0.1
            GameState.zoom = max(0.5, min(5.0, GameState.zoom))
            GameState.camera_offset[0] = wordx * GameState.zoom - mx
            GameState.camera_offset[1] = wordy * GameState.zoom - my

    screen.fill((200, 200, 200))
    overlay = pygame.Surface((1200, 1200), pygame.SRCALPHA)

    if GameState.enemy_summon_cooldown > 0.5 and len(enemy_group) < 4:
        # 每 1 秒生成一個敵人，最多 10 個
        enemy = BossSquareEnemy(random.choice([PATH_1, PATH_2]))
        enemy_group.add(enemy)
        for tower in towers:
            tower.upgrade()
            tower.upgrade()
        GameState.enemy_summon_cooldown = 0.0

    # 更新敵人
    for tile in tile_list:
        tile.update(dt)
    enemy_group.update(dt)
    bullets.update(dt)
    for tower in towers:
        tower.update(dt, enemy_group, bullets)

    for enemy in enemy_group:
        if enemy.display_health <= 0:
            enemy.kill()

    hits = check_hit_group(enemy_group, bullets.group)
    for enemy, bullet in hits.items():
        if bullet.has_target and bullet.target is not enemy:
            continue

        if bullet.is_effect:
            if bullet.is_hitted(enemy):
                continue

            bullet.add_hit_enemy(enemy)

        if not bullet.has_target:
            enemy.health -= bullet.atk

        enemy.display_health -= bullet.atk

        if enemy.display_health <= 0:
            enemy.kill()  # 假設有 kill 方法來處理死亡
        if not bullet.is_effect:
            bullet.kill()  # 移除子彈
        print(
            f"health: {enemy.health}, display_health: {enemy.display_health}, atk: {bullet.atk}"
        )

    # 繪製格子
    tower_buy_list.draw(overlay, GameState.zoom)
    for tile in tile_list:
        tile.draw(overlay, GameState.zoom)

    for tower in towers:
        tower.draw(overlay, GameState.zoom)

    for enemy in enemy_group:
        enemy.draw(overlay, GameState.zoom)

    for bullet in bullets:
        bullet.draw(overlay, GameState.zoom)

    screen.blit(overlay, (0, 0))
    pygame.display.flip()  # 顯示整個畫面內容

pygame.quit()  # 結束遊戲
