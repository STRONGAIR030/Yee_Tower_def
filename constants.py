import os

# 遊戲常數設定
SCREEN_WIDTH = 800  # 寬度
SCREEN_HEIGHT = 800  # 高度
GAME_FPS = 60  # 幀率
HOME_PATH = (5, 4)  # 家園位置
ENEMY_SUMMON_PATH_1 = (1, 1)  # 敵人生成位置1
ENEMY_SUMMON_PATH_2 = (8, 8)  # 敵人生成位置2
PATH_1 = [  # 生成敵人位置1的路徑
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

PATH_2 = [  # 生成敵人位置2的路徑
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
ENEMY_COLORS = [(255, 100, 100), (100, 255, 100), (100, 100, 255)]  # 敵人顏色列表
GRID_SIZE = SCREEN_WIDTH / 10  # 每個格子的大小
GRID_GAP = 5  # 格子之間的間距
MAP_SIZE = 10  # 地圖大小（格子數量）
MAP_REAL_SIZE = [  # 實際地圖大小
    (GRID_SIZE + GRID_GAP) * MAP_SIZE,
    (GRID_SIZE + GRID_GAP) * MAP_SIZE,
]
IMAGE_PATH = os.path.join(os.path.dirname(__file__), "assets", "images")  # 圖片資源路徑
SOUND_PATH = os.path.join(os.path.dirname(__file__), "assets", "sounds")  # 圖片資源路徑
