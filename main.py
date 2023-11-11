import json
import math
import random

import pygame

import ai
import audio
import images
from box import hitboxes


# FNaF 4 Remake by camspec
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
    # when looking left, we move screen to right and vice versa
    if hitboxes['slow_left'].rect.collidepoint(pygame.mouse.get_pos()):
        screen.x += 6
    if hitboxes['fast_left'].rect.collidepoint(pygame.mouse.get_pos()):
        screen.x += 6
    if hitboxes['slow_right'].rect.collidepoint(pygame.mouse.get_pos()):
        screen.x -= 6
    if hitboxes['fast_right'].rect.collidepoint(pygame.mouse.get_pos()):
        screen.x -= 6


def draw_text(string, x, row):
    window.blit(font.render(string, True, (255, 255, 255)), (x, row * 16))


if __name__ == '__main__':
    pygame.display.init()
    SCREEN_X = 1024
    SCREEN_Y = 768
    SCREEN_SIZE = (SCREEN_X, SCREEN_Y)
    window = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Five Nights at Freddy\'s 4')
    icon = pygame.image.load('assets/icon/favicon.png').convert()
    pygame.display.set_icon(icon)

    running = True
    clock = pygame.time.Clock()
    pygame.font.init()
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
    animation_frame = 0
    retreat_frame = 0

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

    listening = ''
    door_shut = ''
    door_status = 'open'
    retreating = ''
    running_location = ''
    viewing_hall = ''
    viewing_bed = False
    viewing_closet = False
    random_bed_view = random.randint(1, 100)

    second_event = pygame.USEREVENT + 2
    twentieth_second_event = pygame.USEREVENT + 3
    fifth_second_event = pygame.USEREVENT + 4
    second_intervals = 0
    afk_seconds = 0
    seconds_looking_at_bed = 0

    run_back_debounce = False
    game_over = False
    foxy_bit = False

    pygame.time.set_timer(hour_event, 60000)
    pygame.time.set_timer(second_event, 1000)
    pygame.time.set_timer(twentieth_second_event, 50)
    pygame.time.set_timer(fifth_second_event, 200)

    # these sounds play nonstop at 0 volume, and actually turn on by changing volume
    audio.sounds['ambience'].play()
    audio.sounds['crickets'].play()
    audio.sounds['breathing'].play()
    audio.sounds['freddles'].play()
    audio.sounds['kitchen'].play()
    audio.sounds['random_call'].play()
    random_sound = 0
    random_call = 0

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
                if second_intervals == 4:
                    audio.sounds['clock_chime'].play()
                if second_intervals % 10 == 0:
                    random_sound = random.randint(1, 30)
                if second_intervals % 2 == 0:
                    if night == 1:
                        random_call = random.randint(1, 40)
                    else:
                        random_call = random.randint(1, 200)
                chica.interval_update(second_intervals, door_shut, listening)
                bonnie.interval_update(second_intervals, door_shut, listening)
                freddy.interval_update(second_intervals, viewing_bed=viewing_bed, screen=screen)
                foxy.interval_update(second_intervals, door_shut)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if screen.name == 'room':
                    if hitboxes['left_door'].rect.collidepoint(pygame.mouse.get_pos()) and animation_frame == 0:
                        audio.sounds['flashlight'].play()
                        screen = images.screens['run_left_door']
                        animation_frame = 0
                    elif (hitboxes['right_door'].rect.collidepoint(pygame.mouse.get_pos()) and
                          animation_frame == screen.frames - 1):
                        audio.sounds['flashlight'].play()
                        screen = images.screens['run_right_door']
                        animation_frame = 0
                    elif hitboxes['closet'].rect.collidepoint(pygame.mouse.get_pos()) and animation_frame == 4:
                        screen = images.screens['run_closet']
                        animation_frame = 0
                if viewing_bed and hitboxes['honk'].rect.collidepoint(pygame.mouse.get_pos()):
                    audio.sounds['honk'].play()
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
                    elif event.key == pygame.K_p:
                        chica.location = 'kitchen'
                    elif event.key == pygame.K_j:
                        foxy.progress += 1
                    elif event.key == pygame.K_s:
                        random_sound = random.randint(1, 3)
                    elif event.key == pygame.K_r:
                        random_call = random.randint(1, 2)
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.QUIT:
                running = False

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
                else:
                    audio.sounds['crickets'].update_volume(25)
                    audio.sounds['clock_chime'].update_volume(25)
                    audio.sounds['foxy_run_left'].update_volume(20)
                    audio.sounds['foxy_run_right'].update_volume(20)
            # update these screens since they are wide (after clamp)
            # start room and closet creak don't need to update since they're always in the same spot
            images.screens['run_left_door'].x = screen.x
            images.screens['run_right_door'].x = screen.x
            images.screens['run_bed'].x = screen.x
            images.screens['start_room_bed'].x = screen.x
            images.screens['run_closet'].x = screen.x
            hitboxes['left_door'].rect.x = screen.x + 18
            hitboxes['right_door'].rect.x = screen.x + 1020
            hitboxes['closet'].rect.x = screen.x + 576
            if animation_frame > screen.frames - 1:  # right side clamp animation
                animation_frame = screen.frames - 1
            elif animation_frame < 0:  # left side clamp animation
                animation_frame = 0
            if hitboxes['run_back'].rect.collidepoint(pygame.mouse.get_pos()):
                if not run_back_debounce:
                    screen = images.screens['run_bed']
                    run_back_debounce = True
                    animation_frame = 0
        elif screen.name == 'run_left_door':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                audio.sounds['crickets'].update_volume(15)
                audio.sounds['clock_chime'].update_volume(30)
                audio.sounds['foxy_run_left'].update_volume(25)
                audio.sounds['foxy_run_right'].update_volume(15)
                screen = images.screens['running']
                running_location = 'start_left_door'
                animation_frame = 0
        elif screen.name == 'run_right_door':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                audio.sounds['crickets'].update_volume(30)
                audio.sounds['clock_chime'].update_volume(15)
                audio.sounds['foxy_run_left'].update_volume(15)
                audio.sounds['foxy_run_right'].update_volume(25)
                screen = images.screens['running']
                running_location = 'start_right_door'
                animation_frame = 0
        elif screen.name == 'running':
            if animation_frame == 0:
                audio.sounds['carpet_run'].play()
            afk_seconds = 0
            seconds_looking_at_bed = 0
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens[running_location]
                animation_frame = 0
                if running_location == 'start_left_door':
                    audio.sounds[f'door_creak{random.randint(1, 4)}'].play()
                    audio.sounds['crickets'].update_volume(10)
                    audio.sounds['clock_chime'].update_volume(50)
                    audio.sounds['foxy_run_left'].update_volume(40)
                    audio.sounds['foxy_run_right'].update_volume(10)
                elif running_location == 'start_right_door':
                    audio.sounds[f'door_creak{random.randint(1, 4)}'].play()
                    audio.sounds['crickets'].update_volume(50)
                    audio.sounds['clock_chime'].update_volume(10)
                    audio.sounds['foxy_run_left'].update_volume(10)
                    audio.sounds['foxy_run_right'].update_volume(40)
                if running_location == 'start_left_door' and foxy.location == 'right_hall':
                    audio.sounds['foxy_enter_right'].play()
                    foxy.location = 'running_to_closet'
                    foxy.progress = random.randint(3, 7)
                elif running_location == 'start_right_door' and foxy.location == 'left_hall':
                    audio.sounds['foxy_enter_left'].play()
                    foxy.location = 'running_to_closet'
                    foxy.progress = random.randint(3, 7)
                elif running_location == 'start_room':
                    if foxy.location == 'running_to_closet':
                        audio.sounds['closet_creak'].play()
                        screen = images.screens['closet_creak']
                        foxy.location = 'closet'
                    if foxy.room_jumpscare:
                        screen = images.screens['jumpscare_foxy_room']
                        animation_frame = 0
                    else:
                        audio.sounds['flashlight'].play()
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
                    audio.sounds['door_creak1'].play()
                    # frames 2 and above are closing door
                    animation_frame = 2
                    door_status = 'closing'
            elif door_status == 'closed':
                audio.sounds[f'door_creak{random.randint(1, 4)}'].play()
                door_status = 'opening'
                door_shut = ''
                ai.Animatronic.cancel_movement = False
            elif keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                # if flashlight sound hasn't played yet
                if animation_frame == 0:
                    audio.sounds['flashlight'].play()
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
            elif hitboxes['run_back'].rect.collidepoint(pygame.mouse.get_pos()) and retreating == '':
                if animation_frame == 1:
                    audio.sounds['flashlight'].play()
                screen = images.screens['leave_left_door']
                animation_frame = 0
            else:
                if animation_frame == 1:
                    audio.sounds['flashlight'].play()
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
                    audio.sounds['door_creak1'].play()
                    # frames 2 and above are closing door
                    animation_frame = 2
                    door_status = 'closing'
            elif door_status == 'closed':
                audio.sounds[f'door_creak{random.randint(1, 4)}'].play()
                door_status = 'opening'
                door_shut = ''
                ai.Animatronic.cancel_movement = False
            elif keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                if animation_frame == 0:
                    audio.sounds['flashlight'].play()
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
            elif hitboxes['run_back'].rect.collidepoint(pygame.mouse.get_pos()) and retreating == '':
                if animation_frame == 1:
                    audio.sounds['flashlight'].play()
                screen = images.screens['leave_right_door']
                animation_frame = 0
            else:
                if animation_frame == 1:
                    audio.sounds['flashlight'].play()
                # closing door animation does not count as listening
                listening = 'right'
                animation_frame = 0
        elif screen.name == 'leave_left_door' or screen.name == 'leave_right_door' or screen.name == 'leave_closet':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                if screen.name == 'leave_left_door':
                    audio.sounds['crickets'].update_volume(15)
                    audio.sounds['clock_chime'].update_volume(30)
                    audio.sounds['foxy_run_left'].update_volume(25)
                    audio.sounds['foxy_run_right'].update_volume(15)
                elif screen.name == 'leave_right_door':
                    audio.sounds['crickets'].update_volume(30)
                    audio.sounds['clock_chime'].update_volume(15)
                    audio.sounds['foxy_run_left'].update_volume(15)
                    audio.sounds['foxy_run_right'].update_volume(25)
                screen = images.screens['running']
                running_location = 'start_room'
                animation_frame = 0
        elif screen.name == 'start_room':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                screen = images.screens['room']
                animation_frame = 4
                screen.x = -238
        elif screen.jumpscare:
            if animation_frame == 0 and not disable_jumpscares:
                audio.Sound.main_volume = 100
                audio.sounds['scream1'].play()
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
                if animation_frame == 19:
                    audio.sounds['flashlight'].play()
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
                if animation_frame != 19:
                    audio.sounds['flashlight'].play()
                viewing_bed = False
                random_bed_view = random.randint(1, 100)
                animation_frame = 19
                if freddy.bed_jumpscare:
                    screen = images.screens['jumpscare_freddy_bed']
                    animation_frame = 0
            if hitboxes['run_back'].rect.collidepoint(pygame.mouse.get_pos()) or ai.Animatronic.force_turn:
                if not run_back_debounce and not viewing_bed or ai.Animatronic.force_turn:
                    screen = images.screens['leave_bed']
                    animation_frame = 0
                    run_back_debounce = True
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
                screen.x = -238
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
                    audio.sounds[f'closet_close{random.randint(1, 3)}'].play()
                    # frames 6 and above are closing door
                    animation_frame = 6
                    door_status = 'closing'
            elif door_status == 'closed':
                audio.sounds[f'closet_close{random.randint(1, 3)}'].play()
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
                            audio.Sound.main_volume = 100
                            audio.sounds['scream_closet'].play()
                            screen = images.screens['foxy_bite']
                            animation_frame = 0
                            foxy_bit = True
                else:
                    animation_frame = 1
            elif hitboxes['run_back'].rect.collidepoint(pygame.mouse.get_pos()):
                if animation_frame == 1:
                    audio.sounds['flashlight'].play()
                screen = images.screens['leave_closet']
                animation_frame = 0
            else:
                if animation_frame == 1:
                    audio.sounds['flashlight'].play()
                animation_frame = 0
        elif screen.name == 'foxy_bite':
            if animation_frame <= screen.frames - 1:
                animation_frame += 0.5
            else:
                audio.Sound.main_volume = 20
                screen = images.screens['closet']
                animation_frame = 5
        if screen.jumpscare:
            game_over = True
        else:
            # freddy can force a jumpscare from anywhere
            if freddy.room_jumpscare:
                screen = images.screens['jumpscare_freddy_room']
                animation_frame = 0
                game_over = True

        if hitboxes['debounce'].rect.collidepoint(pygame.mouse.get_pos()):
            run_back_debounce = False

        bonnie.update(screen, night, viewing_bed, animation_frame)
        chica.update(screen, night, viewing_bed, animation_frame)
        freddy.update(screen, night)
        foxy.update(screen, night, seconds_looking_at_bed=seconds_looking_at_bed)

        bonnie.move(viewing_hall)
        chica.move(viewing_hall)
        foxy.move(viewing_hall, viewing_closet)

        if (listening == 'left' and bonnie.location == 'hall_near' or
                listening == 'right' and chica.location == 'hall_near'):
            audio.sounds['breathing'].update_volume(100)
        else:
            audio.sounds['breathing'].update_volume(0)
        if viewing_bed and freddy.progress >= 10:
            audio.sounds['freddles'].update_volume(50)
        elif freddy.progress >= 30:
            audio.sounds['freddles'].update_volume(2)
        elif freddy.progress >= 20:
            audio.sounds['freddles'].update_volume(1)
        else:
            audio.sounds['freddles'].update_volume(0)
        if chica.location == 'kitchen':
            if listening == 'right':
                audio.sounds['kitchen'].update_volume(100)
            else:
                audio.sounds['kitchen'].update_volume(40)
        else:
            audio.sounds['kitchen'].update_volume(0)
        if random_sound == 1:
            audio.sounds['random_laugh'].play()
        elif random_sound == 2:
            audio.sounds['random_breath'].play()
        elif random_sound == 3:
            audio.sounds['random_dog'].play()
        random_sound = 0
        if random_call == 1:
            audio.sounds['random_call'].update_volume(60)
        elif random_call == 2:
            audio.sounds['random_call'].update_volume(30)
        else:
            audio.sounds['random_call'].update_volume(0)

        window.fill((255, 255, 255))

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
                draw_text(f'Debounce: {run_back_debounce}', 0, 18)
        if draw_hitboxes:
            hitbox_surface = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
            hitbox_surface.set_alpha(hitbox_alpha)
            for h in hitboxes:
                pygame.draw.rect(hitbox_surface, hitboxes[h].colour, hitboxes[h].rect)
            window.blit(hitbox_surface, (0, 0))

        pygame.display.flip()
        dt = clock.tick(60)

    for i in audio.sounds:
        audio.sounds[i].channel.stop()

    while game_over:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_over = False
            elif event.type == pygame.QUIT:
                game_over = False

    pygame.quit()
