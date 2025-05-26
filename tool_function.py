import math
import pygame
import os
from typing import Dict, TYPE_CHECKING
from constants import GRID_GAP, GRID_SIZE, IMAGE_PATH
from game_stat import GameState

if TYPE_CHECKING:
    from components.Item_group import Item


def transform_coordinates(x, y):
    screen_x = int(x * GameState.zoom - GameState.camera_offset[0])
    screen_y = int(y * GameState.zoom - GameState.camera_offset[1])
    return [screen_x, screen_y]


def zoom_coordinates(value):
    return int(value * GameState.zoom)


def tile_center(x, y):
    grid_x = int(x * (GRID_SIZE + GRID_GAP) + GRID_SIZE / 2)
    grid_y = int(y * (GRID_SIZE + GRID_GAP) + GRID_SIZE / 2)
    return [grid_x, grid_y]


def check_hit_radius(item, group) -> "Item | None":
    for other in group:
        if other is item:
            continue  # 跳過自己
        dx = other.pos[0] - item.pos[0]
        dy = other.pos[1] - item.pos[1]
        dist = math.hypot(dx, dy)
        if dist <= item.radius + other.radius:
            return other
    return None


def check_hit_rect(item, group) -> "Item | None":
    for other in group:
        if other is item:
            continue
        if other.rect.colliderect(item.rect):
            return other

    return None


def check_hit_radius_group(group1, group2) -> Dict:
    collisions = {}
    for item1 in group1:
        for item2 in group2:
            if item1 is item2:
                continue  # 跳過自己
            hit = check_hit_radius(item1, group2)
            if hit:
                collisions[item1] = hit
    return collisions


def check_hit_rect_group(group1, group2) -> Dict:
    collisions = {}
    for item1 in group1:
        for item2 in group2:
            if item1 is item2:
                continue  # 跳過自己
            hit = check_hit_rect(item1, group2)
            if hit:
                collisions[item1] = hit
    return collisions


def find_max_health_enemy(enemies) -> "Item | None":
    max_health = -1
    target_enemy = None
    for enemy in enemies:
        if enemy.health > max_health:
            max_health = enemy.health
            target_enemy = enemy
    return target_enemy if target_enemy else None


def load_image(name: str):
    image = pygame.image.load(os.path.join(IMAGE_PATH, name)).convert_alpha()
    return image
