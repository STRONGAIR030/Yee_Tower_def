import pygame
from constants import GRID_SIZE, GRID_GAP
from game_stat import GameState
from tool.tool_function import screen_to_world_coordinates, transform_coordinates


# 格子類別，用於管理遊戲中的格子
class Tile:
    def __init__(self, x, y, type="normal"):
        self.x = x  # 格子的 x 座標
        self.y = y  # 格子的 y 座標
        self.type = type  # 格子的類型，默認為 "normal"
        self.can_build = False  # 是否可以建造塔防
        if type == "normal":
            self.can_build = True
        self.builded = False  # 是否已經建造了塔防
        self.pos = (
            x * (GRID_SIZE + GRID_GAP),
            y * (GRID_SIZE + GRID_GAP),
        )  # 格子的世界座標
        self.rect = pygame.Rect(
            x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE
        )  # 格子的矩形範圍
        self.is_select = False  # 是否被選中

    def update(self, dt):
        mouse_x, mouse_y = screen_to_world_coordinates(
            GameState.mouse_pos[0], GameState.mouse_pos[1]
        )
        hover = self.rect.collidepoint(mouse_x, mouse_y)
        # 檢查是否被選中或取消選中
        if self.is_select:
            if (
                GameState.left_click or (GameState.right_click and not hover)
            ) and not GameState.is_on_tower_list:
                self.is_select = False
        elif GameState.right_click and self.can_build and not self.builded:
            if self.can_build and hover:
                self.is_select = True
                GameState.selected_tile = (self.x, self.y)

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

        # 繪製格子
        pygame.draw.rect(
            surface,
            color,
            (screen_x, screen_y, GRID_SIZE * zoom, GRID_SIZE * zoom),
            border_radius=int(GRID_SIZE * zoom / 10),  # 圓角邊框,
        )

        # 如果格子被選中，繪製邊框
        if self.is_select:
            pygame.draw.rect(
                surface,
                pygame.Color("#ffeb3b"),
                (screen_x, screen_y, GRID_SIZE * zoom, GRID_SIZE * zoom),
                width=int(5 * zoom),  # 邊框寬度
            )
