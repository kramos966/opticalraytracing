import pygame

class App(object):
    def __init__(self, w, h):
        self.w, self.h = self.size = w, h
        self.display = pygame.display.set_mode(self.size)

