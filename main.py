import pygame
import random
from components.bullet import StarBullet
from components.tower_list import OkButton, TowerList
from constants import (
    PATH_1,
    PATH_2,
    HOME_PATH,
    ENEMY_SUMMON_PATH_1,
    ENEMY_SUMMON_PATH_2,
    SCREEN_WIDTH,
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
from tool.tool_function import check_hit_group, get_price, load_image
from components.tile import Tile


# 初始化
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_WIDTH))
pygame.display.set_caption("Yee Tower Defense")
clock = pygame.time.Clock()

# 載入圖片
StarBullet.star_bullet_image = load_image("star_bullet.png")
TriangleEnemy.triangle_enemy_image = load_image("triangle_enemy.png")
BlueTriangleEnemy.blue_triangle_enemy_image = load_image("blue_triangle_enemy.png")
TriangleTower.triangle_tower_image = load_image("triangle_tower.png")
RatctangleTower.ractangle_tower_image = load_image("ractangle_tower.png")
PentagonTower.pentagon_tower_image = load_image("pentagon_tower.png")
StarTower.star_tower_image = load_image("star_bullet.png")
OkButton.ok_button_image = load_image("ok_button.png")

# 遊戲物件群主
tower_buy_list = TowerList()  # 塔防購買列表
tower_select_list = [  # 塔防選擇列表
    # Tower,
    # TriangleTower,
    # SquareTower,
    # StarTower,
    # PentagonTower,
    # RatctangleTower,
]
enemy_group = ItemGroup()  # 敵人群組
bullets = ItemGroup()  # 子彈群組
towers = [
    TriangleTower((0, 0)),  # 初始塔防
    SquareTower((1, 0)),
    StarTower((2, 0)),
    PentagonTower((3, 0)),
    RatctangleTower((4, 0)),
]  # 塔的列表
tile_list = []  # 地圖格子列表
# 可選擇的敵人和Boss列表
enemy_list = [Enemy, TriangleEnemy, SqureEnemy, BlueTriangleEnemy]
boss_list = [BossSquareEnemy, BossTriangleEnemy]

# 初始化格子
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

# 主遊戲循環
while GameState.running:
    dt = clock.tick(60) / 1000  # 獲取每幀時間間隔
    GameState.enemy_summon_cooldown += dt  # 更新敵人生成冷卻時間
    GameState.tower_upgrade_cooldown += dt  # 更新塔防升級冷卻時間
    GameState.mouse_pos = pygame.mouse.get_pos()  # 更新滑鼠位置

    # 處理事件
    for event in pygame.event.get():
        # 滑鼠右建按下和放開事件
        if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            GameState.right_click = True
        else:
            GameState.right_click = False
        # 滑鼠左鍵按下和放開事件
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            GameState.left_click = True
        else:
            GameState.left_click = False
        if event.type == pygame.QUIT:  # 檢查是否關閉遊戲窗口
            GameState.running = False
        elif (
            event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        ):  # 檢查左鍵按下事件
            GameState.dragging = True
            last_mouse_pos = pygame.mouse.get_pos()
        elif (
            event.type == pygame.MOUSEBUTTONUP and event.button == 1
        ):  # 檢查左鍵放開事件
            GameState.dragging = False
        elif event.type == pygame.MOUSEMOTION and GameState.dragging:  # 處理相機拖動
            dx = last_mouse_pos[0] - GameState.mouse_pos[0]
            dy = last_mouse_pos[1] - GameState.mouse_pos[1]
            GameState.camera_offset[0] += dx
            GameState.camera_offset[1] += dy
            last_mouse_pos = GameState.mouse_pos
        elif event.type == pygame.MOUSEWHEEL:  # 處理相機縮放
            mx, my = pygame.mouse.get_pos()
            wordx = (mx + GameState.camera_offset[0]) / GameState.zoom
            wordy = (my + GameState.camera_offset[1]) / GameState.zoom
            GameState.zoom += event.y * 0.1
            GameState.zoom = max(0.5, min(5.0, GameState.zoom))
            GameState.camera_offset[0] = wordx * GameState.zoom - mx
            GameState.camera_offset[1] = wordy * GameState.zoom - my

    screen.fill((200, 200, 200))  # 填充背景顏色
    overlay = pygame.Surface((1200, 1200), pygame.SRCALPHA)  # 創建透明覆蓋層

    if GameState.home_health < 0:  # 檢查家園生命值是否小於 0
        GameState.running = False  # 結束遊戲循環

    if GameState.enemy_summon_cooldown > 0.5 and len(enemy_group) < 30:
        # 每 1 秒生成一個敵人，最多 10 個
        selected_list = enemy_list
        # 每生成 100 隻敵人，生成一隻 Boss
        if GameState.total_enemy_count % 100 == 0 and GameState.total_enemy_count > 0:
            selected_list = boss_list
        selected_enemy = random.choice(selected_list)  # 隨機選擇敵人類型
        enemy = selected_enemy(random.choice([PATH_1, PATH_2]))
        enemy_group.add(enemy)  # 將敵人添加到敵人群組中

        GameState.total_enemy_count += 1  # 增加總敵人數量
        GameState.enemy_summon_cooldown = 0.0  # 重置敵人生成冷卻時間

    # 每隔 0.5 秒隨機升級一個塔
    if GameState.tower_upgrade_cooldown > 0.5:
        if len(towers) > 0:
            tower = random.choice(towers)
            tower.upgrade()
        GameState.tower_upgrade_cooldown = 0.0

    # 更新物件

    # 更新格子
    for tile in tile_list:
        tile.update(dt)

    tower_buy_list.update(dt)  # 更新塔防購買UI
    if all(not tile.is_select for tile in tile_list):  # 如果沒有格子被選中
        GameState.selected_tile = None
    enemy_group.update(dt)  # 更新敵人群組
    bullets.update(dt)  # 更新子彈群組

    # 更新是否要建造新的塔
    if GameState.is_on_ok_button and GameState.left_click:
        for item in tower_buy_list.tower_items:
            if item.is_selected:
                select_tower = tower_select_list[item.tower_id]
                if GameState.money >= get_price(
                    GameState.build_tower, select_tower.base_price
                ):  # 檢查是否有足夠的金錢建造塔
                    GameState.build_tower += 1
                    GameState.money -= select_tower.base_price  # 減少金錢
                    new_tower = select_tower(GameState.selected_tile)
                    towers.append(new_tower)
                # 重製狀態
                GameState.is_on_ok_button = False
                GameState.is_on_tower_list = False
                GameState.selected_tile = None
                break

    # 更新塔
    for tower in towers:
        tower.update(dt, enemy_group, bullets)

    # 檢查敵人是否死亡
    for enemy in enemy_group:
        if enemy.display_health <= 0:
            enemy.kill()  # kill 敵人

    # 檢查子彈是否擊中敵人
    hits = check_hit_group(enemy_group, bullets.group)
    for enemy, bullet in hits.items():
        if bullet.has_target and bullet.target is not enemy:
            continue  # 如果子彈有目標且目標不是當前敵人，則跳過

        if bullet.is_effect:
            if bullet.is_hitted(enemy):
                continue  # 如果子彈是效果類型且已經擊中敵人，則跳過，防止重複計算傷害

            bullet.add_hit_enemy(enemy)  # 添加已擊中敵人，防止重複計算傷害

        if not bullet.has_target:  # 如果不是追蹤目標的子彈
            enemy.health -= bullet.atk  # 減少敵人生命值

        enemy.display_health -= bullet.atk  # 減少敵人顯示生命值

        if enemy.display_health <= 0:  # 如果敵人生命值小於等於 0
            enemy.kill()  # 假設有 kill 方法來處理死亡
        if not bullet.is_effect:  # 如果不是效果類型的子彈
            bullet.kill()  # 移除子彈

    font = pygame.font.Font(None, 24)  # 創建字體對象
    text_surface1 = font.render(
        f"money: {GameState.money}", True, (0, 0, 0)
    )  # 渲染金錢文字
    text_surface2 = font.render(
        f"health: {GameState.home_health}", True, (0, 0, 0)
    )  # 渲染家園生命值文字

    text_rect1 = text_surface1.get_rect()  # 獲取文字矩形
    text_rect1.topleft = (20, 20)  # 設置文字位置
    text_rect2 = text_surface2.get_rect()  # 獲取文字矩形
    text_rect2.topright = (SCREEN_WIDTH - 20, 20)  # 設置文字位置

    # 繪製所有物件
    # 繪製格子
    for tile in tile_list:
        tile.draw(overlay, GameState.zoom)

    # 繪製塔防
    for tower in towers:
        tower.draw(overlay, GameState.zoom)
    # 繪製敵人和子彈
    for enemy in enemy_group:
        enemy.draw(overlay, GameState.zoom)
    # 繪製子彈
    for bullet in bullets:
        bullet.draw(overlay, GameState.zoom)
    tower_buy_list.draw(overlay)  # 繪製塔防購買UI

    screen.blit(overlay, (0, 0))  # 將覆蓋層繪製到屏幕上
    screen.blit(text_surface1, text_rect1)  # 繪製金錢文字
    screen.blit(text_surface2, text_rect2)  # 繪製家園生命值文字
    pygame.display.flip()  # 顯示整個畫面內容

pygame.quit()  # 結束遊戲
print("Game over")  # 打印遊戲結束信息
