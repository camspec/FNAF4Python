import images
import math
import pygame
import random


# FNaF 4 Remake by me
# All images, audio, and characters used in this project are owned by Scott Cawthon.


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
    hour = 0
    hour_event = pygame.USEREVENT + 1
    hour_number = images.screens['hour']
    num_width = hour_number.images[0].get_width()

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

    bonnie_ai = 20
    chica_ai = 20
    bonnie_location = 'mid'
    chica_location = 'mid'
    bonnie_random = 0
    chica_random = 0
    second_event = pygame.USEREVENT + 2
    listening = ''
    left_door_shut = False
    right_door_shut = False
    retreating = ''
    bonnie_move = False
    chica_move = False
    bonnie_seconds_at_door = 0
    chica_seconds_at_door = 0
    bonnie_force_move = False
    chica_force_move = False
    run_back_debounce = False
    cancel_movement = False
    viewing_left_hall = False
    viewing_right_hall = False
    game_over = False
    cleared = False
    night = 1
    room_jumpscare = ''

    pygame.time.set_timer(hour_event, 60000)
    pygame.time.set_timer(second_event, 1000)
    second_intervals = 0

    bonnie_force_move_hour = random.randint(2, 5)
    chica_force_move_hour = random.randint(3, 5)

    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == second_event:
                second_intervals += 1
                if second_intervals % 5 == 0 and not cancel_movement:
                    if random.randint(1, 20) <= bonnie_ai and not left_door_shut and listening != 'left':
                        bonnie_move = True
                    if random.randint(1, 20) <= chica_ai and not right_door_shut and listening != 'right':
                        chica_move = True
                if second_intervals % 10 == 0:
                    if bonnie_move:
                        if bonnie_location == 'left_hall_near' and listening != 'left':
                            bonnie_location = 'left_hall_far'
                            bonnie_move = False
                    if chica_move:
                        if chica_location == 'right_hall_near' and listening != 'right':
                            chica_location = 'right_hall_far'
                            chica_move = False
                # clearing cannot occur if movement is cancelled (you just brought them to near hall)
                if second_intervals % 3 == 0 and not cancel_movement:
                    if bonnie_location == 'left_hall_near' and left_door_shut:
                        bonnie_location = 'left'
                        # clearing will cancel bonnie and chica until door opened again
                        cancel_movement = True
                        bonnie_move = False
                    if chica_location == 'right_hall_near' and right_door_shut:
                        chica_location = 'right'
                        # clearing will cancel bonnie and chica until door opened again
                        cancel_movement = True
                        chica_move = False
                if bonnie_location == 'left_hall_near':
                    bonnie_seconds_at_door += 1
                if chica_location == 'right_hall_near':
                    chica_seconds_at_door += 1
                bonnie_random = random.randint(1, 2)
                chica_random = random.randint(1, 2)

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
                if night == 1:
                    if hour == 2:
                        bonnie_ai += 1
                        chica_ai += 1
                    elif hour == 3:
                        bonnie_ai += 2
                        chica_ai += 1
                elif night == 2:
                    if hour == 3:
                        bonnie_ai += 2
                        chica_ai += 2
                elif night == 3:
                    if hour == 3:
                        bonnie_ai += 3
                        chica_ai += 3
                elif night == 4:
                    if hour == 3:
                        bonnie_ai += 2
                        chica_ai += 2
                elif night == 6:
                    if hour == 4:
                        bonnie_ai -= 12
                        chica_ai -= 12
                if 2 <= night <= 4:
                    if hour == bonnie_force_move_hour:
                        bonnie_force_move = True
                    if hour == chica_force_move_hour:
                        chica_force_move = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_j:
                    pygame.event.post(pygame.event.Event(hour_event))

            elif event.type == pygame.QUIT:
                running = False

        if hour == 6:
            print('Game is over')
            running = False

        listening = ''
        viewing_left_hall = False
        viewing_right_hall = False

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
            # update these screens since they are wide
            images.screens['run_left_door'].x = screen.x
            images.screens['run_right_door'].x = screen.x
            images.screens['run_bed'].x = screen.x
            images.screens['start_room_bed'].x = screen.x
            # start room doesn't need since it's always in the same spot

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
                    left_door_shut = True
                    if bonnie_location == 'left_hall_far':
                        bonnie_location = 'left_hall_near'
                        # bringing them closer by closing the door cancels bonnie and chica until opened again
                        cancel_movement = True
                        bonnie_move = False
            elif animation_frame > 2:
                left_door_shut = False
                cancel_movement = False
                animation_frame -= 0.5
            elif keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                animation_frame = 1
                viewing_left_hall = True
                if bonnie_location == 'left_hall_far':
                    bonnie_location = 'mid'
                    retreating = 'bonnie'
                elif bonnie_location == 'left_hall_near':
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
                    right_door_shut = True
                    if chica_location == 'right_hall_far':
                        chica_location = 'right_hall_near'
                        # bringing them closer by closing the door cancels bonnie and chica until opened again
                        cancel_movement = True
                        chica_move = False
            elif animation_frame > 2:
                right_door_shut = False
                cancel_movement = False
                animation_frame -= 0.5
            elif keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                animation_frame = 1
                viewing_right_hall = True
                if chica_location == 'right_hall_far':
                    chica_location = 'mid'
                    retreating = 'chica'
                elif chica_location == 'right_hall_near':
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
            if run_back_rect.collidepoint(pygame.mouse.get_pos()):
                if not run_back_debounce:
                    screen = images.screens['leave_bed']
                    animation_frame = 0
                    run_back_debounce = True
            else:
                run_back_debounce = False
        elif screen.name == 'leave_bed':
            if animation_frame < screen.frames - 1:
                animation_frame += 0.5
            else:
                if room_jumpscare == 'bonnie':
                    screen = images.screens['jumpscare_bonnie_room']
                    animation_frame = 0
                elif room_jumpscare == 'chica':
                    screen = images.screens['jumpscare_chica_room']
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

        if bonnie_location != 'left_hall_far' and bonnie_location != 'left_hall_near':
            bonnie_seconds_at_door = 0
        if bonnie_seconds_at_door > 20 - night:
            room_jumpscare = 'bonnie'

        if bonnie_move:
            if bonnie_location == 'mid':
                bonnie_location = 'left'
                bonnie_move = False
            elif bonnie_location == 'left':
                if bonnie_random == 1:
                    # if bonnie's waiting to move into left hall but flashlight is on, he will move right when it's off
                    if not viewing_left_hall:
                        bonnie_location = 'left_hall_far'
                        bonnie_move = False
                else:
                    bonnie_location = 'mid'
                    bonnie_move = False
            elif bonnie_location == 'left_hall_far':
                bonnie_location = 'left_hall_near'
                bonnie_move = False
            
        if chica_location != 'right_hall_far' and chica_location != 'right_hall_near':
            chica_seconds_at_door = 0
        if chica_seconds_at_door > 20 - night:
            room_jumpscare = 'chica'
            
        if chica_move:
            if chica_location == 'mid' or chica_location == 'kitchen':
                chica_location = 'right'
                chica_move = False
            elif chica_location == 'right':
                if chica_random == 1:
                    # if chica's waiting to move into right hall but flashlight is on, she will move right when it's off
                    if not viewing_right_hall:
                        chica_location = 'right_hall_far'
                        chica_move = False
                else:
                    chica_location = 'kitchen'
                    chica_move = False
            elif chica_location == 'right_hall_far':
                chica_location = 'right_hall_near'
                chica_move = False

        # force move
        if bonnie_force_move and screen.name == 'room':
            bonnie_location = 'left_hall_near'
            bonnie_force_move = False
        if chica_force_move and screen.name == 'room':
            chica_location = 'right_hall_near'
            chica_force_move = False

        # we increment frames by 0.5 to get that 30 fps animation FNaF 4 seems to have, so floor all the frame values
        window.blit(screen.images[math.floor(animation_frame)], (screen.x, screen.y))
        if retreating == 'bonnie' and viewing_left_hall:
            window.blit(images.screens['retreating_bonnie'].images[math.floor(retreat_frame)], (0, 0))
        elif retreating == 'chica' and viewing_right_hall:
            window.blit(images.screens['retreating_chica'].images[math.floor(retreat_frame)], (0, 0))
        # time
        if hour == 0:
            window.blit(hour_number.images[0], (hour_number.x, hour_number.y))
            window.blit(hour_number.images[1], (hour_number.x + num_width, hour_number.y))
        else:
            window.blit(hour_number.images[hour - 1], (hour_number.x + num_width, hour_number.y))
        window.blit(hour_number.images[hour_number.frames - 1], (958, 32))
        print(f'Bonnie location: {bonnie_location}')
        print(f'Chica location: {chica_location}')
        print(f'Room jumpscare: {room_jumpscare}')
        pygame.display.flip()
        dt = clock.tick(60)
    pygame.quit()
