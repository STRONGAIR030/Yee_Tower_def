import pygame

from components.tower import PentagonTower, RatctangleTower, StarTower, TriangleTower
from constants import GRID_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH
from game_stat import GameState


class TowerListItem:
    def __init__(self, tower_id, pos, type, color=None, image=None, zoom=1):
        self.tower_id = tower_id
        self.zoom = 0.8
        self.pos = pos
        self.type = type
        self.color = color
        self.image = image
        self.radius = GRID_SIZE / 2 * zoom * self.zoom
        self.size = (GRID_SIZE * zoom, GRID_SIZE * zoom)
        self.boerder_rect = pygame.Rect(
            self.pos[0] - GRID_SIZE / 2,
            self.pos[1] - GRID_SIZE / 2,
            self.size[0],
            self.size[1],
        )
        self.boerder_rect.center = (self.pos[0], self.pos[1])
        self.real_size = (self.size[0] * self.zoom, self.size[1] * self.zoom)
        self.is_selected = False
        if self.image:
            self.image = pygame.transform.scale(self.image, self.size)

    def update(self, dt):
        hover = self.boerder_rect.collidepoint(
            GameState.mouse_pos[0], GameState.mouse_pos[1]
        )

        if GameState.selected_tile and hover and GameState.left_click:
            self.is_selected = True

        if (
            self.is_selected
            and not hover
            and not GameState.is_on_ok_button
            and GameState.left_click
        ) or not GameState.selected_tile:
            self.is_selected = False

    def draw(self, surface):
        if self.type == "circle":
            pygame.draw.circle(
                surface,
                self.color,
                (self.pos[0], self.pos[1]),
                int(self.radius),
            )
        elif self.type == "rect":
            rect = pygame.Rect(
                self.pos[0] - GRID_SIZE / 2,
                self.pos[1] - GRID_SIZE / 2,
                self.real_size[0],
                self.real_size[1],
            )
            rect.center = (self.pos[0], self.pos[1])
            pygame.draw.rect(
                surface,
                self.color,
                rect,
            )
        elif self.type == "image" and self.image:
            scale_image = pygame.transform.scale(self.image, self.real_size)
            image_rect = scale_image.get_rect(center=(self.pos[0], self.pos[1]))
            surface.blit(scale_image, image_rect)

        self.boerder_rect.center = (self.pos[0], self.pos[1])
        color = pygame.Color("#000000")
        border = 2
        if self.is_selected:
            color = pygame.Color("#ffeb3b")
            border = 5
        pygame.draw.rect(
            surface,
            color,
            self.boerder_rect,
            border,
        )


class OkButton:
    ok_button_image = None

    def __init__(self, pos):
        self.pos = pos
        self.size = (50, 50)
        self.can_draw = True
        self.image = pygame.transform.scale(self.ok_button_image, self.size)

    @property
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    @property
    def hover(self):
        return self.rect.collidepoint(GameState.mouse_pos[0], GameState.mouse_pos[1])

    def draw(self, surface):
        surface.blit(self.image, self.pos)


class TowerList:
    def __init__(self):
        zoom = 1
        self.can_draw = False
        self.ok_button = OkButton((0, 0))
        self.pos = (0, SCREEN_HEIGHT * 0.8)
        self.size = (SCREEN_WIDTH, SCREEN_HEIGHT * 0.2)
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        self.gap = 40
        circle_tower = TowerListItem(
            tower_id=0,
            type="circle",
            pos=(
                GRID_SIZE * 1.5,
                GRID_SIZE * 1.5,
            ),
            color=(0, 255, 0),
            zoom=zoom,
        )
        triangle_tower = TowerListItem(
            tower_id=1,
            type="image",
            pos=(
                GRID_SIZE * 1.5,
                GRID_SIZE * 3.5,
            ),
            image=TriangleTower.triangle_tower_image,
            zoom=zoom,
        )
        square_tower = TowerListItem(
            tower_id=2,
            type="rect",
            pos=(
                GRID_SIZE * 3.5,
                GRID_SIZE * 1.5,
            ),
            color=pygame.Color("#ff0000"),
            zoom=zoom,
        )
        star_tower = TowerListItem(
            tower_id=3,
            type="image",
            pos=(
                GRID_SIZE * 3.5,
                GRID_SIZE * 3.5,
            ),
            image=StarTower.star_tower_image,
            zoom=zoom,
        )
        pentagon_tower = TowerListItem(
            tower_id=4,
            type="image",
            pos=(
                GRID_SIZE * 5.5,
                GRID_SIZE * 1.5,
            ),
            image=PentagonTower.pentagon_tower_image,
            zoom=zoom,
        )
        rectangle_tower = TowerListItem(
            tower_id=5,
            type="image",
            pos=(
                GRID_SIZE * 5.5,
                GRID_SIZE * 3.5,
            ),
            image=RatctangleTower.ractangle_tower_image,
            zoom=zoom,
        )
        self.tower_items = [
            circle_tower,
            triangle_tower,
            square_tower,
            star_tower,
            pentagon_tower,
            rectangle_tower,
        ]
        all_item_size = sum(item.size[0] for item in self.tower_items) + self.gap * (
            len(self.tower_items) - 1
        )
        self.padding = (self.size[0] - all_item_size) / 2
        item_size = 0
        for i, item in enumerate(self.tower_items):
            item.pos = (
                self.pos[0]
                + item_size
                + self.gap * i
                + self.padding
                + item.size[0] / 2,
                self.pos[1] + self.size[1] / 2,
            )
            item_size += item.size[0]
        self.ok_button.pos = (
            self.size[0] - self.ok_button.size[0] + self.pos[0],
            self.size[1] - self.ok_button.size[1] + self.pos[1],
        )

    def update(self, dt):
        if self.ok_button.hover:
            GameState.is_on_ok_button = True
        else:
            GameState.is_on_ok_button = False

        if GameState.selected_tile:
            self.can_draw = True
            if GameState.selected_tile and self.rect.collidepoint(
                GameState.mouse_pos[0], GameState.mouse_pos[1]
            ):
                GameState.is_on_tower_list = True
            else:
                GameState.is_on_tower_list = False
        else:
            GameState.is_on_ok_button = False
            GameState.is_on_tower_list = False
            self.can_draw = False
        for item in self.tower_items:
            item.update(dt)

    def draw(self, surface):
        if not self.can_draw:
            return
        pygame.draw.rect(
            surface,
            pygame.Color("#ffffff"),
            (self.pos[0], self.pos[1], self.size[0], self.size[1]),
        )
        for item in self.tower_items:
            item.draw(surface)

        if any(item.is_selected for item in self.tower_items):
            self.ok_button.can_draw = True
            self.ok_button.draw(surface)
        else:
            self.ok_button.can_draw = False
