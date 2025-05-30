import pygame

from components.tower import PentagonTower, RatctangleTower, StarTower, TriangleTower
from constants import GRID_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH
from game_stat import GameState


class TowerListItem:
    def __init__(self, pos, type, color=None, image=None, zoom=1):
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
        if GameState.selected_tile and self.boerder_rect.collidepoint(
            GameState.mouse_pos
        ):
            self.is_selected = True
        else:
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

        border_rect = pygame.Rect(
            self.pos[0] - GRID_SIZE / 2,
            self.pos[1] - GRID_SIZE / 2,
            self.size[0],
            self.size[1],
        )
        border_rect.center = (self.pos[0], self.pos[1])

        pygame.draw.rect(
            surface,
            pygame.Color("#000000"),
            border_rect,
            width=2,
        )


class TowerList:
    def __init__(self):
        zoom = 1
        self.can_draw = False
        self.pos = (0, SCREEN_HEIGHT * 0.8)
        self.size = (SCREEN_WIDTH, SCREEN_HEIGHT * 0.2)
        self.gap = 40
        circle_tower = TowerListItem(
            type="circle",
            pos=(
                GRID_SIZE * 1.5,
                GRID_SIZE * 1.5,
            ),
            color=(0, 255, 0),
            zoom=zoom,
        )
        triangle_tower = TowerListItem(
            type="image",
            pos=(
                GRID_SIZE * 1.5,
                GRID_SIZE * 3.5,
            ),
            image=TriangleTower.triangle_tower_image,
            zoom=zoom,
        )
        square_tower = TowerListItem(
            type="rect",
            pos=(
                GRID_SIZE * 3.5,
                GRID_SIZE * 1.5,
            ),
            color=pygame.Color("#ff0000"),
            zoom=zoom,
        )
        star_tower = TowerListItem(
            type="image",
            pos=(
                GRID_SIZE * 3.5,
                GRID_SIZE * 3.5,
            ),
            image=StarTower.star_tower_image,
            zoom=zoom,
        )
        pentagon_tower = TowerListItem(
            type="image",
            pos=(
                GRID_SIZE * 5.5,
                GRID_SIZE * 1.5,
            ),
            image=PentagonTower.pentagon_tower_image,
            zoom=zoom,
        )
        rectangle_tower = TowerListItem(
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

    def update(self, dt):
        if GameState.selected_tile:
            self.can_draw = True
        else:
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
