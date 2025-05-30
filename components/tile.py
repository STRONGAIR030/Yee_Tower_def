import pygame
from constants import GRID_SIZE, GRID_GAP
from game_stat import GameState
from tool.tool_function import screen_to_world_coordinates, transform_coordinates


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
        self.is_select = False

    def update(self, dt):
        mouse_x, mouse_y = screen_to_world_coordinates(
            GameState.mouse_pos[0], GameState.mouse_pos[1]
        )
        hover = self.rect.collidepoint(mouse_x, mouse_y)
        if self.is_select:
            if GameState.left_click or (GameState.right_click and not hover):
                self.is_select = False
                GameState.selected_tile = None
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

        pygame.draw.rect(
            surface,
            color,
            (screen_x, screen_y, GRID_SIZE * zoom, GRID_SIZE * zoom),
            border_radius=int(GRID_SIZE * zoom / 10),  # 圓角邊框,
        )

        if self.is_select:
            pygame.draw.rect(
                surface,
                pygame.Color("#ffeb3b"),
                (screen_x, screen_y, GRID_SIZE * zoom, GRID_SIZE * zoom),
                width=int(5 * zoom),  # 邊框寬度
            )
