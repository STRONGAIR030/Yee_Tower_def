from calendar import c
import re
from tokenize import group
from typing import List
import pygame
import math
import random

from tool_function import rotate_point

# 初始化
pygame.init()
screen = pygame.display.set_mode((1200, 1200))
pygame.display.set_caption("Tower Defense - Enemies on Grid Path")
clock = pygame.time.Clock()

GRID_SIZE = 64
ZOOM = 1.0
camera_offset = [0, 0]
dragging = False
last_mouse_pos = (0, 0)

# 路徑節點（格子座標）


# 建立多個敵人


def transform_coordinates(x, y):
    screen_x = int(x * ZOOM - camera_offset[0])
    screen_y = int(y * ZOOM - camera_offset[1])
    return [screen_x, screen_y]


running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            dragging = True
            last_mouse_pos = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            dragging = False
        elif event.type == pygame.MOUSEMOTION and dragging:
            current_mouse_pos = pygame.mouse.get_pos()
            dx = last_mouse_pos[0] - current_mouse_pos[0]
            dy = last_mouse_pos[1] - current_mouse_pos[1]
            camera_offset[0] += dx
            camera_offset[1] += dy
            last_mouse_pos = current_mouse_pos
        elif event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            wordx = (mx + camera_offset[0]) / ZOOM
            wordy = (my + camera_offset[1]) / ZOOM
            ZOOM += event.y * 0.1
            ZOOM = max(0.5, min(5.0, ZOOM))
            camera_offset[0] = wordx * ZOOM - mx
            camera_offset[1] = wordy * ZOOM - my
    screen.fill((200, 200, 200))

    rect_point = ((0, -0.5), (3, -0.5), (3, 0.5), (0, 0.5))
    pos = (0, 0)
    scale_point = []
    for point in rect_point:
        x, y = transform_coordinates(
            point[0] * GRID_SIZE + pos[0], point[1] * GRID_SIZE + pos[1]
        )
        print(point, x, y)
        x, y = rotate_point(pos[0], pos[1], x, y, 90)  # 假設沒有旋轉
        scale_point.append((x, y))

    pygame.draw.polygon(
        screen,
        (255, 0, 0),
        scale_point,
    )
    pygame.draw.circle(
        screen,
        (0, 255, 0),
        transform_coordinates(pos[0], pos[1]),
        int(GRID_SIZE * ZOOM / 2),
    )

    pygame.display.flip()

pygame.quit()
