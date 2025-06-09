# 遊戲狀態管理模組
# 此模組用於管理遊戲的各種狀態和參數
class GameState:
    zoom = 1.0  # 畫面縮放比例
    camera_offset = [0, 0]  # 相機偏移量
    dragging = False  # 是否正在拖動相機
    running = True  # 遊戲是否正在運行
    last_mouse_pos = (0, 0)  # 上一次滑鼠位置
    enemy_summon_cooldown = -5  # 敵人生成冷卻時間
    total_enemy_count = 0  # 總敵人數量
    tower_upgrade_cooldown = 0  # 塔防升級冷卻時間
    right_click = False  # 右鍵點擊狀態
    left_click = False  # 左鍵點擊狀態
    mouse_pos = (0, 0)  # 當前滑鼠位置
    money = 200  # 初始金錢
    home_health = 50  # 家園生命值
    selected_tile = None  # 當前選中的格子
    selected_tower = None  # 當前選中的塔防
    is_on_tower_list = False  # 是否在塔防列表中
    is_on_ok_button = False  # 是否在確認按鈕上
    build_tower = 1  # 當前建造的塔防數量
    show_start = True  # 是否顯示開始介面
    start_time = 0  # 開始時間
    end_time = 0  # 結束時間
