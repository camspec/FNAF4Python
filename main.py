import json
import math
import random

import pygame

import ai
import images


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
        freddy.ai = 0
        foxy.ai = 0
    elif night == 2:
        bonnie.ai = 5
        chica.ai = 5
        freddy.ai = 2
        foxy.ai = 1
    elif night == 3:
        bonnie.ai = 7
        chica.ai = 7
        freddy.ai = 3
        foxy.ai = 10
    elif night == 4:
        bonnie.ai = 10
        chica.ai = 10
        freddy.ai = 4
        foxy.ai = 5


def move_screen():
    if fast_left_rect.collidepoint(pygame.mouse.get_pos()):
        screen.x += 6
    if slow_left_rect.collidepoint(pygame.mouse.get_pos()):
        screen.x += 6
    if fast_right_rect.collidepoint(pygame.mouse.get_pos()):
        screen.x -= 6
    if slow_right_rect.collidepoint(pygame.mouse.get_pos()):
        screen.x -= 6


def draw_text(string, x, row):
    window.blit(font.render(string, True, (255, 255, 255)), (x, row * 16))


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
        'freddy_ai': 20,
        'foxy_ai': 20,
        'enable_debug_text': False,
        'enable_advanced_debug_text': False,
        'enable_cheat_keys': False,
        'disable_natural_ai_changes': False,
        'draw_hitboxes': False,
        'hitbox_alpha': 50
    }
    config = load_config(default_config)
    night = config['night']
    hour = config['hour']
    disable_jumpscares = config['disable_jumpscares']
    override_ai = config['override_ai']
    enable_debug_text = config['enable_debug_text']
    enable_advanced_debug_text = config['enable_advanced_debug_text']
    enable_cheat_keys = config['enable_cheat_keys']
    disable_natural_ai_changes = config['disable_natural_ai_changes']
    draw_hitboxes = config['draw_hitboxes']
    hitbox_alpha = config['hitbox_alpha']

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
    debounce_rect = pygame.Rect(12, 464, 998, 192)
    closet_rect = pygame.Rect(576, 130, 262, 538)
    fast_left_rect = pygame.Rect(-3, -13, 206, 778)
    slow_left_rect = pygame.Rect(-7, -13, 348, 778)
    fast_right_rect = pygame.Rect(821, -3, 206, 778)
    slow_right_rect = pygame.Rect(681, -1, 344, 778)

    bonnie = ai.Animatronic('bonnie', 'mid', random.randint(2, 5), 'left')
    chica = ai.Animatronic('chica', 'mid', random.randint(3, 5), 'right')
    freddy = ai.Animatronic('freddy')
    foxy = ai.Animatronic('foxy', 'mid')

    if override_ai:
        bonnie.ai = config['bonnie_ai']
        chica.ai = config['chica_ai']
        freddy.ai = config['freddy_ai']
        foxy.ai = config['foxy_ai']
    else:
        set_ai_levels()

    hour_event = pygame.USEREVENT + 1
    hour_number = images.screens['hour']
    num_width = hour_number.images[0].get_width()

    second_event = pygame.USEREVENT + 2
    listening = ''
    door_shut = ''
    door_status = 'open'
    retreating = ''
    viewing_hall = ''
    viewing_bed = False
    viewing_closet = False
    random_bed_view = random.randint(1, 100)

    twentieth_second_event = pygame.USEREVENT + 3
    fifth_second_event = pygame.USEREVENT + 4

    run_back_debounce = False
    game_over = False
    jumpscared_by = ''
    cleared = False
    foxy_bit = False

    pygame.time.set_timer(hour_event, 60000)
    pygame.time.set_timer(second_event, 1000)
    pygame.time.set_timer(twentieth_second_event, 50)
    pygame.time.set_timer(fifth_second_event, 200)
    second_intervals = 0
    afk_seconds = 0
    seconds_looking_at_bed = 0

    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == twentieth_second_event:
                if viewing_bed and freddy.progress > 0:
                    if freddy.progress == 30:
                        retreating = 'freddle_3'
                        retreat_frame = 0
                    elif freddy.progress == 20:
                        retreating = 'freddle_2'
                        retreat_frame = 5
                    elif freddy.progress == 10:
                        retreating = 'freddle_1'
                        retreat_frame = 10
                    freddy.progress -= 1
            elif event.type == fifth_second_event:
                # if you haven't run in 30 seconds on night 2+, progress is constant
                if night > 1 and afk_seconds >= 30 and not viewing_bed:
                    freddy.progress += 1
            elif event.type == second_event:
                second_intervals += 1
                afk_seconds += 1
                if viewing_bed:
                    seconds_looking_at_bed += 1
                chica.interval_update(second_intervals, door_shut, listening)
                bonnie.interval_update(second_intervals, door_shut, listening)
                freddy.interval_update(second_intervals, viewing_bed=viewing_bed, screen=screen)
                foxy.interval_update(second_intervals, door_shut)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if screen.name == 'room':
                    if left_door_rect.collidepoint(pygame.mouse.get_pos()) and animation_frame == 0:
                        screen = images.screens['run_left_door']
                        animation_frame = 0
                    elif right_door_rect.collidepoint(pygame.mouse.get_pos()) and animation_frame == screen.frames - 1:
                        screen = images.screens['run_right_door']
                        animation_frame = 0
                    elif closet_rect.collidepoint(pygame.mouse.get_pos()) and animation_frame == 4:
                        screen = images.screens['run_closet']
                        animation_frame = 0
            elif event.type == hour_event:
                hour += 1
                if not disable_natural_ai_changes:
                    if night == 1:
                        if hour == 2:
                            bonnie.ai += 1
                            chica.ai += 1
                            freddy.ai += 1
                        elif hour == 3:
                            bonnie.ai += 2
                            chica.ai += 1
                            freddy.ai += 1
                    elif night == 2:
                        if hour == 3:
                            bonnie.ai += 2
                            chica.ai += 2
                            freddy.ai += 1
                            foxy.ai += 3
                    elif night == 3:
                        if hour == 3:
                            bonnie.ai += 3
                            chica.ai += 3
                    elif night == 4:
                        if hour == 3:
                            bonnie.ai += 2
                            chica.ai += 2
                            foxy.ai += 5
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
                        bonnie.location = 'hall_near'
                        bonnie.seconds_at_door = 21 - night
                    elif event.key == pygame.K_c:
                        chica.location = 'hall_near'
                        chica.seconds_at_door = 21 - night
                    elif event.key == pygame.K_f:
                        freddy.progress += 10
                    elif event.key == pygame.K_h:
                        foxy.location = 'right_hall'
                    elif event.key == pygame.K_j:
                        foxy.progress += 1
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
            elif event.type == pygame.QUIT:
                pygame.quit()

        if hour == 6:
            running = False

        listening = ''
        viewing_hall = ''
        viewing_closet = False

        # simple animation cycles depending on which screen is selected
        # if the frame is the last, go back to the first frame
        # also initialize frame number when switching screens
        if screen.name == 'room':
            move_screen()

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
            # start room and closet creak don't need to update since they're always in the same spot
            images.screens['run_left_door'].x = screen.x
            images.screens['run_right_door'].x = screen.x
            images.screens['run_bed'].x = screen.x
            images.screens['start_room_bed'].x = screen.x
            images.screens['run_closet'].x = screen.x
            closet_rect.x = screen.x + 576
            if animation_frame > screen.frames - 1:  # right side clamp animation
                animation_frame = screen.frames - 1
            elif animation_frame < 0:  # left side clamp animation
                animation_frame = 0
            if run_back_rect.collidepoint(pygame.mouse.get_pos()):
                if not run_back_debounce:
                    screen = images.screens['run_bed']
                    run_back_debounce = True
                    animation_frame = 0
            elif debounce_rect.collidepoint(pygame.mouse.get_pos()):
                run_back_debounce = False
        elif screen.name == 'run_left_door':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['running']
                running_location = 'start_left_door'
                animation_frame = 0
        elif screen.name == 'run_right_door':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['running']
                running_location = 'start_right_door'
                animation_frame = 0
        elif screen.name == 'running':
            afk_seconds = 0
            seconds_looking_at_bed = 0
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens[running_location]
                animation_frame = 0
                if (running_location == 'start_left_door' and foxy.location == 'right_hall' or
                        running_location == 'start_right_door' and foxy.location == 'left_hall'):
                    foxy.location = 'running_to_closet'
                    foxy.progress = random.randint(3, 7)
                elif running_location == 'start_room':
                    if foxy.location == 'running_to_closet':
                        screen = images.screens['closet_creak']
                        foxy.location = 'closet'
                    if foxy.room_jumpscare:
                        screen = images.screens['jumpscare_foxy_room']
                        animation_frame = 0
        elif screen.name == 'start_left_door':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['left_door']
                animation_frame = 0
        elif screen.name == 'start_right_door':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['right_door']
                animation_frame = 0
        elif screen.name == 'left_door':
            # in order of priority in the game
            if door_status == 'closing':
                if animation_frame <= screen.frames - 1:
                    animation_frame += 0.5
                else:
                    door_status = 'closed'
                    door_shut = 'left'
                    if bonnie.location == 'hall_far':
                        bonnie.location = 'hall_near'
                        # bringing them closer by closing the door cancels bonnie and chica until opened again
                        ai.Animatronic.cancel_movement = True
                        bonnie.will_move = False
            elif door_status == 'opening':
                if animation_frame > 2:
                    animation_frame -= 0.5
                else:
                    door_status = 'open'
            elif keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                if door_status == 'open':
                    # frames 2 and above are closing door
                    animation_frame = 2
                    door_status = 'closing'
            elif door_status == 'closed':
                door_status = 'opening'
                door_shut = ''
                ai.Animatronic.cancel_movement = False
            elif keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                animation_frame = 1
                viewing_hall = 'left'
                if bonnie.location == 'hall_far':
                    bonnie.location = 'mid'
                    retreating = 'bonnie'
                    retreat_frame = 0
                elif bonnie.location == 'hall_near':
                    screen = images.screens['jumpscare_bonnie_hall']
                    animation_frame = 0
                elif foxy.location == 'left_hall':
                    foxy.location = 'mid'
                    if retreating == '':
                        retreating = 'foxy_left'
                        retreat_frame = 0
            elif run_back_rect.collidepoint(pygame.mouse.get_pos()) and retreating == '':
                screen = images.screens['leave_left_door']
                animation_frame = 0
            else:
                # closing door animation does not count as listening
                listening = 'left'
                animation_frame = 0
        elif screen.name == 'right_door':
            # in order of priority in the game
            if door_status == 'closing':
                if animation_frame <= screen.frames - 1:
                    animation_frame += 0.5
                else:
                    door_status = 'closed'
                    door_shut = 'right'
                    if chica.location == 'hall_far':
                        chica.location = 'hall_near'
                        # bringing them closer by closing the door cancels bonnie and chica until opened again
                        ai.Animatronic.cancel_movement = True
                        chica.will_move = False
            elif door_status == 'opening':
                if animation_frame > 2:
                    animation_frame -= 0.5
                else:
                    door_status = 'open'
            elif keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                if door_status == 'open':
                    # frames 2 and above are closing door
                    animation_frame = 2
                    door_status = 'closing'
            elif door_status == 'closed':
                door_status = 'opening'
                door_shut = ''
                ai.Animatronic.cancel_movement = False
            elif keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                animation_frame = 1
                viewing_hall = 'right'
                if chica.location == 'hall_far':
                    chica.location = 'mid'
                    retreating = 'chica'
                    retreat_frame = 0
                elif chica.location == 'hall_near':
                    screen = images.screens['jumpscare_chica_hall']
                    animation_frame = 0
                # for some reason foxy retreats after chica unlike with bonnie
                elif foxy.location == 'right_hall' and retreating == '':
                    foxy.location = 'mid'
                    retreating = 'foxy_right'
                    retreat_frame = 9
            elif run_back_rect.collidepoint(pygame.mouse.get_pos()) and retreating == '':
                screen = images.screens['leave_right_door']
                animation_frame = 0
            else:
                # closing door animation does not count as listening
                listening = 'right'
                animation_frame = 0
        elif screen.name == 'leave_left_door' or screen.name == 'leave_right_door' or screen.name == 'leave_closet':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['running']
                running_location = 'start_room'
                animation_frame = 0
        elif screen.name == 'start_room':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['room']
                animation_frame = 4
                screen.x = -240
        elif screen.jumpscare:
            game_over = True
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                running = False
        elif screen.name == 'run_bed':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['start_bed']
                animation_frame = 0
        elif screen.name == 'start_bed':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['bed']
                animation_frame = 19
        elif screen.name == 'bed':
            if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                if freddy.progress >= 60:
                    screen = images.screens['jumpscare_freddy_bed']
                    animation_frame = 0
                elif 30 <= freddy.progress < 60:
                    if viewing_bed:
                        if animation_frame <= 4:
                            animation_frame += 0.5
                        else:
                            animation_frame = 0
                    else:
                        # set to first frame only if the flashlight was just turned on
                        animation_frame = 0
                elif 20 <= freddy.progress < 30:
                    if viewing_bed:
                        if animation_frame <= 9:
                            animation_frame += 0.5
                        else:
                            animation_frame = 5
                    else:
                        animation_frame = 6
                elif 10 <= freddy.progress < 20:
                    if viewing_bed:
                        if animation_frame <= 14:
                            animation_frame += 0.5
                        else:
                            animation_frame = 10
                    else:
                        animation_frame = 10
                else:
                    if random_bed_view == 1:
                        animation_frame = 16
                    elif random_bed_view == 2:
                        animation_frame = 17
                    elif random_bed_view == 3:
                        animation_frame = 18
                    else:
                        animation_frame = 15
                viewing_bed = True
            else:
                viewing_bed = False
                random_bed_view = random.randint(1, 100)
                animation_frame = 19
                if freddy.bed_jumpscare:
                    screen = images.screens['jumpscare_freddy_bed']
                    animation_frame = 0
            if run_back_rect.collidepoint(pygame.mouse.get_pos()) or ai.Animatronic.force_turn:
                if not run_back_debounce and not viewing_bed or ai.Animatronic.force_turn:
                    screen = images.screens['leave_bed']
                    animation_frame = 0
                    run_back_debounce = True
            elif debounce_rect.collidepoint(pygame.mouse.get_pos()):
                run_back_debounce = False
        elif screen.name == 'leave_bed':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                # priority: chica > bonnie > foxy
                if chica.room_jumpscare:
                    screen = images.screens['jumpscare_chica_room']
                    animation_frame = 0
                elif bonnie.room_jumpscare:
                    screen = images.screens['jumpscare_bonnie_room']
                    animation_frame = 0
                elif foxy.room_jumpscare:
                    screen = images.screens['jumpscare_foxy_room']
                    animation_frame = 0
                else:
                    screen = images.screens['start_room_bed']
                    animation_frame = 0
        elif screen.name == 'start_room_bed':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['room']
                animation_frame = 4
        elif screen.name == 'closet_creak':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['room']
                animation_frame = 4
                screen.x = -240
        elif screen.name == 'run_closet':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['running']
                running_location = 'start_closet'
                animation_frame = 0
        elif screen.name == 'start_closet':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['closet']
                animation_frame = 0
        elif screen.name == 'closet':
            # in order of priority in the game
            if door_status == 'closing':
                if animation_frame <= screen.frames - 1:
                    animation_frame += 0.5
                else:
                    door_status = 'closed'
                    door_shut = 'closet'
            elif door_status == 'opening':
                if animation_frame > 6:
                    animation_frame -= 0.5
                else:
                    door_status = 'open'
            elif keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                if door_status == 'open':
                    # frames 6 and above are closing door
                    animation_frame = 6
                    door_status = 'closing'
            elif door_status == 'closed':
                door_status = 'opening'
                door_shut = ''
            elif keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                viewing_closet = True
                if foxy.location == 'closet':
                    if foxy.progress <= 1:
                        animation_frame = 2
                    elif foxy.progress <= 3:
                        animation_frame = 3
                    elif foxy.progress <= 5:
                        animation_frame = 4
                    elif foxy.progress >= 6:
                        animation_frame = 5
                        if not foxy_bit:
                            screen = images.screens['foxy_bite']
                            animation_frame = 0
                            foxy_bit = True
                else:
                    animation_frame = 1
            elif run_back_rect.collidepoint(pygame.mouse.get_pos()):
                screen = images.screens['leave_closet']
                animation_frame = 0
            else:
                animation_frame = 0
        elif screen.name == 'foxy_bite':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['closet']
                animation_frame = 5
        # freddy can force a jumpscare from anywhere
        if not screen.jumpscare:
            if freddy.room_jumpscare:
                screen = images.screens['jumpscare_freddy_room']
                animation_frame = 0

        bonnie.update(screen, night, viewing_bed, animation_frame)
        chica.update(screen, night, viewing_bed, animation_frame)
        freddy.update(screen, night)
        foxy.update(screen, night, seconds_looking_at_bed=seconds_looking_at_bed)

        bonnie.move(viewing_hall)
        chica.move(viewing_hall)
        foxy.move(viewing_hall, viewing_closet)

        # we increment frames by 0.5 to get that 30 fps animation FNaF 4 seems to have, so floor all the frame values
        if disable_jumpscares and screen.jumpscare:
            # black screen and say who you were killed by
            window.fill((0, 0, 0))
            draw_text(f'Jumpscare: {screen.name}', 380, 3)
            running = False
        else:
            window.blit(screen.images[math.floor(animation_frame)], (screen.x, screen.y))
            # retreating animations are played above everything else because their frames are independent
            if retreating == 'bonnie':
                window.blit(images.screens['retreating_bonnie'].images[math.floor(retreat_frame)], (0, 0))
            elif retreating == 'chica':
                window.blit(images.screens['retreating_chica'].images[math.floor(retreat_frame)], (0, 0))
            elif retreating != '' and viewing_bed:
                window.blit(images.screens['retreating_freddles'].images[math.floor(retreat_frame)], (0, 0))
            elif retreating == 'foxy_left' or retreating == 'foxy_right':
                window.blit(images.screens['retreating_foxy'].images[math.floor(retreat_frame)], (0, 0))

        if retreating == 'bonnie':
            if retreat_frame <= images.screens['retreating_bonnie'].frames - 1:
                retreat_frame += 0.5
            else:
                retreating = ''
        elif retreating == 'chica':
            if retreat_frame <= images.screens['retreating_chica'].frames - 1:
                retreat_frame += 0.5
            else:
                retreating = ''
        elif retreating == 'foxy_left':
            if retreat_frame <= 8:
                retreat_frame += 0.5
            else:
                retreating = ''
        elif retreating == 'foxy_right':
            if retreat_frame <= 8:
                retreat_frame = 9
            elif retreat_frame <= images.screens['retreating_foxy'].frames - 1:
                retreat_frame += 0.5
            else:
                retreating = ''
        else:
            if retreating == 'freddle_3':
                if retreat_frame <= 4:
                    retreat_frame += 0.5
                else:
                    retreating = ''
            elif retreating == 'freddle_2':
                if retreat_frame <= 9:
                    retreat_frame += 0.5
                else:
                    retreating = ''
            elif retreating == 'freddle_1':
                if retreat_frame <= 14:
                    retreat_frame += 0.5
                else:
                    retreating = ''

        # time
        if hour == 0:
            window.blit(hour_number.images[0], (hour_number.x, hour_number.y))
            window.blit(hour_number.images[1], (hour_number.x + num_width, hour_number.y))
        else:
            window.blit(hour_number.images[hour - 1], (hour_number.x + num_width, hour_number.y))
        window.blit(hour_number.images[hour_number.frames - 1], (958, 32))

        if enable_debug_text:
            draw_text(f'Night: {night}', 0, 0)
            draw_text(f'Bonnie location: {bonnie.location}', 0, 1)
            draw_text(f'Chica location: {chica.location}', 0, 2)
            draw_text(f'Foxy location: {foxy.location}', 0, 3)
            pending_jumpscares = []
            if chica.seconds_at_door > 20 - night:
                pending_jumpscares.append('chica room')
            if chica.location == 'hall_near':
                pending_jumpscares.append('chica hall')
            if bonnie.seconds_at_door > 20 - night:
                pending_jumpscares.append('bonnie room')
            if bonnie.location == 'hall_near':
                pending_jumpscares.append('bonnie hall')
            if freddy.progress >= 60:
                pending_jumpscares.append('freddy bed')
            if freddy.progress >= 80:
                pending_jumpscares.append('freddy room')
            if foxy.room_jumpscare:
                pending_jumpscares.append('foxy room')
            pending_jumpscares_text = ', '.join(pending_jumpscares)
            draw_text(f'Pending jumpscares: {pending_jumpscares_text}', 0, 4)
            draw_text(f'Bonnie AI: {bonnie.ai}', 0, 5)
            draw_text(f'Chica AI: {chica.ai}', 0, 6)
            draw_text(f'Freddy AI: {freddy.ai}', 0, 7)
            draw_text(f'Foxy AI: {foxy.ai}', 0, 8)
            draw_text(f'Freddy progress: {freddy.progress}', 0, 9)
            draw_text(f'Foxy progress: {foxy.progress}', 0, 10)
            if enable_advanced_debug_text:
                draw_text(f'Screen: {screen.name}', 0, 11)
                draw_text(f'Frame: {math.floor(animation_frame)}', 0, 12)
                draw_text(f'{round(clock.get_fps())} FPS', 0, 13)
                draw_text(f'Seconds without running: {afk_seconds}', 0, 14)
                draw_text(f'Freddy countdown: {freddy.countdown}', 0, 15)
                draw_text(f'Door shut: {door_shut}', 0, 16)
                draw_text(f'Seconds looking at bed: {seconds_looking_at_bed}', 0, 17)
            if draw_hitboxes:
                hitbox_surface = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
                hitbox_surface.set_alpha(hitbox_alpha)
                pygame.draw.rect(hitbox_surface, (255, 0, 255), slow_left_rect)
                pygame.draw.rect(hitbox_surface, (100, 50, 255), fast_left_rect)
                pygame.draw.rect(hitbox_surface, (255, 0, 255), slow_right_rect)
                pygame.draw.rect(hitbox_surface, (100, 50, 255), fast_right_rect)
                pygame.draw.rect(hitbox_surface, (255, 0, 0), left_door_rect)
                pygame.draw.rect(hitbox_surface, (255, 0, 0), right_door_rect)
                pygame.draw.rect(hitbox_surface, (255, 0, 0), run_back_rect)
                pygame.draw.rect(hitbox_surface, (255, 0, 0), debounce_rect)
                pygame.draw.rect(hitbox_surface, (255, 0, 0), closet_rect)
                window.blit(hitbox_surface, (0, 0))

        pygame.display.flip()
        dt = clock.tick(60)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
            elif event.type == pygame.QUIT:
                pygame.quit()
