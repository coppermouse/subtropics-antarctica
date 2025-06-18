# -----------------------------------------
# source/resource_handler.py
# ------------------------------------------

import pygame
import json
import os
from paths import res_folder
from on_signal import on_signal
from config import SOUND
from config import MUSIC


class ResourceHandler:

    images = dict()
    sounds = dict()
    jsons = dict()

    @on_signal(type='on setup', order=12)
    def on_setup(message):
        cls = ResourceHandler

        cls.load_images()
        cls.load_jsons()

        if SOUND:
            cls.load_sounds()

        if MUSIC:
            cls.load_music()

    @classmethod
    def load_images(cls):
        for file in os.listdir(res_folder):
            if not file.endswith(".png"):
                continue
            surface = pygame.image.load(os.path.join(
                res_folder, file)).convert()
            surface.set_colorkey((128,255,255))

            final = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            final.blit(surface)

            cls.images[file[:-4]] = surface

    @classmethod
    def load_jsons(cls):
        for file in os.listdir(res_folder):
            if not file.endswith(".json"):
                continue
            with open(os.path.join(res_folder, file)) as f:
                cls.jsons[file[:-5]] = json.loads(f.read())

    @classmethod
    def load_sounds(cls):

        pygame.mixer.init()

        for file in os.listdir(res_folder):
            if not file.endswith(".wav"):
                continue
            cls.sounds[file[:-4]] = pygame.mixer.Sound(os.path.join(
                res_folder, file))

    @classmethod
    def load_music(cls):

        pygame.mixer.init()

        # find the first mp3 and make that the music,
        # we just assume there is only one mp3 at the moment and that is the music file

        for file in os.listdir(res_folder):
            if not file.endswith(".mp3"):
                continue
            pygame.mixer.music.load(os.path.join(res_folder, file))
