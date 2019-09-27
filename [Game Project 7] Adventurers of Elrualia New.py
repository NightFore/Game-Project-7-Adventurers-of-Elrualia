import pygame
import os

from pygame.locals import *
"""
    Settings
"""
project_title = "Adventurers of Elrualia"
screen_size = display_width, display_height = 1280, 768



"""
    Colors
"""
RED     = 255, 20,  0
GREEN   = 60,  210, 120
BLUE    = 0,   160, 230
GREY    = 150, 170, 210
WHITE   = 255, 255, 255
BLACK   = 1,   0,   0



"""
    Game
"""
class Game:
    def __init__(self):
        pygame.init()
        self.gameDisplay = ScaledGame(project_title, screen_size)
        self.clock = pygame.time.Clock()
        self.load_data()

    def load_data(self):
        pass
        


class ScaledGame(pygame.Surface):
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # Center window position
    game_size       = None
    ss              = None
    screen          = None
    clock           = None
    resize          = True
    zoom            = False
    game_gap        = None
    game_scaled     = None
    title           = None
    fps             = True
    set_fullscreen  = False
    factor_w        = 1
    factor_h        = 1

    def __init__(self, title, game_size, first_screen=False):
        # Title
        self.title = title
        pygame.display.set_caption(self.title)

        # Window Settings
        self.game_size   = game_size
        self.ss          = game_size
        self.game_gap    = (0, 0)
        self.screen_info = pygame.display.Info() # Required to set a good resolution for the game screen

        if first_screen == False:
            self.screen  = pygame.display.set_mode(game_size, RESIZABLE)
        else:
            first_screen = (self.screen_info.current_w, self.screen_info.current_h - 120) # Take 120 pixels from the height because of the menu bar, window bar and dock takes space
            self.screen  = pygame.display.set_mode(first_screen, RESIZABLE)
        
        # Sets up the Surface for the game.
        pygame.Surface.__init__(self, self.game_size)

        # Game Settings
        self.clock = pygame.time.Clock()

    
    def get_resolution(self, ss, gs): 
        gap = float(gs[0]) / float(gs[1]) # Game aspect ratio
        sap = float(ss[0]) / float(ss[1]) # Scaled aspect ratio
        if gap > sap:
            factor = float(gs[0]) /float(ss[0])
            new_h = gs[1]/factor #Divides the height by the factor which the width changes so the aspect ratio remains the same.
            game_scaled = (ss[0], new_h)
        elif gap < sap:
            factor = float(gs[1]) /float(ss[1])
            new_w = gs[0]/factor #Divides the width by the factor which the height changes so the aspect ratio remains the same.
            game_scaled = (new_w, ss[1])
        else:
            game_scaled = self.screen.get_size()
        return game_scaled


    def fullscreen(self):
        if self.set_fullscreen == False:
            self.screen = pygame.display.set_mode(self.game_size, FULLSCREEN)
            self.factor_w = 1
            self.factor_h = 1
            self.set_fullscreen = True
        else:
            self.resize = True
            self.set_fullscreen = False


    def update(self):
        # Display FPS in window title
        if self.fps == True:
            pygame.display.set_caption(self.title + " - " + str(int(self.clock.get_fps())) + "fps")

        #Updates screen properly
        win_size_done = False # Changes to True if the window size is got by the VIDEORESIZE event below
        for event in Setup.events:
            if event.type == VIDEORESIZE:
                ss = [event.w, event.h]
                self.resize = True
                win_size_done = True

                if ss[0] == self.screen_info.current_w:
                    self.zoom = True

        # Fullscreen
        if self.set_fullscreen == True:
            self.screen.blit(self, self.game_gap)

        # Resize
        elif self.resize == True:
            # Sizes not gotten by resize event
            if win_size_done == False:
                ss = [self.screen.get_width(), self.screen.get_height()]

            # Zoom
            if self.zoom == True and ss[0] != self.screen_info.current_w and ss[1] != self.ss[1]:
                self.game_scaled = self.game_size
                self.zoom = False
            else:
                self.game_scaled = self.get_resolution(ss, self.game_size)
                self.game_scaled = int(self.game_scaled[0]), int(self.game_scaled[1])
                
            # Scale game to screen resolution, keeping aspect ratio 
            self.screen = pygame.display.set_mode(self.game_scaled, RESIZABLE)
            self.resize = False

            # Usable Variables
            self.factor_w = self.game_scaled[0] / self.get_width()
            self.factor_h = self.game_scaled[1] / self.get_height()
            self.ss = ss

        # Add game to screen with the scaled size and gap required.                
        self.screen.blit(pygame.transform.scale(self, self.game_scaled), self.game_gap)
        
        pygame.display.flip()
        self.clock.tick(60)



Game()