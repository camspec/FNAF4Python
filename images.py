import pygame


class Screen:
    def __init__(self, name, frames, x=0, y=0, transparent=False, alpha=255, jumpscare=False):
        self.name = name
        self.frames = frames
        # image names have padded zeroes
        self.images = [pygame.image.load(f'assets/img/{name}/{str(i).zfill(2)}.png') for i in range(frames)]
        self.x = x
        self.y = y
        self.transparent = transparent
        self.alpha = alpha
        self.jumpscare = jumpscare
        if self.transparent:
            for i in self.images:
                i.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)


screens = {
    'room': Screen('room', 9),
    'run_left_door': Screen('run_left_door', 6),
    'run_right_door': Screen('run_right_door', 6),
    'running': Screen('running', 31),
    'start_left_door': Screen('start_left_door', 31),
    'start_right_door': Screen('start_right_door', 31),
    'left_door': Screen('left_door', 12),
    'right_door': Screen('right_door', 12),
    'leave_left_door': Screen('leave_left_door', 9),
    'leave_right_door': Screen('leave_right_door', 10),
    'start_room': Screen('start_room', 6, -240),
    'hour': Screen('hour', 7, 905, 18, True, 55),
    'retreating_bonnie': Screen('retreating_bonnie', 16),
    'jumpscare_bonnie_hall': Screen('jumpscare_bonnie_hall', 26, jumpscare=True),
    'retreating_chica': Screen('retreating_chica', 20),
    'jumpscare_chica_hall': Screen('jumpscare_chica_hall', 26, jumpscare=True),
    'run_bed': Screen('run_bed', 9),
    'start_bed': Screen('start_bed', 10),
    'bed': Screen('bed', 20),
    'leave_bed': Screen('leave_bed', 11),
    'start_room_bed': Screen('start_room_bed', 9),
    'jumpscare_bonnie_room': Screen('jumpscare_bonnie_room', 26, jumpscare=True),
    'jumpscare_chica_room': Screen('jumpscare_chica_room', 26, jumpscare=True),
    'retreating_freddles': Screen('retreating_freddles', 15),
    'jumpscare_freddy_bed': Screen('jumpscare_freddy_bed', 26, jumpscare=True),
    'jumpscare_freddy_room': Screen('jumpscare_freddy_room', 26, jumpscare=True),
    'retreating_foxy': Screen('retreating_foxy', 18),
    'closet_creak': Screen('closet_creak', 11, -240),
    'jumpscare_foxy_room': Screen('jumpscare_foxy_room', 26, jumpscare=True),
    'run_closet': Screen('run_closet', 7),
    'start_closet': Screen('start_closet', 14),
    'closet': Screen('closet', 11),
    'leave_closet': Screen('leave_closet', 10),
    'foxy_bite': Screen('foxy_bite', 11)
}
