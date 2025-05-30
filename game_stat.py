import select


class GameState:
    zoom = 1.0
    camera_offset = [0, 0]
    dragging = False
    running = True
    last_mouse_pos = (0, 0)
    enemy_summon_cooldown = 0
    tower_upgrade_cooldown = 0
    right_click = False
    left_click = False
    mouse_pos = (0, 0)
    money = 1000
    selected_tile = None
    selected_tower = None
