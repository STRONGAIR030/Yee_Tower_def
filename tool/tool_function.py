import math
import pygame
import os
from typing import Dict, TYPE_CHECKING
from constants import GRID_GAP, GRID_SIZE, IMAGE_PATH
from game_stat import GameState
from tool.hitbox_tool import (
    circle_vs_circle,
    polygon_vs_circle,
    polygon_vs_polygon,
    polygon_vs_rect,
    rect_vs_circle,
    rect_vs_rect,
)

if TYPE_CHECKING:
    from components.Item_group import Item, ItemGroup

# 工具函式


# 將世界座標轉換為螢幕座標
def transform_coordinates(x, y):
    screen_x = int(x * GameState.zoom - GameState.camera_offset[0])
    screen_y = int(y * GameState.zoom - GameState.camera_offset[1])
    return [screen_x, screen_y]


# 將螢幕座標轉換為世界座標
def screen_to_world_coordinates(x, y):
    world_x = (x + GameState.camera_offset[0]) / GameState.zoom
    world_y = (y + GameState.camera_offset[1]) / GameState.zoom
    return [world_x, world_y]


# 將座標縮放到遊戲狀態的縮放比例
def zoom_coordinates(value):
    return int(value * GameState.zoom)


# 將格子座標轉換為格子中心點座標
def tile_center(x, y):
    grid_x = int(x * (GRID_SIZE + GRID_GAP) + GRID_SIZE / 2)
    grid_y = int(y * (GRID_SIZE + GRID_GAP) + GRID_SIZE / 2)
    return [grid_x, grid_y]


# 檢查是否與其他物件碰撞
def check_hit(item: "Item", group: "ItemGroup") -> "Item | None":
    for other in group:
        if other is item:
            continue
        if item.hit_box == "circle" and other.hit_box == "circle":
            hit = circle_vs_circle(item.pos, item.radius, other.pos, other.radius)
        elif item.hit_box == "rect" and other.hit_box == "rect":
            hit = rect_vs_rect(item.rect, other.rect)
        elif item.hit_box == "circle" and other.hit_box == "rect":
            hit = rect_vs_circle(other.rect, item.pos, item.radius)
        elif item.hit_box == "rect" and other.hit_box == "circle":
            hit = rect_vs_circle(item.rect, other.pos, other.radius)
        elif item.hit_box == "polygon" and other.hit_box == "polygon":
            hit = polygon_vs_polygon(item.polygon, other.polygon)
        elif item.hit_box == "circle" and other.hit_box == "polygon":
            hit = polygon_vs_circle(other.polygon, item.pos, item.radius)
        elif item.hit_box == "polygon" and other.hit_box == "circle":
            hit = polygon_vs_circle(item.polygon, other.pos, other.radius)
        elif item.hit_box == "rect" and other.hit_box == "polygon":
            hit = polygon_vs_rect(other.polygon, item.rect)
        elif item.hit_box == "polygon" and other.hit_box == "rect":
            hit = polygon_vs_rect(item.polygon, other.rect)
        else:
            raise ValueError(f"Unknown hit box type: {item.hit_box} or {other.hit_box}")

        if hit:
            return other


# 檢查兩個物件組之間的碰撞
def check_hit_group(group1: "ItemGroup", group2: "ItemGroup") -> Dict:
    collisions = {}
    for item1 in group1:
        for item2 in group2:
            if item1 is item2:
                continue  # 跳過自己
            hit = check_hit(item1, group2)
            if hit:
                collisions[item1] = hit
    return collisions


# 尋找生命值最高的敵人
def find_max_health_enemy(enemies) -> "Item | None":
    max_health = -1
    target_enemy = None
    for enemy in enemies:
        if enemy.health > max_health:
            max_health = enemy.health
            target_enemy = enemy
    return target_enemy if target_enemy else None


# 載入圖片
def load_image(name: str):
    image = pygame.image.load(os.path.join(IMAGE_PATH, name)).convert_alpha()
    return image


def rotate_point(cx, cy, x, y, angle_deg):
    angle_rad = math.radians(-angle_deg)
    dx = x - cx
    dy = y - cy
    rx = cx + dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
    ry = cy + dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
    return rx, ry


def get_price(level, base=100, late_rate=1.5, switch_level=8, power=1.1):
    if level <= switch_level:
        return int(base + 10 * (level - 1) * base * 0.2 + (1 * (1.5**level) - 1))
    else:
        early = int(
            base + 10 * (switch_level - 1) * base * 0.2 + (1 * (1.5**switch_level) - 1)
        )
        growth = late_rate ** ((level - switch_level) ** power)
        return int(base * early * growth)
