from calendar import c
import re
from tokenize import group
from typing import List
import pygame
import math
import random

from tool.tool_function import rotate_point

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

running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                dragging = True
                last_mouse_pos = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False
        elif event.type == pygame.MOUSEMOTION and dragging:
            current = pygame.mouse.get_pos()
            # 滑鼠移動的距離 = 相機偏移量
            dx = last_mouse_pos[0] - current[0]
            dy = last_mouse_pos[1] - current[1]
            camera_offset[0] -= dx
            camera_offset[1] -= dy
            last_mouse_pos = current
        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_x = (mouse_x - camera_offset[0]) / ZOOM
            world_y = (mouse_y - camera_offset[1]) / ZOOM
            ZOOM += event.y * 0.1
            ZOOM = max(0.1, min(10, ZOOM))
            camera_offset[0] = -(world_x * ZOOM - mouse_x)
            camera_offset[1] = -(world_y * ZOOM - mouse_y)
    screen.fill((200, 200, 200))

    rect_point = ((0.5, 0), (0.5, 3), (-0.5, 3), (-0.5, 0))
    pos = (0, 0)
    scale_point = []
    for point in rect_point:
        x, y = point
        x *= GRID_SIZE * ZOOM
        y *= GRID_SIZE * ZOOM
        x += camera_offset[0]
        y += camera_offset[1]
        x, y = rotate_point(pos[0], pos[1], x, y, 0)  # 假設沒有旋轉
        scale_point.append((x, y))

    pygame.draw.polygon(
        screen,
        (255, 0, 0),
        scale_point,
    )

    pygame.display.flip()

pygame.quit()
