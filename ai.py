import random

import pygame

import audio


class Animatronic:
    cancel_movement = False
    force_turn = False

    def __init__(self, name, location='', force_move_hour=0, side=''):
        self.name = name
        self.ai = 0
        self.location = location
        self.force_move_hour = force_move_hour
        self.side = side
        self.progress = 0
        self.random = 0
        self.will_move = False
        self.seconds_at_door = 0
        self.force_move = False
        self.room_jumpscare = False
        self.bed_jumpscare = False
        self.countdown = 0

    def interval_update(self, second_intervals, door_shut='', listening='', viewing_bed=False, screen=None):
        if self.name == 'bonnie' or self.name == 'chica':
            self.random = random.randint(1, 2)
            if second_intervals % 5 == 0 and not Animatronic.cancel_movement:
                if random.randint(1, 20) <= self.ai and door_shut != self.side and listening != self.side:
                    self.will_move = True
            if second_intervals % 10 == 0:
                if self.will_move:
                    if self.location == 'hall_near' and listening != self.side:
                        walk = random.randint(1, 4)
                        if self.name == 'bonnie':
                            audio.sounds[f'close_walk{walk}'].channel = pygame.mixer.Channel(7)
                            audio.sounds[f'close_walk{walk}'].pan = -100
                        else:
                            audio.sounds[f'close_walk{walk}'].channel = pygame.mixer.Channel(8)
                            audio.sounds[f'close_walk{walk}'].pan = 100
                        audio.sounds[f'close_walk{walk}'].play()
                        self.location = 'hall_far'
                        self.will_move = False
            # clearing cannot occur if movement is cancelled (you just brought them to near hall)
            if second_intervals % 3 == 0 and not Animatronic.cancel_movement:
                if self.location == 'hall_near' and door_shut == self.side:
                    self.location = self.side
                    self.will_move = False
                    # clearing will cancel bonnie and chica until door opened again
                    Animatronic.cancel_movement = True
            if self.location == 'hall_near':
                self.seconds_at_door += 1
            if second_intervals % 4 == 0 and self.room_jumpscare:
                Animatronic.force_turn = True
        elif self.name == 'freddy':
            if second_intervals % 3 == 0 and self.progress >= 60 and screen.name == 'bed':
                self.bed_jumpscare = True
            if second_intervals % 4 == 0 and not viewing_bed:
                self.progress += self.ai
        elif self.name == 'foxy':
            self.random = random.randint(1, 10)
            if door_shut == 'closet' and self.location == 'closet':
                self.progress -= 1
            if second_intervals % 5 == 0:
                if random.randint(1, 10) <= self.ai:
                    self.will_move = True

    def update(self, screen, night, viewing_bed=False, animation_frame=0, seconds_looking_at_bed=0):
        if self.name == 'bonnie' or self.name == 'chica':
            # force move
            if self.force_move and screen.name == 'room' and animation_frame == 4:
                self.location = 'hall_near'
                self.force_move = False
            if self.location != 'hall_far' and self.location != 'hall_near':
                self.seconds_at_door = 0
            # determine if we should jumpscare
            if self.seconds_at_door > 20 - night and viewing_bed:
                self.room_jumpscare = True
        elif self.name == 'freddy':
            if self.progress >= 80:
                # 0: countdown hasn't started yet
                if self.countdown == 0:
                    self.countdown = 50 + random.randint(0, 99)
                elif self.countdown > 1:
                    self.countdown -= 1
                elif self.countdown == 1:
                    self.room_jumpscare = True
        elif self.name == 'foxy':
            if self.progress >= 10:
                self.room_jumpscare = True
            if seconds_looking_at_bed >= 15:
                self.room_jumpscare = True
                Animatronic.force_turn = True
            if self.room_jumpscare and screen.name == 'bed':
                Animatronic.force_turn = True

    def move(self, viewing_hall, viewing_closet=False):
        close_walk = False
        far_walk = False
        if self.name == 'bonnie' or self.name == 'chica':
            if self.will_move:
                if self.location == 'mid' or self.location == 'kitchen':
                    far_walk = True
                    self.location = self.side
                    self.will_move = False
                elif self.location == self.side:
                    if self.random == 1:
                        # if they're waiting to move into hall but flashlight is on,
                        # they will move right when it's off
                        if viewing_hall != self.side:
                            close_walk = True
                            self.location = 'hall_far'
                            self.will_move = False
                    else:
                        far_walk = True
                        if self.name == 'bonnie':
                            self.location = 'mid'
                        else:
                            self.location = 'kitchen'
                        self.will_move = False
                elif self.location == 'hall_far':
                    close_walk = True
                    self.location = 'hall_near'
                    self.will_move = False
        elif self.name == 'foxy':
            if self.will_move:
                foxy_move = random.randint(1, 2)
                if self.location == 'mid':
                    self.will_move = False
                    if self.random <= 5:
                        audio.sounds[f'foxy_left{foxy_move}'].play()
                        self.location = 'left'
                    elif self.random > 5:
                        audio.sounds[f'foxy_right{foxy_move}'].play()
                        self.location = 'right'
                elif self.location == 'left':
                    if self.random <= 9:
                        audio.sounds[f'foxy_right{foxy_move}'].play()
                        self.will_move = False
                        self.location = 'right'
                    elif self.random == 10:
                        if viewing_hall != 'left':
                            audio.sounds['foxy_run_left'].play()
                            # if they're waiting to move into hall but flashlight is on,
                            # they will move right when it's off
                            self.will_move = False
                            self.location = 'left_hall'
                elif self.location == 'right':
                    if self.random <= 9:
                        audio.sounds[f'foxy_left{foxy_move}'].play()
                        self.will_move = False
                        self.location = 'left'
                    elif self.random == 10:
                        if viewing_hall != 'right':
                            audio.sounds['foxy_run_right'].play()
                            # if they're waiting to move into hall but flashlight is on,
                            # they will move right when it's off
                            self.will_move = False
                            self.location = 'right_hall'
                elif (self.location == 'closet' or self.location == 'running_to_closet') and not viewing_closet:
                    self.progress += 1
                    self.will_move = False
        if close_walk:
            walk = random.randint(1, 4)
            if self.name == 'bonnie':
                audio.sounds[f'close_walk{walk}'].channel = pygame.mixer.Channel(7)
                audio.sounds[f'close_walk{walk}'].pan = -100
            else:
                audio.sounds[f'close_walk{walk}'].channel = pygame.mixer.Channel(8)
                audio.sounds[f'close_walk{walk}'].pan = 100
            audio.sounds[f'close_walk{walk}'].play()
        if far_walk:
            walk = random.randint(1, 3)
            if self.name == 'bonnie':
                audio.sounds[f'far_walk{walk}'].channel = pygame.mixer.Channel(7)
                audio.sounds[f'far_walk{walk}'].pan = -100
            else:
                audio.sounds[f'far_walk{walk}'].channel = pygame.mixer.Channel(8)
                audio.sounds[f'far_walk{walk}'].pan = 100
            audio.sounds[f'far_walk{walk}'].play()
