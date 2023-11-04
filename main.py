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
        freddy.ai = 0
    elif night == 2:
        bonnie.ai = 5
        chica.ai = 5
        freddy.ai = 2
    elif night == 3:
        bonnie.ai = 7
        chica.ai = 7
        freddy.ai = 3
    elif night == 4:
        bonnie.ai = 10
        chica.ai = 10
        freddy.ai = 4


def mouse_delta_x():
    # very close estimates
    mouse_x = pygame.mouse.get_pos()[0] + 1  # add 1 so the math works out (max 1024 instead of 1023)
    if mouse_x > 4 / 5 * SCREEN_X:
        return -12
    elif mouse_x > 2 / 3 * SCREEN_X:
        return -6
    elif mouse_x < 1 / 5 * SCREEN_X:
        return 12
    elif mouse_x < 1 / 3 * SCREEN_X:
        return 6
    return 0


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
    freddy = ai.Animatronic('freddy', progress=0)

    if override_ai:
        bonnie.ai = config['bonnie_ai']
        chica.ai = config['chica_ai']
        freddy.ai = config['freddy_ai']
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
    random_bed_view = random.randint(1, 100)

    twentieth_second_event = pygame.USEREVENT + 3
    fifth_second_event = pygame.USEREVENT + 4

    run_back_debounce = False
    game_over = False
    jumpscared_by = ''
    cleared = False

    pygame.time.set_timer(hour_event, 60000)
    pygame.time.set_timer(second_event, 1000)
    pygame.time.set_timer(twentieth_second_event, 50)
    pygame.time.set_timer(fifth_second_event, 200)
    second_intervals = 0
    afk_seconds = 0

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
                chica.interval_update(second_intervals, screen, door_shut, listening)
                bonnie.interval_update(second_intervals, screen, door_shut, listening)
                freddy.interval_update(second_intervals, screen, viewing_bed=viewing_bed)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if screen.name == 'room' and event.button == 1:
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
                    elif night == 3:
                        if hour == 3:
                            bonnie.ai += 3
                            chica.ai += 3
                    elif night == 4:
                        if hour == 3:
                            bonnie.ai += 2
                            chica.ai += 2
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
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
            elif event.type == pygame.QUIT:
                pygame.quit()

        if hour == 6:
            running = False

        listening = ''
        viewing_hall = ''

        # simple animation cycles depending on which screen is selected
        # if the frame is the last, go back to the first frame
        # also initialize frame number when switching screens
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
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens[running_location]
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
            else:
                run_back_debounce = False
        elif screen.name == 'leave_bed':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                # priority: chica > bonnie
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
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['room']
                animation_frame = 4
        if not screen.jumpscare:
            if freddy.room_jumpscare:
                screen = images.screens['jumpscare_freddy_room']
                animation_frame = 0

        bonnie.update(screen, night, viewing_bed, animation_frame)
        chica.update(screen, night, viewing_bed, animation_frame)
        freddy.update(screen, night)

        bonnie.move(viewing_hall)
        chica.move(viewing_hall)

        # we increment frames by 0.5 to get that 30 fps animation FNaF 4 seems to have, so floor all the frame values
        if disable_jumpscares and screen.jumpscare:
            # black screen and say who you were killed by
            window.fill((0, 0, 0))
            draw_text(f'Jumpscare: {screen.name}', 380, 3)
            running = False
        else:
            window.blit(screen.images[math.floor(animation_frame)], (screen.x, screen.y))
            # retreating animations are played above everything else because their frames are independent
            if retreating == 'bonnie' and viewing_hall == 'left':
                window.blit(images.screens['retreating_bonnie'].images[math.floor(retreat_frame)], (0, 0))
            elif retreating == 'chica' and viewing_hall == 'right':
                window.blit(images.screens['retreating_chica'].images[math.floor(retreat_frame)], (0, 0))
            elif retreating != '' and viewing_bed:
                window.blit(images.screens['retreating_freddles'].images[math.floor(retreat_frame)], (0, 0))

        if retreating == '':
            retreat_frame = 0
        elif retreating == 'bonnie' or retreating == 'chica':
            if retreat_frame <= 15:
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
            pending_jumpscares_text = ', '.join(pending_jumpscares)
            draw_text(f'Pending jumpscares: {pending_jumpscares_text}', 0, 3)
            draw_text(f'Bonnie AI: {bonnie.ai}', 0, 4)
            draw_text(f'Chica AI: {chica.ai}', 0, 5)
            draw_text(f'Freddy AI: {freddy.ai}', 0, 6)
            draw_text(f'Freddy progress: {freddy.progress}', 0, 7)
            draw_text(f'Screen: {screen.name}', 0, 8)
            draw_text(f'Frame: {math.floor(animation_frame)}', 0, 9)
            draw_text(f'{round(clock.get_fps())} FPS', 0, 10)
            draw_text(f'Seconds without running: {afk_seconds}', 0, 11)
            draw_text(f'Freddy countdown: {freddy.countdown}', 0, 12)
            draw_text(f'Door status: {door_status}', 0, 13)

        pygame.display.flip()
        dt = clock.tick(60)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
            elif event.type == pygame.QUIT:
                pygame.quit()
