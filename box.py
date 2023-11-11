import pygame


class Hitbox:
    def __init__(self, rect, colour):
        self.rect = rect
        self.colour = colour


hitboxes = {
    'slow_left': Hitbox(pygame.Rect(-7, -13, 348, 778), (255, 0, 255)),
    'fast_left': Hitbox(pygame.Rect(-3, -13, 206, 778), (100, 50, 255)),
    'slow_right': Hitbox(pygame.Rect(681, -1, 344, 778), (255, 0, 255)),
    'fast_right': Hitbox(pygame.Rect(821, -3, 206, 778), (100, 50, 255)),
    'left_door': Hitbox(pygame.Rect(18, 148, 262, 538), (255, 0, 0)),
    'right_door': Hitbox(pygame.Rect(1020, 132, 262, 538), (255, 0, 0)),
    'run_back': Hitbox(pygame.Rect(10, 682, 998, 80), (255, 0, 0)),
    'debounce': Hitbox(pygame.Rect(12, 464, 998, 192), (255, 0, 0)),
    'closet': Hitbox(pygame.Rect(576, 130, 262, 538), (255, 0, 0)),
    'honk': Hitbox(pygame.Rect(552, 333, 11, 11), (255, 255, 0))
}
