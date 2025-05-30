import pygame

from components.tower import PentagonTower, RatctangleTower, StarTower, TriangleTower
from test import GRID_SIZE


class TowerListItem:
    def __init__(self, pos, type, color=None, image=None, zoom=1):
        self.type = type
        self.color = color
        self.image = image
        self.radius = GRID_SIZE / 2 * zoom
        self.size = (GRID_SIZE * zoom, GRID_SIZE * zoom)
        if self.image:
            self.image = pygame.transform.scale(self.image, self.size)

    def draw(self, surface, zoom):
        if self.type == "circle":
            pygame.draw.circle(
                surface,
                self.color,
                (self.pos[0], self.pos[1]),
                int(GRID_SIZE / 2 * zoom),
            )
        elif self.type == "rect":
            pygame.draw.rect(
                surface,
                self.color,
                (
                    self.pos[0] - GRID_SIZE / 2 * zoom,
                    self.pos[1] - GRID_SIZE / 2 * zoom,
                    GRID_SIZE * zoom,
                    GRID_SIZE * zoom,
                ),
            )
        elif self.type == "image" and self.image:
            scale_image = pygame.transform.scale(self.image, self.size)
            image_rect = scale_image.get_rect(center=(self.pos[0], self.pos[1]))
            surface.blit(scale_image, image_rect)


class TowerList:
    def __init__(self):
        circle_tower = TowerListItem(
            type="circle",
            pos=(
                GRID_SIZE * 1.5,
                GRID_SIZE * 1.5,
            ),
            color=pygame.Color("#4aca8b"),
        )
        triangle_tower = TowerListItem(
            type="image",
            pos=(
                GRID_SIZE * 1.5,
                GRID_SIZE * 3.5,
            ),
            image=TriangleTower.triangle_tower_image,
            zoom=1,
        )
        square_tower = TowerListItem(
            type="rect",
            pos=(
                GRID_SIZE * 3.5,
                GRID_SIZE * 1.5,
            ),
            color=pygame.Color("#ff0000"),
        )
        star_tower = TowerListItem(
            type="image",
            pos=(
                GRID_SIZE * 3.5,
                GRID_SIZE * 3.5,
            ),
            image=StarTower.star_tower_image,
            zoom=1,
        )
        pentagon_tower = TowerListItem(
            type="image",
            pos=(
                GRID_SIZE * 5.5,
                GRID_SIZE * 1.5,
            ),
            image=PentagonTower.pentagon_tower_image,
            zoom=1,
        )
        rectangle_tower = TowerListItem(
            type="image",
            pos=(
                GRID_SIZE * 5.5,
                GRID_SIZE * 3.5,
            ),
            image=RatctangleTower.ractangle_tower_image,
            zoo=1,
        )
        self.tower_items = [
            circle_tower,
            triangle_tower,
            square_tower,
            star_tower,
            pentagon_tower,
            rectangle_tower,
        ]

    def draw(self, surface, zoom):
        for item in self.tower_items:
            item.draw(surface, zoom)
