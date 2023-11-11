import pygame

pygame.mixer.init()
pygame.mixer.set_num_channels(100)


class Sound:
    main_volume = 20

    def __init__(self, name, channel_id, volume=100, pan=0, loops=0):
        self.name = name
        self.channel = pygame.mixer.Channel(channel_id)
        self.volume = volume
        self.sound = pygame.mixer.Sound(f'assets/audio/{name}.wav')
        self.pan = pan
        self.loops = loops
        self.update_volume()

    def play(self):
        # pan ranges from -100 to 100, with 0 being half volume for both left and right channels
        # volume is from 0.0 to 1.0 so divide by 100
        # channel.set_volume(self.volume * (0.5 - self.pan / 200) / 100,
        #                         self.volume * (0.5 + self.pan / 200) / 100)
        self.channel.play(self.sound, self.loops)
        self.update_volume()

    def update_volume(self, volume=None):
        if volume is not None:
            self.volume = volume
        self.channel.set_volume(self.volume * (0.5 - self.pan / 200) / 100 * (Sound.main_volume / 100),
                                self.volume * (0.5 + self.pan / 200) / 100 * (Sound.main_volume / 100))


sounds = {
    'ambience': Sound('ambience', 0, volume=10, loops=-1),
    'clock_chime': Sound('clock_chime', 1, volume=25, pan=-50),
    'crickets': Sound('crickets', 2, volume=25, pan=50, loops=-1),
    'flashlight': Sound('flashlight', 3),
    'door_creak1': Sound('door_creak1', 4),
    'door_creak2': Sound('door_creak2', 4),
    'door_creak3': Sound('door_creak3', 4),
    'door_creak4': Sound('door_creak4', 4),
    'closet_close1': Sound('closet_close1', 4),
    'closet_close2': Sound('closet_close2', 4),
    'closet_close3': Sound('closet_close3', 4),
    'closet_creak': Sound('closet_creak', 4),
    'carpet_run': Sound('carpet_run', 5),
    'foxy_left1': Sound('foxy_left1', 6, volume=25),
    'foxy_left2': Sound('foxy_left2', 6, volume=25),
    'foxy_right1': Sound('foxy_right1', 6, volume=25),
    'foxy_right2': Sound('foxy_right2', 6, volume=25),
    'foxy_run_left': Sound('foxy_run_left', 7, pan=-100),
    'foxy_run_right': Sound('foxy_run_right', 8, pan=100),
    'foxy_enter_left': Sound('foxy_enter', 7, pan=-100),
    'foxy_enter_right': Sound('foxy_enter', 8, pan=100),
    'breathing': Sound('breathing', 9, volume=0, loops=-1),
    'freddles': Sound('freddles', 10, volume=0, loops=-1),
    'close_walk1': Sound('close_walk1', 7),
    'close_walk2': Sound('close_walk2', 7),
    'close_walk3': Sound('close_walk3', 7),
    'close_walk4': Sound('close_walk4', 7),
    'far_walk1': Sound('far_walk1', 7),
    'far_walk2': Sound('far_walk2', 7),
    'far_walk3': Sound('far_walk3', 7),
    'kitchen': Sound('kitchen', 11, volume=0, loops=-1),
    'scream1': Sound('scream1', 12, volume=100),
    'scream_closet': Sound('scream_closet', 13, volume=100),
    'random_laugh': Sound('random_laugh', 14, volume=25),
    'random_breath': Sound('random_breath', 14, volume=25),
    'random_dog': Sound('random_dog', 14, volume=25),
    'honk': Sound('honk', 15),
    'random_call': Sound('random_call', 16, volume=0)
}
