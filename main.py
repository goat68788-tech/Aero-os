import pygame
import sys
import os
import random
import math

pygame.init()

# ============================================================
# ეკრანის ინიციალიზაცია
# ============================================================
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Aero OS Prototype")
clock = pygame.time.Clock()

# ============================================================
# AERO OS ფერები
# ============================================================
BACKGROUND_COLOR = (20, 24, 35)
CARD_COLOR = (40, 45, 60)
ACTIVE_COLOR = (0, 120, 255)
TEXT_COLOR = (255, 255, 255)

font = pygame.font.SysFont("sans-serif", 40)
title_font = pygame.font.SysFont("sans-serif", 60)
small_font = pygame.font.SysFont("sans-serif", 22)
tiny_font = pygame.font.SysFont("sans-serif", 18)

# ============================================================
# თამაშების სია
# ============================================================
games = [
    {"title": "Piglet Escape", "package": "piglet_escape"},
    {"title": "Space Shooter", "package": ""},
    {"title": "Aero Racing", "package": ""}
]
selected_index = 0

# ============================================================
# PIGLET ESCAPE — თამაშის ფუნქცია
# ============================================================
def run_piglet_escape():
    """Piglet Escape თამაშის მთავარი ფუნქცია.
    უბრუნებს None-ს, როცა მოთამაშე გამოდის (ESC)."""

    # თამაშის შიდა ზომები (ინახავს ორიგინალ ლოგიკას)
    GW, GH = 640, 480
    game_surf = pygame.Surface((GW, GH))

    # ლოკალური ფონტები
    g_font = pygame.font.SysFont('sans-serif', 32)
    g_small = pygame.font.SysFont('sans-serif', 22)
    g_tiny = pygame.font.SysFont('sans-serif', 18)
    button_rect = pygame.Rect(GW // 2 - 80, GH // 2 + 40, 160, 50)

    # ---- თამაშის ცვლადები ----
    current_level = 1
    pig_x, pig_y = 320, 240
    pig_radius = 50
    carrots_eaten = 0
    energy = 100.0
    time_left = 30.0
    game_over = False
    win = False
    loss_reason = ""

    carrot_x = random.randint(50, GW - 50)
    carrot_y = random.randint(50, GH - 50)
    human_x = 50
    human_y = 400
    human_speed = 5

    wolf_x, wolf_y = 50, 50
    wolf_speed = 5
    wolf_alive = True
    wolf_hp = 100

    hunter_x, hunter_y = GW - 80, GH - 80
    hunter_speed = 8
    hunter_ammo = 5
    bullets = []
    shoot_cooldown = 0

    enemy_pigs = []
    bite_count = 0
    bite_target = 10
    bite_cooldown = 0
    bite_effect_timer = 0
    bite_effect_pos = (0, 0)

    ENEMY_COLORS = [
        (100, 100, 220), (220, 180, 50),
        (150, 220, 100), (220, 100, 200),
    ]

    mud_x = random.randint(150, GW - 150)
    mud_y = random.randint(150, GH - 150)

    HUMAN_COLOR = (245, 222, 179)
    MUD_COLOR = (139, 69, 19)
    WOLF_COLOR = (105, 105, 105)
    WOLF_DARK = (60, 60, 60)
    HUNTER_COLOR = (200, 160, 100)
    HUNTER_HAT = (60, 40, 20)
    ROPE_COLOR = (180, 140, 80)

    trees = []
    TREE_TRUNK_COLOR = (101, 67, 33)
    TREE_TRUNK_DARK = (70, 45, 20)
    TREE_LEAF_COLORS = [
        (34, 120, 40), (45, 140, 50),
        (60, 160, 60), (25, 100, 30),
    ]

    rope_hp = 100.0
    rope_max_hp = 100.0
    click_damage = 8.0
    click_cooldown = 0.0
    hanging_swing = 0.0
    cut_particles = []

    butcher_x, butcher_y = 80.0, 380.0
    butcher_speed = 1.1
    butcher_alive = True

    pig_state = "hanging"
    fall_vy = 0.0
    ground_y = GH - 90

    exit_rect = pygame.Rect(GW - 60, GH // 2 - 80, 60, 160)

    blood = 100.0
    blood_max = 100.0
    blood_loss_rate = 3.5
    blood_particles = []
    blood_trails = []
    knife_stuck = True
    vet_x, vet_y = GW - 90, 90
    vet_radius = 55
    vignette_alpha = 0

    # ---- დამხმარე ფუნქციები ----
    def spawn_trees(count=10):
        nonlocal trees
        trees = []
        for _ in range(count):
            attempts = 0
            while attempts < 50:
                tx = random.randint(40, GW - 40)
                ty = random.randint(40, GH - 40)
                r = random.randint(28, 45)
                if tx > GW - 140 and ty < 140:
                    attempts += 1; continue
                if math.hypot(tx - mud_x, ty - mud_y) < 90:
                    attempts += 1; continue
                if math.hypot(tx - 320, ty - 240) < 120:
                    attempts += 1; continue
                too_close = False
                for t in trees:
                    if math.hypot(tx - t['x'], ty - t['y']) < (r + t['r'] + 20):
                        too_close = True; break
                if too_close:
                    attempts += 1; continue
                trees.append({
                    'x': tx, 'y': ty, 'r': r,
                    'leaf_color': random.choice(TREE_LEAF_COLORS),
                    'trunk_h': r + random.randint(5, 15),
                })
                break

    def spawn_enemy_pigs(count=4):
        nonlocal enemy_pigs
        enemy_pigs = []
        for i in range(count):
            while True:
                ex = random.randint(80, GW - 80)
                ey = random.randint(80, GH - 80)
                if math.hypot(ex - 320, ey - 240) > 150:
                    break
            enemy_pigs.append({
                'x': ex, 'y': ey, 'r': 30,
                'color': ENEMY_COLORS[i % len(ENEMY_COLORS)],
                'hp': 3,
                'speed': random.uniform(2.0, 3.0),
                'wander_x': random.uniform(-1, 1),
                'wander_y': random.uniform(-1, 1),
                'wander_timer': random.uniform(0.5, 1.5),
                'hit_flash': 0,
            })

    def start_level(level_num):
        nonlocal pig_x, pig_y, pig_radius, carrots_eaten, energy, time_left
        nonlocal game_over, win, loss_reason, carrot_x, carrot_y
        nonlocal human_x, human_y, mud_x, mud_y, current_level
        nonlocal wolf_x, wolf_y, wolf_alive, wolf_hp
        nonlocal hunter_x, hunter_y, hunter_ammo, bullets, shoot_cooldown
        nonlocal bite_count, bite_cooldown, bite_effect_timer
        nonlocal rope_hp, rope_max_hp, click_damage, click_cooldown
        nonlocal hanging_swing, cut_particles
        nonlocal butcher_x, butcher_y, butcher_speed, butcher_alive
        nonlocal pig_state, fall_vy, ground_y
        nonlocal blood, blood_max, blood_loss_rate, blood_particles, blood_trails
        nonlocal knife_stuck, vet_x, vet_y, vet_radius, vignette_alpha

        current_level = level_num
        pig_x, pig_y = 320, 240
        pig_radius = 50
        carrots_eaten = 0
        energy = 100.0
        time_left = 30.0 if level_num != 4 else 40.0
        game_over = False
        win = False
        loss_reason = ""

        carrot_x = random.randint(50, GW - 50)
        carrot_y = random.randint(50, GH - 50)
        human_x, human_y = 50, 400

        wolf_x, wolf_y = 50, 50
        wolf_alive = True
        wolf_hp = 100

        hunter_x, hunter_y = GW - 80, GH - 80
        hunter_ammo = 5
        bullets = []
        shoot_cooldown = 0

        bite_count = 0
        bite_cooldown = 0
        bite_effect_timer = 0

        mud_x = random.randint(150, GW - 150)
        mud_y = random.randint(150, GH - 150)

        rope_hp = 100.0
        rope_max_hp = 100.0
        click_damage = 8.0
        click_cooldown = 0.0
        hanging_swing = 0.0
        cut_particles = []

        butcher_x, butcher_y = 80.0, 380.0
        butcher_speed = 1.1
        butcher_alive = True

        pig_state = "hanging"
        fall_vy = 0.0
        ground_y = GH - 90

        blood = 100.0
        blood_max = 100.0
        blood_loss_rate = 99
        blood_particles = []
        blood_trails = []
        knife_stuck = True
        vet_x, vet_y = GW - 90, 90
        vet_radius = 55
        vignette_alpha = 0

        if level_num in (1, 2):
            spawn_trees(10)
        else:
            trees.clear()

        if level_num == 4:
            spawn_enemy_pigs(4)
        elif level_num == 5:
            pig_x = GW // 2
            pig_y = GH // 2 - 100
            time_left = 0
        elif level_num == 6:
            pig_x = 80
            pig_y = GH - 80
            time_left = 0

    start_level(1)

    # ---- მთავარი თამაშის ციკლი ----
    playing = True
    while playing:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return  # სრული გასვლა

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                playing = False
                break

            # მოვლენები უნდა იყოს დამუშავებული იმავე შიდა კოორდინატებში
            # ამიტომ ვაწარმოებთ ორიგინალ ლოგიკას (მაუსის პოზიცია კორექტირებულია ქვემოთ)

            if current_level == 4 and not game_over and event.type == pygame.MOUSEBUTTONDOWN:
                if bite_cooldown <= 0:
                    bite_range = pig_radius + 45
                    closest = None
                    closest_dist = bite_range
                    for ep in enemy_pigs:
                        d = math.hypot(pig_x - ep['x'], pig_y - ep['y'])
                        if d < closest_dist:
                            closest_dist = d
                            closest = ep
                    if closest:
                        closest['hp'] -= 1
                        closest['hit_flash'] = 0.2
                        bite_count += 1
                        bite_cooldown = 0.35
                        bite_effect_timer = 0.3
                        bite_effect_pos = (closest['x'], closest['y'])
                        if closest['hp'] <= 0:
                            enemy_pigs.remove(closest)
                        if bite_count >= bite_target:
                            game_over = True
                            win = True

            if current_level == 5 and not game_over and pig_state == "hanging":
                if event.type == pygame.MOUSEBUTTONDOWN or \
                   (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                    if click_cooldown <= 0:
                        rope_hp -= click_damage
                        click_cooldown = 0.1
                        for _ in range(6):
                            cut_particles.append({
                                'x': pig_x + random.uniform(-8, 8),
                                'y': pig_y - pig_radius + random.uniform(-5, 5),
                                'vx': random.uniform(-3, 3),
                                'vy': random.uniform(-1, 3),
                                'life': 0.7,
                                'color': ROPE_COLOR,
                            })
                        if rope_hp <= 0:
                            rope_hp = 0
                            pig_state = "falling"
                            fall_vy = 0.0

            if game_over and event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # გადაითვალეთ შიდა კოორდინატებში
                scale_x = GW / WIDTH
                scale_y = GH / HEIGHT
                # fullscreen scaling
                inner_mx = mx * scale_x
                inner_my = my * scale_y
                if button_rect.collidepoint(inner_mx, inner_my):
                    if win:
                        if current_level == 1:
                            start_level(2)
                        elif current_level == 2:
                            start_level(3)
                        elif current_level == 3:
                            start_level(4)
                        elif current_level == 4:
                            start_level(5)
                        elif current_level == 5:
                            start_level(6)
                        else:
                            start_level(1)
                    else:
                        start_level(current_level)

        if not playing:
            break

        # მაუსის პოზიცია შიდა კოორდინატებში
        real_mx, real_my = pygame.mouse.get_pos()
        mouse_x = real_mx * (GW / WIDTH)
        mouse_y = real_my * (GH / HEIGHT)

        if not game_over:
            if current_level != 5:
                pig_x, pig_y = mouse_x, mouse_y

            if bite_cooldown > 0:
                bite_cooldown -= dt
            if bite_effect_timer > 0:
                bite_effect_timer -= dt

            if current_level == 2:
                energy -= 0.25
                if energy <= 0:
                    energy = 0
                    game_over = True
                    win = False
                    loss_reason = "GAME OVER: OUT OF ENERGY!"

            if current_level in (3, 4):
                time_left -= dt
                if time_left <= 0:
                    time_left = 0
                    game_over = True
                    win = False
                    loss_reason = "GAME OVER: TIME'S UP!"

            is_in_mud = False
            mud_visible = (current_level == 2 and carrots_eaten >= 5)
            if mud_visible:
                dist_to_mud = math.hypot(pig_x - mud_x, pig_y - mud_y)
                is_in_mud = dist_to_mud < (pig_radius + 40)
                if is_in_mud:
                    game_over = True
                    win = True

            if current_level in (1, 2):
                if not is_in_mud:
                    if human_x < pig_x: human_x += human_speed
                    elif human_x > pig_x: human_x -= human_speed
                    if human_y < pig_y: human_y += human_speed
                    elif human_y > pig_y: human_y -= human_speed
                    dist_to_human = math.hypot(pig_x - human_x, pig_y - human_y)
                    if dist_to_human < (pig_radius + 3):
                        game_over = True
                        win = False
                        loss_reason = "GAME OVER: HUMAN CAUGHT YOU!"
                else:
                    human_x += random.randint(-1, 1)
                    human_y += random.randint(-1, 1)

            if current_level == 3 and wolf_alive:
                if wolf_x < pig_x: wolf_x += wolf_speed
                elif wolf_x > pig_x: wolf_x -= wolf_speed
                if wolf_y < pig_y: wolf_y += wolf_speed
                elif wolf_y > pig_y: wolf_y -= wolf_speed

                dist_to_wolf = math.hypot(pig_x - wolf_x, pig_y - wolf_y)
                if dist_to_wolf < (pig_radius + 5):
                    game_over = True
                    win = False
                    loss_reason = "GAME OVER: WOLF CAUGHT YOU!"

                dist_hunter_wolf = math.hypot(hunter_x - wolf_x, hunter_y - wolf_y)
                if dist_hunter_wolf > 180:
                    if hunter_x < wolf_x: hunter_x += hunter_speed
                    elif hunter_x > wolf_x: hunter_x -= hunter_speed
                    if hunter_y < wolf_y: hunter_y += hunter_speed
                    elif hunter_y > wolf_y: hunter_y -= hunter_speed

                shoot_cooldown -= dt
                if dist_hunter_wolf < 250 and hunter_ammo > 0 and shoot_cooldown <= 0:
                    dx = wolf_x - hunter_x
                    dy = wolf_y - hunter_y
                    dist = math.hypot(dx, dy)
                    if dist > 0:
                        dx /= dist; dy /= dist
                        bullets.append([hunter_x, hunter_y, dx * 8, dy * 8])
                        hunter_ammo -= 1
                        shoot_cooldown = 0.8

                for bullet in bullets[:]:
                    bullet[0] += bullet[2]
                    bullet[1] += bullet[3]
                    if math.hypot(bullet[0] - wolf_x, bullet[1] - wolf_y) < 25:
                        wolf_hp -= 34
                        bullets.remove(bullet)
                        if wolf_hp <= 0:
                            wolf_alive = False
                        continue
                    if not (0 <= bullet[0] <= GW and 0 <= bullet[1] <= GH):
                        bullets.remove(bullet)

            if current_level == 4:
                for ep in enemy_pigs[:]:
                    dx = ep['x'] - pig_x
                    dy = ep['y'] - pig_y
                    dist = math.hypot(dx, dy)
                    if dist < 160 and dist > 0:
                        flee_x = dx / dist
                        flee_y = dy / dist
                        ep['x'] += flee_x * ep['speed']
                        ep['y'] += flee_y * ep['speed']
                    else:
                        ep['wander_timer'] -= dt
                        if ep['wander_timer'] <= 0:
                            ep['wander_x'] = random.uniform(-1, 1)
                            ep['wander_y'] = random.uniform(-1, 1)
                            ep['wander_timer'] = random.uniform(0.5, 1.5)
                        ep['x'] += ep['wander_x'] * ep['speed'] * 0.7
                        ep['y'] += ep['wander_y'] * ep['speed'] * 0.7

                    if ep['x'] < ep['r']:
                        ep['x'] = ep['r']; ep['wander_x'] = abs(ep['wander_x'])
                    if ep['x'] > GW - ep['r']:
                        ep['x'] = GW - ep['r']; ep['wander_x'] = -abs(ep['wander_x'])
                    if ep['y'] < ep['r']:
                        ep['y'] = ep['r']; ep['wander_y'] = abs(ep['wander_y'])
                    if ep['y'] > GH - ep['r']:
                        ep['y'] = GH - ep['r']; ep['wander_y'] = -abs(ep['wander_y'])

                    if ep['hit_flash'] > 0:
                        ep['hit_flash'] -= dt

                    if dist < (pig_radius + ep['r']) and bite_cooldown <= 0:
                        ep['hp'] -= 1
                        ep['hit_flash'] = 0.2
                        bite_count += 1
                        bite_cooldown = 0.4
                        bite_effect_timer = 0.3
                        bite_effect_pos = (ep['x'], ep['y'])
                        if ep['hp'] <= 0:
                            if ep in enemy_pigs:
                                enemy_pigs.remove(ep)
                        if bite_count >= bite_target:
                            game_over = True
                            win = True

            if current_level == 5:
                if click_cooldown > 0:
                    click_cooldown -= dt
                tension = 1.0 - (rope_hp / rope_max_hp)
                hanging_swing += dt * (2 + tension * 5)
                for p in cut_particles[:]:
                    p['x'] += p['vx']; p['y'] += p['vy']
                    p['vy'] += 0.2; p['life'] -= dt
                    if p['life'] <= 0:
                        cut_particles.remove(p)

                dx = pig_x - butcher_x
                dy = pig_y - butcher_y
                dist_b = math.hypot(dx, dy)
                if dist_b > 0:
                    butcher_x += (dx / dist_b) * butcher_speed
                    butcher_y += (dy / dist_b) * butcher_speed

                if pig_state == "hanging":
                    if dist_b < 55:
                        game_over = True
                        win = False
                        loss_reason = "GAME OVER: BUTCHER GOT YOU!"
                elif pig_state == "falling":
                    fall_vy += 0.8
                    pig_y += fall_vy
                    if pig_y >= ground_y:
                        pig_y = ground_y
                        pig_state = "free"
                elif pig_state == "free":
                    pig_x = mouse_x
                    pig_y = mouse_y
                    dx = pig_x - butcher_x
                    dy = pig_y - butcher_y
                    dist_b = math.hypot(dx, dy)
                    if dist_b > 0:
                        speed = butcher_speed * (1.4 if dist_b > 200 else 1.0)
                        butcher_x += (dx / dist_b) * speed
                        butcher_y += (dy / dist_b) * speed
                    if dist_b < (pig_radius + 20):
                        game_over = True
                        win = False
                        loss_reason = "GAME OVER: BUTCHER CAUGHT YOU!"
                    if exit_rect.collidepoint(pig_x, pig_y):
                        game_over = True
                        win = True

            if current_level == 6:
                blood -= blood_loss_rate * dt
                if blood <= 0:
                    blood = 0
                    game_over = True
                    win = False
                    loss_reason = "GAME OVER: YOU BLED OUT!"

                if blood > 0:
                    if random.random() < 0.3:
                        blood_particles.append({
                            'x': pig_x + random.uniform(-pig_radius * 0.4, pig_radius * 0.4),
                            'y': pig_y + random.uniform(-pig_radius * 0.2, pig_radius * 0.5),
                            'vx': random.uniform(-1, 1),
                            'vy': random.uniform(1, 3),
                            'life': 1.5,
                            'size': random.randint(2, 5),
                        })
                    if random.random() < 0.08:
                        blood_trails.append({
                            'x': pig_x + random.uniform(-10, 10),
                            'y': pig_y + pig_radius - random.uniform(0, 10),
                            'size': random.randint(4, 9),
                            'life': 30.0,
                        })

                for p in blood_particles[:]:
                    p['x'] += p['vx']; p['y'] += p['vy']
                    p['vy'] += 0.15; p['life'] -= dt
                    if p['life'] <= 0:
                        blood_particles.remove(p)
                for t in blood_trails[:]:
                    t['life'] -= dt
                    if t['life'] <= 0:
                        blood_trails.remove(t)

                vignette_alpha = int((1.0 - blood / blood_max) * 180)

                dist_to_vet = math.hypot(pig_x - vet_x, pig_y - vet_y)
                if dist_to_vet < (pig_radius + vet_radius):
                    game_over = True
                    win = True

            if current_level in (1, 2, 3):
                distance = math.hypot(pig_x - carrot_x, pig_y - carrot_y)
                if distance < (pig_radius + 20):
                    carrots_eaten += 1
                    if current_level == 1:
                        pig_radius += 5
                        if carrots_eaten >= 10:
                            game_over = True
                            win = False
                            loss_reason = "GAME OVER: PIG EXPLODED!"
                    elif current_level == 2:
                        energy += 25.0
                        if energy > 100: energy = 100.0
                    else:
                        time_left += 1.5
                        if time_left > 30: time_left = 30.0
                    if not game_over:
                        carrot_x = random.randint(30, GW - 30)
                        carrot_y = random.randint(50, GH - 50)

            if current_level == 1 and 4 <= carrots_eaten <= 8 and pig_x > GW - 100 and pig_y < 100:
                game_over = True
                win = True
            if current_level == 3 and carrots_eaten >= 15 and pig_x > GW - 100 and pig_y < 100:
                game_over = True
                win = True

        # ============================================================
        # ხატვა (inner surface-ზე)
        # ============================================================
        if not game_over:
            if current_level == 3:
                game_surf.fill((20, 20, 60))
            elif current_level == 4:
                game_surf.fill((60, 15, 15))
            elif current_level == 5:
                game_surf.fill((45, 30, 25))
            elif current_level == 6:
                game_surf.fill((30, 60, 30))
            else:
                game_surf.fill((34, 139, 34))

            if current_level in (1, 2):
                for t in trees:
                    tx, ty, tr = int(t['x']), int(t['y']), int(t['r'])
                    pygame.draw.ellipse(game_surf, (25, 90, 25),
                                        (tx - tr, ty + tr - 5, tr * 2, 14))
                    trunk_w = max(8, tr // 3)
                    trunk_h = t['trunk_h']
                    pygame.draw.rect(game_surf, TREE_TRUNK_COLOR,
                                     (tx - trunk_w // 2, ty, trunk_w, trunk_h))
                    pygame.draw.rect(game_surf, TREE_TRUNK_DARK,
                                     (tx - trunk_w // 2, ty, trunk_w // 3, trunk_h))
                    leaf_color = t['leaf_color']
                    leaf_dark = (max(leaf_color[0] - 30, 0),
                                 max(leaf_color[1] - 30, 0),
                                 max(leaf_color[2] - 30, 0))
                    pygame.draw.circle(game_surf, leaf_dark, (tx - tr // 2, ty - tr // 4), tr // 2)
                    pygame.draw.circle(game_surf, leaf_dark, (tx + tr // 2, ty - tr // 4), tr // 2)
                    pygame.draw.circle(game_surf, leaf_color, (tx, ty - tr // 2), int(tr * 0.7))
                    pygame.draw.circle(game_surf, leaf_color, (tx - tr // 2, ty - tr // 4), tr // 2)
                    pygame.draw.circle(game_surf, leaf_color, (tx + tr // 2, ty - tr // 4), tr // 2)
                    lighter = (min(leaf_color[0] + 40, 255),
                               min(leaf_color[1] + 40, 255),
                               min(leaf_color[2] + 40, 255))
                    pygame.draw.circle(game_surf, lighter, (tx - tr // 4, ty - tr // 2), tr // 3)

            if current_level in (1, 3):
                pygame.draw.rect(game_surf, (255, 215, 0), (GW - 100, 0, 100, 100))
                game_surf.blit(g_font.render("HOME", True, (0, 0, 0)), (GW - 85, 35))

            if mud_visible:
                pygame.draw.circle(game_surf, MUD_COLOR, (int(mud_x), int(mud_y)), 70)
                game_surf.blit(g_font.render("MUD", True, (255, 255, 255)),
                               (int(mud_x) - 25, int(mud_y) - 10))

            if current_level == 6:
                for t in blood_trails:
                    alpha = min(1.0, t['life'] / 30.0)
                    col_val = int(120 * alpha)
                    pygame.draw.circle(game_surf, (col_val + 40, 0, 0),
                                       (int(t['x']), int(t['y'])), int(t['size']))

                vx, vy = int(vet_x), int(vet_y)
                pygame.draw.rect(game_surf, (240, 240, 245),
                                 (vx - 60, vy - 55, 120, 110), border_radius=8)
                pygame.draw.rect(game_surf, (200, 200, 210),
                                 (vx - 60, vy - 55, 120, 110), 3, border_radius=8)
                pygame.draw.rect(game_surf, (220, 30, 30), (vx - 22, vy - 20, 44, 14))
                pygame.draw.rect(game_surf, (220, 30, 30), (vx - 7, vy - 35, 14, 44))
                pygame.draw.circle(game_surf, HUMAN_COLOR, (vx, vy + 35), 14)
                pygame.draw.rect(game_surf, (240, 240, 250), (vx - 10, vy + 45, 20, 22))
                pygame.draw.ellipse(game_surf, (255, 255, 255), (vx - 16, vy + 20, 32, 12))
                vet_label = g_small.render("VET", True, (255, 255, 255))
                game_surf.blit(vet_label, (vx - vet_label.get_width() // 2, vy - 80))

            if current_level == 5:
                pygame.draw.rect(game_surf, (70, 45, 30), (0, 0, GW, 40))
                pygame.draw.line(game_surf, (120, 80, 50), (0, 40), (GW, 40), 3)
                pygame.draw.rect(game_surf, (60, 40, 30), (0, GH - 60, GW, 60))

                pygame.draw.rect(game_surf, (60, 180, 60), exit_rect)
                pygame.draw.rect(game_surf, (30, 100, 30), exit_rect, 4)
                pygame.draw.circle(game_surf, (255, 220, 100),
                                   (exit_rect.x + 12, exit_rect.centery), 5)
                exit_text = g_small.render("EXIT", True, (255, 255, 255))
                game_surf.blit(exit_text, (exit_rect.x + 10, exit_rect.y - 25))

                if pig_state in ("hanging", "falling"):
                    tension = 1.0 - (rope_hp / rope_max_hp)
                    swing_offset = math.sin(hanging_swing) * (3 + tension * 10)
                    rope_top = (pig_x, 40)
                    rope_bottom = (pig_x + swing_offset, pig_y - pig_radius)
                    if rope_hp > 0:
                        pygame.draw.line(game_surf, ROPE_COLOR, rope_top, rope_bottom, 5)
                        if tension > 0.3:
                            for i in range(3):
                                off = math.sin(hanging_swing * 3 + i) * 4
                                pygame.draw.line(game_surf, (140, 100, 60),
                                                 (pig_x + off, 40),
                                                 (rope_bottom[0] + off, rope_bottom[1]), 1)
                    else:
                        mid_y = 40 + (pig_y - 40) * 0.3
                        pygame.draw.line(game_surf, ROPE_COLOR, rope_top, (pig_x, mid_y), 5)

                for p in cut_particles:
                    pygame.draw.circle(game_surf, p['color'],
                                       (int(p['x']), int(p['y'])), 3)

                px, py, pr = int(pig_x), int(pig_y), int(pig_radius)
                if pig_state == "free":
                    pygame.draw.ellipse(game_surf, (30, 20, 15),
                                        (px - pr, py + pr - 8, pr * 2, 14))
                pygame.draw.circle(game_surf, (235, 192, 203), (px, py), pr)
                pygame.draw.circle(game_surf, (255, 105, 180),
                                   (px, py + int(pr * 0.2)), int(pr * 0.45))
                pygame.draw.circle(game_surf, (0, 0, 0),
                                   (px - int(pr * 0.13), py + int(pr * 0.2)), int(pr * 0.11))
                pygame.draw.circle(game_surf, (0, 0, 0),
                                   (px + int(pr * 0.13), py + int(pr * 0.2)), int(pr * 0.11))

                eye_r = int(pr * 0.12)
                if pig_state == "hanging":
                    pygame.draw.circle(game_surf, (255, 255, 255),
                                       (px - int(pr * 0.3), py - int(pr * 0.2)), eye_r + 2)
                    pygame.draw.circle(game_surf, (0, 0, 0),
                                       (px - int(pr * 0.3), py - int(pr * 0.2)), eye_r)
                    pygame.draw.circle(game_surf, (255, 255, 255),
                                       (px + int(pr * 0.3), py - int(pr * 0.2)), eye_r + 2)
                    pygame.draw.circle(game_surf, (0, 0, 0),
                                       (px + int(pr * 0.3), py - int(pr * 0.2)), eye_r)
                    pygame.draw.circle(game_surf, (100, 180, 255),
                                       (px + int(pr * 0.5), py - int(pr * 0.4)), 4)
                else:
                    pygame.draw.circle(game_surf, (255, 255, 255),
                                       (px - int(pr * 0.3), py - int(pr * 0.2)), eye_r)
                    pygame.draw.circle(game_surf, (0, 0, 0),
                                       (px - int(pr * 0.3), py - int(pr * 0.2)), int(eye_r * 0.5))
                    pygame.draw.circle(game_surf, (255, 255, 255),
                                       (px + int(pr * 0.3), py - int(pr * 0.2)), eye_r)
                    pygame.draw.circle(game_surf, (0, 0, 0),
                                       (px + int(pr * 0.3), py - int(pr * 0.2)), int(eye_r * 0.5))

                bx, by = int(butcher_x), int(butcher_y)
                pygame.draw.circle(game_surf, (60, 40, 80), (bx, by + 20), 22)
                pygame.draw.circle(game_surf, HUMAN_COLOR, (bx, by - 15), 22)
                pygame.draw.arc(game_surf, (60, 40, 20),
                                (bx - 22, by - 38, 44, 30), 0, math.pi, 5)
                pygame.draw.circle(game_surf, (255, 0, 0), (bx - 7, by - 18), 3)
                pygame.draw.circle(game_surf, (255, 0, 0), (bx + 7, by - 18), 3)
                pygame.draw.arc(game_surf, (0, 0, 0),
                                (bx - 10, by - 10, 20, 12),
                                math.pi, 2 * math.pi, 2)
                pygame.draw.rect(game_surf, (230, 230, 230), (bx - 14, by + 8, 28, 32))
                pygame.draw.circle(game_surf, (180, 0, 0), (bx - 5, by + 18), 3)
                pygame.draw.circle(game_surf, (180, 0, 0), (bx + 6, by + 24), 4)

                knife_angle = math.atan2(pig_y - by, pig_x - bx)
                hx1 = bx + math.cos(knife_angle) * 15
                hy1 = by + math.sin(knife_angle) * 15
                hx2 = bx + math.cos(knife_angle) * 35
                hy2 = by + math.sin(knife_angle) * 35
                pygame.draw.line(game_surf, (60, 30, 10), (hx1, hy1), (hx2, hy2), 7)
                bx1 = hx2 + math.cos(knife_angle - 0.25) * 8
                by1 = hy2 + math.sin(knife_angle - 0.25) * 8
                bx2 = hx2 + math.cos(knife_angle + 0.25) * 8
                by2 = hy2 + math.sin(knife_angle + 0.25) * 8
                tip_x = hx2 + math.cos(knife_angle) * 45
                tip_y = hy2 + math.sin(knife_angle) * 45
                pygame.draw.polygon(game_surf, (210, 210, 225),
                                    [(bx1, by1), (tip_x, tip_y), (bx2, by2)])
                pygame.draw.polygon(game_surf, (255, 255, 255),
                                    [(bx1, by1), (tip_x, tip_y), (bx2, by2)], 1)

                if pig_state == "hanging":
                    bar_w = 320
                    bar_x = GW // 2 - bar_w // 2
                    bar_y = 55
                    pygame.draw.rect(game_surf, (20, 10, 5), (bar_x - 3, bar_y - 3, bar_w + 6, 26))
                    pygame.draw.rect(game_surf, (60, 20, 20), (bar_x, bar_y, bar_w, 20))
                    rope_pct = rope_hp / rope_max_hp
                    if rope_pct > 0.5:
                        col = (int(255 * (1 - rope_pct) * 2), 220, 60)
                    else:
                        col = (220, int(255 * rope_pct * 2), 40)
                    pygame.draw.rect(game_surf, col,
                                     (bar_x, bar_y, int(bar_w * rope_pct), 20))
                    pygame.draw.rect(game_surf, (255, 255, 255),
                                     (bar_x, bar_y, bar_w, 20), 2)
                    rope_label = g_small.render("ROPE — CLICK/SPACE to cut!",
                                                True, (255, 255, 255))
                    game_surf.blit(rope_label,
                                   (GW // 2 - rope_label.get_width() // 2, bar_y + 24))

                if pig_state == "falling":
                    ft = g_font.render("FALLING!", True, (255, 255, 0))
                    game_surf.blit(ft, (GW // 2 - ft.get_width() // 2, 100))
                if pig_state == "free":
                    rt = g_font.render("RUN TO EXIT!", True, (100, 255, 100))
                    game_surf.blit(rt, (GW // 2 - rt.get_width() // 2, 100))

            if current_level == 4:
                for ep in enemy_pigs:
                    ex, ey, er = int(ep['x']), int(ep['y']), int(ep['r'])
                    body_color = ep['color']
                    if ep['hit_flash'] > 0:
                        body_color = (255, 255, 255)
                    pygame.draw.circle(game_surf, body_color, (ex, ey), er)
                    pygame.draw.circle(game_surf, (min(body_color[0] + 40, 255),
                                                   min(body_color[1] + 40, 255),
                                                   min(body_color[2] + 40, 255)),
                                       (ex, ey + int(er * 0.2)), int(er * 0.4))
                    pygame.draw.circle(game_surf, (0, 0, 0), (ex - 4, ey + int(er * 0.2)), 2)
                    pygame.draw.circle(game_surf, (0, 0, 0), (ex + 4, ey + int(er * 0.2)), 2)
                    pygame.draw.circle(game_surf, (255, 255, 255), (ex - 8, ey - 8), 5)
                    pygame.draw.circle(game_surf, (0, 0, 0), (ex - 8, ey - 8), 3)
                    pygame.draw.circle(game_surf, (255, 255, 255), (ex + 8, ey - 8), 5)
                    pygame.draw.circle(game_surf, (0, 0, 0), (ex + 8, ey - 8), 3)
                    bar_w = 40
                    bar_x = ex - bar_w // 2
                    bar_y = ey - er - 12
                    pygame.draw.rect(game_surf, (60, 0, 0), (bar_x, bar_y, bar_w, 5))
                    hp_w = int(bar_w * (ep['hp'] / 3))
                    pygame.draw.rect(game_surf, (255, 80, 80), (bar_x, bar_y, hp_w, 5))

            if current_level != 5:
                px, py, pr = int(pig_x), int(pig_y), int(pig_radius)
                current_pig_color = (150, 110, 120) if is_in_mud else (235, 192, 203)
                snout_color = (110, 80, 90) if is_in_mud else (255, 105, 180)

                pygame.draw.circle(game_surf, current_pig_color, (px, py), pr)
                snout_r = int(pr * 0.45)
                snout_x, snout_y = px, py + int(pr * 0.2)
                pygame.draw.circle(game_surf, snout_color, (snout_x, snout_y), snout_r)
                pygame.draw.circle(game_surf, (0, 0, 0),
                                   (snout_x - int(snout_r * 0.3), snout_y), int(snout_r * 0.25))
                pygame.draw.circle(game_surf, (0, 0, 0),
                                   (snout_x + int(snout_r * 0.3), snout_y), int(snout_r * 0.25))

                eye_r = int(pr * 0.1)
                pygame.draw.circle(game_surf, (255, 255, 255),
                                   (px - int(pr * 0.3), py - int(pr * 0.2)), eye_r)
                pygame.draw.circle(game_surf, (0, 0, 0),
                                   (px - int(pr * 0.3), py - int(pr * 0.2)), int(eye_r * 0.5))
                pygame.draw.circle(game_surf, (255, 255, 255),
                                   (px + int(pr * 0.3), py - int(pr * 0.2)), eye_r)
                pygame.draw.circle(game_surf, (0, 0, 0),
                                   (px + int(pr * 0.3), py - int(pr * 0.2)), int(eye_r * 0.5))

                if current_level == 4:
                    pygame.draw.line(game_surf, (0, 0, 0),
                                     (px - int(pr * 0.45), py - int(pr * 0.4)),
                                     (px - int(pr * 0.15), py - int(pr * 0.28)), 4)
                    pygame.draw.line(game_surf, (0, 0, 0),
                                     (px + int(pr * 0.45), py - int(pr * 0.4)),
                                     (px + int(pr * 0.15), py - int(pr * 0.28)), 4)
                    pygame.draw.polygon(game_surf, (255, 255, 255),
                                        [(px - 8, py + int(pr * 0.45)),
                                         (px - 4, py + int(pr * 0.55)),
                                         (px, py + int(pr * 0.45))])
                    pygame.draw.polygon(game_surf, (255, 255, 255),
                                        [(px, py + int(pr * 0.45)),
                                         (px + 4, py + int(pr * 0.55)),
                                         (px + 8, py + int(pr * 0.45))])

                if current_level == 6 and knife_stuck:
                    knife_x = px + int(pr * 0.4)
                    knife_y = py - int(pr * 0.5)
                    pygame.draw.rect(game_surf, (60, 30, 10),
                                     (knife_x - 5, knife_y - 25, 10, 22), border_radius=3)
                    pygame.draw.rect(game_surf, (200, 200, 210),
                                     (knife_x - 9, knife_y - 4, 18, 5))
                    blade_pts = [
                        (knife_x - 4, knife_y),
                        (knife_x + 4, knife_y),
                        (knife_x, knife_y + int(pr * 0.55)),
                    ]
                    pygame.draw.polygon(game_surf, (220, 220, 235), blade_pts)
                    pygame.draw.polygon(game_surf, (255, 255, 255), blade_pts, 1)
                    for _ in range(3):
                        bx_off = random.randint(-6, 6)
                        by_off = random.randint(0, 12)
                        pygame.draw.circle(game_surf, (180, 20, 20),
                                           (knife_x + bx_off, knife_y + by_off),
                                           random.randint(2, 4))

            if current_level in (1, 2, 3):
                cx, cy = int(carrot_x), int(carrot_y)
                pygame.draw.polygon(game_surf, (211, 47, 47),
                                    [(cx - 15, cy - 15), (cx + 15, cy - 15), (cx, cy + 25)])
                pygame.draw.polygon(game_surf, (19, 195, 74),
                                    [(cx - 15, cy - 15), (cx + 15, cy - 15), (cx, cy - 35)])

            if current_level in (1, 2):
                hx, hy = int(human_x), int(human_y)
                pygame.draw.circle(game_surf, HUMAN_COLOR, (hx, hy), 30)
                pygame.draw.rect(game_surf, (25, 255, 255), (hx - 15, hy - 5, 30, 35))
                pygame.draw.line(game_surf, (25, 0, 0), (hx - 5, hy + 10), (hx + 5, hy + 20), 3)

            if current_level == 3 and wolf_alive:
                wx, wy = int(wolf_x), int(wolf_y)
                pygame.draw.circle(game_surf, WOLF_COLOR, (wx, wy), 28)
                pygame.draw.circle(game_surf, WOLF_DARK, (wx, wy - 20), 18)
                pygame.draw.polygon(game_surf, WOLF_DARK,
                                    [(wx - 14, wy - 32), (wx - 6, wy - 42), (wx - 2, wy - 30)])
                pygame.draw.polygon(game_surf, WOLF_DARK,
                                    [(wx + 14, wy - 32), (wx + 6, wy - 42), (wx + 2, wy - 30)])
                pygame.draw.circle(game_surf, (255, 0, 0), (wx - 7, wy - 22), 3)
                pygame.draw.circle(game_surf, (255, 0, 0), (wx + 7, wy - 22), 3)
                bar_w = 50
                bar_x = wx - bar_w // 2
                bar_y = wy - 55
                pygame.draw.rect(game_surf, (80, 0, 0), (bar_x, bar_y, bar_w, 6))
                hp_w = int(bar_w * (wolf_hp / 100))
                pygame.draw.rect(game_surf, (220, 40, 40), (bar_x, bar_y, hp_w, 6))

            if current_level == 3:
                hx, hy = int(hunter_x), int(hunter_y)
                pygame.draw.circle(game_surf, HUNTER_COLOR, (hx, hy), 22)
                pygame.draw.ellipse(game_surf, HUNTER_HAT, (hx - 22, hy - 30, 44, 14))
                pygame.draw.rect(game_surf, HUNTER_HAT, (hx - 14, hy - 34, 28, 12))
                angle = math.atan2(wolf_y - hy, wolf_x - hx) if wolf_alive else 0
                gun_len = 30
                gx = hx + math.cos(angle) * gun_len
                gy = hy + math.sin(angle) * gun_len
                pygame.draw.line(game_surf, (30, 30, 30), (hx, hy), (gx, gy), 6)
                pygame.draw.circle(game_surf, (0, 0, 0), (int(gx), int(gy)), 4)

            for bullet in bullets:
                pygame.draw.circle(game_surf, (255, 240, 100),
                                   (int(bullet[0]), int(bullet[1])), 4)
                pygame.draw.circle(game_surf, (255, 180, 0),
                                   (int(bullet[0]), int(bullet[1])), 2)

            if bite_effect_timer > 0 and current_level == 4:
                bx, by = int(bite_effect_pos[0]), int(bite_effect_pos[1])
                radius = int(20 + (0.3 - bite_effect_timer) * 100)
                pygame.draw.circle(game_surf, (255, 100, 100), (bx, by), radius, 3)
                pygame.draw.circle(game_surf, (255, 50, 50), (bx, by), max(radius - 8, 0), 2)

            if current_level == 6:
                for p in blood_particles:
                    size = int(p['size'])
                    pygame.draw.circle(game_surf, (150, 0, 0),
                                       (int(p['x']), int(p['y'])), size)
                    pygame.draw.circle(game_surf, (200, 30, 30),
                                       (int(p['x']), int(p['y'])), max(size - 1, 1))
                if vignette_alpha > 0:
                    vig_surf = pygame.Surface((GW, GH), pygame.SRCALPHA)
                    for i in range(8):
                        a = int(vignette_alpha * (1 - i / 8))
                        pygame.draw.rect(vig_surf, (120, 0, 0, a), (0, i * 15, GW, 15))
                        pygame.draw.rect(vig_surf, (120, 0, 0, a),
                                         (0, GH - (i + 1) * 15, GW, 15))
                        pygame.draw.rect(vig_surf, (120, 0, 0, a), (i * 15, 0, 15, GH))
                        pygame.draw.rect(vig_surf, (120, 0, 0, a),
                                         (GW - (i + 1) * 15, 0, 15, GH))
                    game_surf.blit(vig_surf, (0, 0))

            # HUD
            if current_level == 2:
                pygame.draw.rect(game_surf, (0, 0, 0), (GW - 160, 15, 150, 20))
                energy_color = (0, 255, 0) if energy > 30 else (255, 0, 0)
                pygame.draw.rect(game_surf, energy_color, (GW - 155, 15, int(1.4 * energy), 14))
                game_surf.blit(g_font.render("Energy:", True, (255, 255, 25)), (GW - 260, 12))

            if current_level == 3:
                pygame.draw.rect(game_surf, (0, 0, 0), (GW - 260, 15, 250, 20))
                time_color = (0, 255, 0) if time_left > 10 else (255, 0, 0)
                bar_width = int((time_left / 30.0) * 245)
                pygame.draw.rect(game_surf, time_color, (GW - 255, 17, bar_width, 16))
                game_surf.blit(g_small.render(f"Time: {time_left:.1f}s", True, (255, 255, 255)),
                               (GW - 260, 40))
                game_surf.blit(g_small.render(f"Ammo: {hunter_ammo}", True, (255, 220, 100)),
                               (GW - 260, 68))
                if wolf_alive:
                    game_surf.blit(g_small.render("Wolf: HUNTING", True, (255, 80, 80)),
                                   (GW - 260, 95))
                else:
                    game_surf.blit(g_small.render("Wolf: DEAD!", True, (100, 255, 100)),
                                   (GW - 260, 95))

            if current_level == 4:
                pygame.draw.rect(game_surf, (0, 0, 0), (GW - 260, 15, 250, 20))
                time_color = (0, 255, 0) if time_left > 15 else (255, 0, 0)
                bar_width = int((time_left / 40.0) * 245)
                pygame.draw.rect(game_surf, time_color, (GW - 255, 17, bar_width, 16))
                game_surf.blit(g_small.render(f"Time: {time_left:.1f}s", True, (255, 255, 255)),
                               (GW - 260, 40))

            if current_level == 6:
                bar_w = 340
                bar_x = GW // 2 - bar_w // 2
                bar_y = GH - 40
                pygame.draw.rect(game_surf, (20, 0, 0), (bar_x - 3, bar_y - 3, bar_w + 6, 26))
                pygame.draw.rect(game_surf, (60, 15, 15), (bar_x, bar_y, bar_w, 20))
                blood_pct = blood / blood_max
                if blood_pct > 0.5:
                    col = (200, 20, 20)
                elif blood_pct > 0.25:
                    col = (150, 10, 10)
                else:
                    col = (100, 0, 0)
                pygame.draw.rect(game_surf, col,
                                 (bar_x, bar_y, int(bar_w * blood_pct), 20))
                label = g_small.render("BLOOD", True, (255, 255, 255))
                game_surf.blit(label,
                               (bar_x + bar_w // 2 - label.get_width() // 2, bar_y - 25))

            game_surf.blit(g_font.render(f"LEVEL {current_level}", True, (255, 255, 255)), (10, 10))

            if current_level == 1:
                game_surf.blit(g_font.render(f"Carrots: {carrots_eaten}/10",
                                             True, (255, 25, 255)), (10, 40))
            elif current_level == 2:
                if carrots_eaten < 5:
                    game_surf.blit(g_font.render(f"Eat Carrots to Find Mud: {carrots_eaten}/5",
                                                 True, (255, 255, 25)), (10, 40))
                else:
                    game_surf.blit(g_font.render("MUD FOUND! RUN TO IT!",
                                                 True, (25, 255, 255)), (10, 40))
            elif current_level == 3:
                game_surf.blit(g_font.render(f"Carrots: {carrots_eaten}/15",
                                             True, (255, 25, 255)), (10, 40))
                if wolf_alive:
                    game_surf.blit(g_tiny.render("Survive the wolf - hunter is coming!",
                                                 True, (255, 200, 200)), (10, 78))
                else:
                    game_surf.blit(g_tiny.render("Wolf dead! RUN TO HOME!",
                                                 True, (100, 255, 100)), (10, 78))
            elif current_level == 4:
                game_surf.blit(g_font.render("ANGRY PIGLET", True, (255, 60, 60)), (10, 45))
                game_surf.blit(g_small.render(f"Bites: {bite_count}/{bite_target}",
                                              True, (255, 200, 60)), (10, 82))
                game_surf.blit(g_tiny.render(f"Enemy pigs left: {len(enemy_pigs)}",
                                             True, (255, 200, 200)), (10, 110))
                game_surf.blit(g_tiny.render("CLICK near a pig to bite it!",
                                             True, (255, 255, 100)), (10, 132))
            elif current_level == 5:
                game_surf.blit(g_font.render("HANGING PIGLET", True, (255, 80, 80)), (10, 45))
                if pig_state == "hanging":
                    game_surf.blit(g_small.render("SPACE or CLICK to cut the rope!",
                                                  True, (255, 220, 100)), (10, 82))
                    game_surf.blit(g_tiny.render("Then RUN to the EXIT (right side)!",
                                                 True, (255, 200, 200)), (10, 110))
                elif pig_state == "falling":
                    game_surf.blit(g_small.render("You're falling! Get ready to RUN!",
                                                  True, (255, 255, 0)), (10, 82))
                else:
                    game_surf.blit(g_small.render("RUN! Use mouse to escape to EXIT!",
                                                  True, (100, 255, 100)), (10, 82))
            elif current_level == 6:
                game_surf.blit(g_font.render("WOUNDED PIGLET", True, (255, 60, 60)), (10, 45))
                game_surf.blit(g_small.render("The butcher stabbed you!",
                                              True, (255, 200, 200)), (10, 82))
                game_surf.blit(g_tiny.render("RUN to the VET (top-right) before you bleed out!",
                                             True, (255, 255, 100)), (10, 110))
                blood_pct_txt = g_small.render(f"Blood: {int(blood)}%", True,
                                               (255, 100, 100) if blood < 40 else (255, 255, 255))
                game_surf.blit(blood_pct_txt, (10, 135))

            # ESC hint
            game_surf.blit(g_tiny.render("Press ESC to return to Aero OS",
                                         True, (180, 180, 180)), (10, GH - 25))
        else:
            game_surf.fill((0, 0, 0))
            if win:
                if current_level == 1:
                    win_text = "LEVEL 1 CLEAR! Piglet is safe!"
                    btn_str = "NEXT LEVEL"
                elif current_level == 2:
                    win_text = "SAFE IN MUD! LEVEL 2 CLEAR!"
                    btn_str = "NEXT LEVEL"
                elif current_level == 3:
                    win_text = "YOU SURVIVED! HUNTER SAVED YOU!"
                    btn_str = "NEXT LEVEL"
                elif current_level == 4:
                    win_text = "ANGRY PIGLET SATISFIED!"
                    btn_str = "NEXT LEVEL"
                elif current_level == 5:
                    win_text = "YOU ESCAPED THE BUTCHER!"
                    btn_str = "NEXT LEVEL"
                else:
                    win_text = "THE VET SAVED YOU! YOU WIN!"
                    btn_str = "PLAY AGAIN"
                text_surf = g_font.render(win_text, True, (0, 255, 0))
                game_surf.blit(text_surf, (GW // 2 - text_surf.get_width() // 2, GH // 2 - 20))
                pygame.draw.rect(game_surf, (46, 125, 50), button_rect, border_radius=10)
                btn_text = g_font.render(btn_str, True, (255, 255, 255))
                game_surf.blit(btn_text, (GW // 2 - btn_text.get_width() // 2, GH // 2 + 52))
            else:
                text_surf = g_font.render(loss_reason, True, (255, 0, 0))
                game_surf.blit(text_surf, (GW // 2 - text_surf.get_width() // 2, GH // 2 - 20))
                pygame.draw.rect(game_surf, (211, 47, 47), button_rect, border_radius=10)
                btn_text = g_font.render("RESTART", True, (255, 255, 255))
                game_surf.blit(btn_text, (GW // 2 - btn_text.get_width() // 2, GH // 2 + 52))

            game_surf.blit(g_tiny.render("Press ESC to return to Aero OS",
                                         True, (180, 180, 180)), (10, GH - 25))

        # inner surface -> ეკრანზე (მასშტაბირება)
        scaled = pygame.transform.scale(game_surf, (WIDTH, HEIGHT))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()


# ============================================================
# AERO OS მთავარი ციკლი
# ============================================================
running = True
while running:
    screen.fill(BACKGROUND_COLOR)

    title_surface = title_font.render("AERO PLATFORM", True, TEXT_COLOR)
    screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 50))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                if selected_index < len(games) - 1:
                    selected_index += 1
            elif event.key == pygame.K_LEFT:
                if selected_index > 0:
                    selected_index -= 1
            elif event.key == pygame.K_RETURN:
                game = games[selected_index]
                if game["package"] == "piglet_escape":
                    run_piglet_escape()
                else:
                    print(f"გაეშვა თამაში: {game['title']} (placeholder)")

        # შეხება / მაუსის დაჭერა ბარათზე
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            card_width, card_height = 250, 350
            start_x = (WIDTH - (len(games) * (card_width + 40))) // 2
            y_pos = HEIGHT // 2 - card_height // 2
            for i, game in enumerate(games):
                x_pos = start_x + i * (card_width + 40)
                card_rect = pygame.Rect(x_pos, y_pos, card_width, card_height)
                if card_rect.collidepoint(mx, my):
                    selected_index = i
                    if game["package"] == "piglet_escape":
                        run_piglet_escape()

    # ბარათების ხატვა
    card_width, card_height = 250, 350
    start_x = (WIDTH - (len(games) * (card_width + 40))) // 2
    y_pos = HEIGHT // 2 - card_height // 2

    for i, game in enumerate(games):
        x_pos = start_x + i * (card_width + 40)
        card_rect = pygame.Rect(x_pos, y_pos, card_width, card_height)

        if i == selected_index:
            pygame.draw.rect(screen, ACTIVE_COLOR, card_rect, border_radius=15)
            pygame.draw.rect(screen, (0, 255, 255), card_rect, width=4, border_radius=15)
        else:
            pygame.draw.rect(screen, CARD_COLOR, card_rect, border_radius=15)

        text_surface = font.render(game["title"], True, TEXT_COLOR)
        text_x = x_pos + (card_width // 2) - (text_surface.get_width() // 2)
        text_y = y_pos + card_height - 60
        screen.blit(text_surface, (text_x, text_y))

        # მინიშნება
        if game["package"] == "piglet_escape":
            hint = small_font.render("ENTER / CLICK to play", True, (200, 255, 200))
            screen.blit(hint, (x_pos + (card_width // 2) - (hint.get_width() // 2),
                               y_pos + card_height - 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
