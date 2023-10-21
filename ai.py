import random


class Animatronic:
    cancel_movement = False
    force_turn = False

    def __init__(self, name, location, ai, force_move_hour=0, side=''):
        self.name = name
        self.location = location
        self.ai = ai
        self.side = side
        self.random = 0
        self.will_move = False
        self.seconds_at_door = 0
        self.force_move = False
        self.force_move_hour = force_move_hour

    def interval_update(self, second_intervals, door_shut, listening, room_jumpscare):
        if self.name == 'bonnie' or self.name == 'chica':
            self.random = random.randint(1, 2)
            if second_intervals % 5 == 0 and not Animatronic.cancel_movement:
                if random.randint(1, 20) <= self.ai and door_shut != self.side and listening != self.side:
                    self.will_move = True
            if second_intervals % 10 == 0:
                if self.will_move:
                    if self.location == 'hall_near' and listening != self.side:
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
            if second_intervals % 4 == 0 and room_jumpscare == self.name:
                Animatronic.force_turn = True

    def update(self, screen, night):
        if self.name == 'bonnie' or self.name == 'chica':
            # force move
            if self.force_move and screen.name == 'room':
                self.location = 'hall_near'
                self.force_move = False
            if self.location != 'hall_far' and self.location != 'hall_near':
                self.seconds_at_door = 0
            # determine if we should jumpscare
            if self.seconds_at_door > 20 - night:
                return True
            else:
                return False

    def move(self, viewing_hall):
        if self.name == 'bonnie' or self.name == 'chica':
            if self.will_move:
                if self.location == 'mid' or self.location == 'kitchen':
                    self.location = self.side
                    self.will_move = False
                elif self.location == self.side:
                    if self.random == 1:
                        # if they're waiting to move into hall but flashlight is on,
                        # they will move right when it's off
                        if viewing_hall != self.side:
                            self.location = 'hall_far'
                            self.will_move = False
                    else:
                        if self.name == 'bonnie':
                            self.location = 'mid'
                        else:
                            self.location = 'kitchen'
                        self.will_move = False
                elif self.location == 'hall_far':
                    self.location = 'hall_near'
                    self.will_move = False
