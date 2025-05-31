class GameState:
    zoom = 1.0
    camera_offset = [0, 0]
    dragging = False
    running = True
    last_mouse_pos = (0, 0)
    enemy_summon_cooldown = 0
    total_enemy_count = 0
    tower_upgrade_cooldown = 0
    right_click = False
    left_click = False
    mouse_pos = (0, 0)
    money = 20
    home_health = 50
    selected_tile = None
    selected_tower = None
    is_on_tower_list = False
    is_on_ok_button = False
