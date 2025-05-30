import os

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1200
GAME_FPS = 60
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
ENEMY_COLORS = [(255, 100, 100), (100, 255, 100), (100, 100, 255)]
GRID_SIZE = 128
GRID_GAP = 5
MAP_SIZE = 10
MAP_REAL_SIZE = [
    (GRID_SIZE + GRID_GAP) * MAP_SIZE,
    (GRID_SIZE + GRID_GAP) * MAP_SIZE,
]
IMAGE_PATH = os.path.join(os.path.dirname(__file__), "assets", "images")
