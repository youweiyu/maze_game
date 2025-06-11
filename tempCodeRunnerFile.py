    icon_y = 25
    icon_size = 60
    gap = 30
    total_width = 6 * icon_size + 5 * gap
    start_x = WIDTH // 2 - total_width // 2 + icon_size // 2
    for i in range(6):
        icon_x = start_x + i * (icon_size + gap)
        # 以图标中心为圆心，半径30像素为点击区域
        if (pos[0] - icon_x) ** 2 + (pos[1] - icon_y) ** 2 < 30 ** 2:
            play_sound("click")
            current_level = i
            load_level(current_level)
            game_state = GameState.PLAYING
            return