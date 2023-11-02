import ai
import images
import json
import math
import pygame
import random

# FNaF 4 Remake by me
# All images, audio, and characters used in this project are owned by Scott Cawthon.


def create_default_config(config_dict):
    config_file = open('config.json', 'w')
    json.dump(config_dict, config_file, indent=4)
    config_file.close()
    print('Created config.json. Wrote default config.')


def load_config(config_dict):
    # ensure json exists
    try:
        json_string = read_config()
    except FileNotFoundError:
        print('Could not find config.json. Creating new file...')
        create_default_config(config_dict)
        json_string = read_config()
    # then ensure json is valid
    try:
        return json.loads(json_string)
    except json.decoder.JSONDecodeError:
        print('JSON invalid. Rewriting file...')
        create_default_config(config_dict)
        json_string = read_config()
        return json.loads(json_string)


def read_config():
    config_file = open('config.json', 'r')
    print('Read config.json.')
    return config_file.read()


def set_ai_levels():
    if night == 1:
        bonnie.ai = 0
        chica.ai = 0
    elif night == 2:
        bonnie.ai = 5
        chica.ai = 5


def mouse_delta_x():
    # very close estimates
    mouse_x = pygame.mouse.get_pos()[0] + 1  # add 1 so the math works out (max 1024 instead of 1023)
    if mouse_x > 4 / 5 * SCREEN_X:
        # fast right
        return -12
    elif mouse_x > 2 / 3 * SCREEN_X:
        # slow right
        return -6
    elif mouse_x < 1 / 5 * SCREEN_X:
        # fast left
        return 12
    elif mouse_x < 1 / 3 * SCREEN_X:
        # slow left
        return 6
    return 0


if __name__ == '__main__':
    pygame.init()
    SCREEN_X = 1024
    SCREEN_Y = 768
    SCREEN_SIZE = (SCREEN_X, SCREEN_Y)
    window = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Five Nights at Freddy\'s 4')
    icon = pygame.image.load('assets/icon/favicon.png').convert()
    pygame.display.set_icon(icon)
    clock = pygame.time.Clock()
    running = True
    font = pygame.font.Font(None, 16)

    default_config = {
        'night': 1,
        'hour': 0,
        'disable_jumpscares': False,
        'override_ai': False,
        'bonnie_ai': 20,
        'chica_ai': 20,
        'enable_debug_text': False,
        'enable_cheat_keys': False,
        'disable_natural_ai_changes': False
    }
    config = load_config(default_config)
    night = config['night']
    hour = config['hour']
    disable_jumpscares = config['disable_jumpscares']
    override_ai = config['override_ai']
    enable_debug_text = config['enable_debug_text']
    enable_cheat_keys = config['enable_cheat_keys']
    disable_natural_ai_changes = config['disable_natural_ai_changes']

    # convert image pixel formats for performant blit
    for s in images.screens:
        for i in images.screens[s].images:
            i.convert()
    screen = images.screens['room']
    room_width = screen.images[0].get_width()
    running_location = ''
    animation_frame = 0
    retreat_frame = 0

    # should be accurate hitboxes
    left_door_rect = pygame.Rect(18, 148, 262, 538)
    right_door_rect = pygame.Rect(SCREEN_X - 262 - 18, 148, 262, 538)
    run_back_rect = pygame.Rect(10, 682, 998, 80)

    bonnie = ai.Animatronic('bonnie', 'mid', random.randint(2, 5), 'left')
    chica = ai.Animatronic('chica', 'mid', random.randint(3, 5), 'right')

    if override_ai:
        bonnie.ai = config['bonnie_ai']
        chica.ai = config['chica_ai']
    else:
        set_ai_levels()

    hour_event = pygame.USEREVENT + 1
    hour_number = images.screens['hour']
    num_width = hour_number.images[0].get_width()

    second_event = pygame.USEREVENT + 2
    listening = ''
    door_shut = ''
    retreating = ''
    viewing_hall = ''
    viewing_bed = False
    random_bed_view = random.randint(1, 100)

    run_back_debounce = False
    game_over = False
    jumpscared_by = ''
    cleared = False

    pygame.time.set_timer(hour_event, 60000)
    pygame.time.set_timer(second_event, 1000)
    second_intervals = 0

    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == second_event:
                second_intervals += 1
                bonnie.interval_update(second_intervals, door_shut, listening, screen)
                chica.interval_update(second_intervals, door_shut, listening, screen)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if screen.name == 'room':
                    if left_door_rect.collidepoint(pygame.mouse.get_pos()) and animation_frame == 0:
                        screen = images.screens['run_left_door']
                        animation_frame = 0
                    elif right_door_rect.collidepoint(pygame.mouse.get_pos()) and animation_frame == screen.frames - 1:
                        screen = images.screens['run_right_door']
                        animation_frame = 0
            elif event.type == hour_event:
                hour += 1
                if not disable_natural_ai_changes:
                    if night == 1:
                        if hour == 2:
                            bonnie.ai += 1
                            chica.ai += 1
                        elif hour == 3:
                            bonnie.ai += 2
                            chica.ai += 1
                    elif night == 2:
                        if hour == 3:
                            bonnie.ai += 2
                            chica.ai += 2
                    elif night == 3:
                        if hour == 3:
                            bonnie.ai += 3
                            chica.ai += 3
                    elif night == 4:
                        if hour == 3:
                            bonnie.ai += 2
                            chica.ai += 2
                    elif night == 6:
                        if hour == 4:
                            bonnie.ai -= 12
                            chica.ai -= 12
                if 2 <= night <= 4:
                    if hour == bonnie.force_move_hour:
                        bonnie.force_move = True
                    if hour == chica.force_move_hour:
                        chica.force_move = True
            elif event.type == pygame.KEYDOWN:
                if enable_cheat_keys:
                    if event.key == pygame.K_t:
                        pygame.event.post(pygame.event.Event(hour_event))
                    elif event.key == pygame.K_b:
                        screen = images.screens['jumpscare_bonnie_room']
                        animation_frame = 0
                        bonnie.room_jumpscare = True
                    elif event.key == pygame.K_c:
                        chica.room_jumpscare = True
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
            elif event.type == pygame.QUIT:
                pygame.quit()

        if hour == 6:
            running = False

        listening = ''
        viewing_hall = ''

        if retreating == '':
            retreat_frame = 0
        else:
            if retreat_frame < 15:
                retreat_frame += 0.5
            else:
                retreating = ''

        if screen.name == 'room':
            # looking around the room
            screen.x += mouse_delta_x()

            # flashlight animation
            if screen.x <= SCREEN_X - room_width:  # right side clamp
                animation_frame += 0.5
                screen.x = SCREEN_X - room_width
            elif screen.x >= 0:  # left side clamp
                animation_frame -= 0.5
                screen.x = 0
            else:  # move light to middle
                if animation_frame < 4:
                    animation_frame += 0.5
                elif animation_frame > 4:
                    animation_frame -= 0.5
            # update these screens since they are wide (after clamp)
            images.screens['run_left_door'].x = screen.x
            images.screens['run_right_door'].x = screen.x
            images.screens['run_bed'].x = screen.x
            images.screens['start_room_bed'].x = screen.x
            # start room doesn't need since it's always in the same spot
            if animation_frame > screen.frames - 1:  # right side clamp animation
                animation_frame = screen.frames - 1
            elif animation_frame < 0:  # left side clamp animation
                animation_frame = 0
            if run_back_rect.collidepoint(pygame.mouse.get_pos()):
                if not run_back_debounce:
                    screen = images.screens['run_bed']
                    run_back_debounce = True
                    animation_frame = 0
            else:
                run_back_debounce = False
        elif screen.name == 'run_left_door':
            if animation_frame < screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['running']
                running_location = 'start_left_door'
                animation_frame = 0
        elif screen.name == 'run_right_door':
            if animation_frame < screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['running']
                running_location = 'start_right_door'
                animation_frame = 0
        elif screen.name == 'running':
            if animation_frame < screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens[running_location]
                animation_frame = 0
        elif screen.name == 'start_left_door':
            if animation_frame < screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['left_door']
                animation_frame = 0
        elif screen.name == 'start_right_door':
            if animation_frame < screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['right_door']
                animation_frame = 0
        elif screen.name == 'left_door':
            # in order of priority in the game
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                if animation_frame < screen.frames - 1:
                    # frames 2 and above are closing door
                    if animation_frame <= 1:
                        animation_frame = 2
                    else:
                        animation_frame += 0.5
                else:
                    door_shut = 'left'
                    if bonnie.location == 'hall_far':
                        bonnie.location = 'hall_near'
                        # bringing them closer by closing the door cancels bonnie and chica until opened again
                        ai.Animatronic.cancel_movement = True
                        bonnie.will_move = False
            elif animation_frame > 2:
                door_shut = ''
                ai.Animatronic.cancel_movement = False
                animation_frame -= 0.5
            elif keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                animation_frame = 1
                viewing_hall = 'left'
                if bonnie.location == 'hall_far':
                    bonnie.location = 'mid'
                    retreating = 'bonnie'
                elif bonnie.location == 'hall_near':
                    screen = images.screens['jumpscare_bonnie_hall']
                    animation_frame = 0
            elif run_back_rect.collidepoint(pygame.mouse.get_pos()):
                screen = images.screens['leave_left_door']
                animation_frame = 0
            else:
                # closing door animation does not count as listening
                listening = 'left'
                animation_frame = 0
        elif screen.name == 'right_door':
            # in order of priority in the game
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                if animation_frame < screen.frames - 1:
                    # frames 2 and above are closing door
                    if animation_frame <= 1:
                        animation_frame = 2
                    else:
                        animation_frame += 0.5
                else:
                    door_shut = 'right'
                    if chica.location == 'hall_far':
                        chica.location = 'hall_near'
                        # bringing them closer by closing the door cancels bonnie and chica until opened again
                        ai.Animatronic.cancel_movement = True
                        chica.will_move = False
            elif animation_frame > 2:
                door_shut = ''
                ai.Animatronic.cancel_movement = False
                animation_frame -= 0.5
            elif keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                animation_frame = 1
                viewing_hall = 'right'
                if chica.location == 'hall_far':
                    chica.location = 'mid'
                    retreating = 'chica'
                elif chica.location == 'hall_near':
                    screen = images.screens['jumpscare_chica_hall']
                    animation_frame = 0
            elif run_back_rect.collidepoint(pygame.mouse.get_pos()):
                screen = images.screens['leave_right_door']
                animation_frame = 0
            else:
                # closing door animation does not count as listening
                listening = 'right'
                animation_frame = 0
        elif screen.name == 'leave_left_door' or screen.name == 'leave_right_door':
            if animation_frame < screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['running']
                running_location = 'start_room'
                animation_frame = 0
        elif screen.name == 'start_room':
            if animation_frame < screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['room']
                animation_frame = 4
                screen.x = -240
        elif screen.jumpscare:
            game_over = True
            if not disable_jumpscares:
                if animation_frame < screen.frames - 1:
                    animation_frame += 0.5
                else:
                    running = False
        elif screen.name == 'run_bed':
            if animation_frame < screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['start_bed']
                animation_frame = 0
        elif screen.name == 'start_bed':
            if animation_frame < screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['bed']
                animation_frame = 22
        elif screen.name == 'bed':
            if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                viewing_bed = True
                if random_bed_view == 1:
                    animation_frame = 19
                elif random_bed_view == 2:
                    animation_frame = 20
                elif random_bed_view == 3:
                    animation_frame = 21
                else:
                    animation_frame = 18
            else:
                viewing_bed = False
                random_bed_view = random.randint(1, 100)
                animation_frame = 22
            if run_back_rect.collidepoint(pygame.mouse.get_pos()) or ai.Animatronic.force_turn:
                if not run_back_debounce and not viewing_bed or ai.Animatronic.force_turn:
                    screen = images.screens['leave_bed']
                    animation_frame = 0
                    run_back_debounce = True
            else:
                run_back_debounce = False
        elif screen.name == 'leave_bed':
            if animation_frame < screen.frames - 1:
                animation_frame += 0.5
            else:
                # priority: chica, bonnie, freddy bed, freddy not flashlight, foxy force
                # when freddy counter >= 80, timer of 50 + random(0 to 49) counts down until 1, then jumpscare happens
                if chica.room_jumpscare:
                    screen = images.screens['jumpscare_chica_room']
                    animation_frame = 0
                elif bonnie.room_jumpscare:
                    screen = images.screens['jumpscare_bonnie_room']
                    animation_frame = 0
                else:
                    screen = images.screens['start_room_bed']
                    animation_frame = 0
        elif screen.name == 'start_room_bed':
            if animation_frame < screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['room']
                animation_frame = 4

        bonnie.update(screen, night)
        chica.update(screen, night)

        bonnie.move(viewing_hall)
        chica.move(viewing_hall)

        # we increment frames by 0.5 to get that 30 fps animation FNaF 4 seems to have, so floor all the frame values
        if disable_jumpscares and screen.jumpscare:
            window.fill((0, 0, 0))
            window.blit(font.render(f'Jumpscare: {screen.name}', True, (255, 255, 255)), (380, 50))
            running = False
        else:
            window.blit(screen.images[math.floor(animation_frame)], (screen.x, screen.y))
        if retreating == 'bonnie' and viewing_hall == 'left':
            window.blit(images.screens['retreating_bonnie'].images[math.floor(retreat_frame)], (0, 0))
        elif retreating == 'chica' and viewing_hall == 'right':
            window.blit(images.screens['retreating_chica'].images[math.floor(retreat_frame)], (0, 0))
        # time
        if hour == 0:
            window.blit(hour_number.images[0], (hour_number.x, hour_number.y))
            window.blit(hour_number.images[1], (hour_number.x + num_width, hour_number.y))
        else:
            window.blit(hour_number.images[hour - 1], (hour_number.x + num_width, hour_number.y))
        window.blit(hour_number.images[hour_number.frames - 1], (958, 32))

        if enable_debug_text:
            window.blit(font.render(f'Bonnie location: {bonnie.location}', True, (255, 255, 255)), (0, 0))
            window.blit(font.render(f'Chica location: {chica.location}', True, (255, 255, 255)), (0, 16))
            pending_jumpscares = []
            if chica.room_jumpscare:
                pending_jumpscares.append(chica.name)
            if bonnie.room_jumpscare:
                pending_jumpscares.append(bonnie.name)
            pending_jumpscares_text = ', '.join(pending_jumpscares)
            window.blit(font.render(f'Jumpscares pending: {pending_jumpscares_text}', True, (255, 255, 255)), (0, 32))
            window.blit(font.render(f'Bonnie AI: {bonnie.ai}', True, (255, 255, 255)), (0, 48))
            window.blit(font.render(f'Chica AI: {chica.ai}', True, (255, 255, 255)), (0, 64))
            window.blit(font.render(f'Screen: {screen.name}', True, (255, 255, 255)), (0, 80))
            window.blit(font.render(f'Frame: {math.floor(animation_frame)}', True, (255, 255, 255)), (0, 96))
            window.blit(font.render(f'{round(clock.get_fps())} FPS', True, (255, 255, 255)), (0, 112))

        pygame.display.flip()
        dt = clock.tick(60)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
            elif event.type == pygame.QUIT:
                pygame.quit()
