import pygame
import os
import time
import random
import pygame_textinput
import pytmx

from pygame.locals import *
from operator import itemgetter


############################################################
"""
    Main Functions
"""
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
        pygame.init()

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



class Setup():
    def __init__(self):
        # Setup
        self.events         = ""
        self.background     = None
        self.music          = None

        # State
        self.button         = False
        self.list_button    = []
        
        self.text           = False
        self.list_text      = []


    def update_init(self, background=None, music=None, button=False, text=False):
        self.background = background
        self.update_music(music)

        self.button         = button
        self.list_button    = []
        
        self.text           = text
        self.list_text      = []


    def update_music(self, music):
        if self.music != music and music != None:
            self.music = music
            pygame.mixer.music.load(music)
            pygame.mixer.music.play(-1)
            

    def update_1(self):
        if self.background != None:
            if isinstance(self.background, tuple) == True:
                gameDisplay.fill(self.background)
            else:
                gameDisplay.blit(self.background, (0,0))
        
        self.events = pygame.event.get()


    def update_2(self):
        # Button
        if self.button == True:
            for index in self.list_button:
                index.update()

        # Text
        if self.text == True:
            for index in self.list_text:
                index.update()
Setup = Setup()



class Button():
    def __init__(self, text, sound, pos, display, variable, action=None):
        """
        Setup    : Add button to list_button
        Sound    : sound_action, sound_active
        Position : center, x, y, width, height, border width, border
        Text     : text, font
        Display  : Active/Inactive button display depending of the mouse position
        Action   : variable, action
        """
        # Setup
        Setup.button = True
        Setup.list_button.append(self)

        # Text
        self.text, self.font = text[0], text[1]

        # Sound Effect
        self.sound_action   = sound[0]
        self.sound_active   = sound[1]
        self.sound_state    = False

        # Position
        self.center     = pos[0]
        self.x          = pos[1]
        self.y          = pos[2]
        if len(pos) > 3:
            self.w      = pos[3]
            self.h      = pos[4]
            self.b      = pos[5]
            self.border = pos[6]

        # Button
        if isinstance(display[0], tuple) == True or display[0] is None:
            self.inactive   = display[0]
            self.active     = display[1]
            self.display    = self.inactive

            # Center
            if self.center == True:
                self.x  = self.x - self.w/2
                self.y  = self.y - self.h/2
            self.rect   = pygame.Rect(self.x, self.y, self.w, self.h)

        # Button Image
        elif isinstance(display[0], pygame.Surface) == True:
            self.inactive   = display[0].convert()
            self.active     = display[1].convert()
            self.display    = self.inactive

            # Center
            if self.center == False:
                self.rect = self.display.get_rect(topleft=(self.x, self.y))
            elif self.center == True:
                self.rect = self.display.get_rect(center=(self.x, self.y))
        
        # Action
        self.variable   = variable
        self.action     = action

        # Scale
        self.factor_w       = 1
        self.factor_h       = 1
        self.x_scaled       = self.rect[0]
        self.y_scaled       = self.rect[1]
        self.w_scaled       = self.rect[2]
        self.h_scaled       = self.rect[3]
        self.rect_scaled    = self.rect


    def update_scale(self):
        if self.factor_w != gameDisplay.factor_w or self.factor_h != gameDisplay.factor_h:
            self.factor_w    = gameDisplay.factor_w
            self.factor_h    = gameDisplay.factor_h
            self.x_scaled    = self.rect[0] * self.factor_w
            self.y_scaled    = self.rect[1] * self.factor_h
            self.w_scaled    = self.rect[2] * self.factor_w
            self.h_scaled    = self.rect[3] * self.factor_h
            self.rect_scaled = pygame.Rect(self.x_scaled, self.y_scaled, self.w_scaled, self.h_scaled)


    def update(self):
        # Button
        if isinstance(self.display, tuple) == True:
            pygame.draw.rect(gameDisplay, self.display, self.rect)
            if self.border == True:
                pygame.draw.rect(gameDisplay, color_black, self.rect, self.b)

        # Button Image
        elif isinstance(self.display, pygame.Surface) == True:
            gameDisplay.blit(self.display, self.rect)
        
        # Text
        if self.text != None or self.font != None:
            font, color     = self.font()
            textSurf        = font.render(self.text, True, color)
            textRect        = textSurf.get_rect()
            textRect.center = (self.x + self.w/2), (self.y + self.h/2)
            gameDisplay.blit(textSurf, textRect)

        # Event
        for event in Setup.events:
            mouse = pygame.mouse.get_pos()
            self.update_scale()

            if self.rect_scaled.collidepoint(mouse):
                self.display = self.active

                if self.sound_active != None and self.sound_state == False:
                    pygame.mixer.Sound.play(self.sound_active)
                    self.sound_state = True

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.action != None:
                    if self.sound_action != None:
                        pygame.mixer.Sound.play(self.sound_action)

                    if self.variable != None:
                        self.action(self.variable)
                    else:
                        self.action() 
            else:
                self.display     = self.inactive
                self.sound_state = False



class Text():
    def __init__(self, text, pos, hollow=False, outline=False, stroke=0, setup=False):
        """
        Text     : text, font
        Position : center, x ,y
        Hollow   : Create a hollow text surface
        Outline  : Create a surface around the text
        Setup    : Add text to the list_text
        """
        # Text
        self.text               = text[0]
        self.font, self.color   = text[1]()

        # Position
        self.center = pos[0]
        self.x      = pos[1]
        self.y      = pos[2]
        self.textSurface = self.font.render(self.text, True, self.color)
    
        # Center
        if self.center == False:
            self.textRect        = (self.x, self.y)
            
        elif self.center == True:
            self.textRect        = self.textSurface.get_rect()
            self.textRect.center = (self.x, self.y)

        # Hollow/Outline
        self.hollow     = hollow
        self.outline    = outline
        self.stroke     = stroke

        if isinstance(self.outline, tuple) == True:
            self.textSurface = self.textOutline(self.font, self.text, self.color, self.outline, self.stroke)

        elif hollow == True:
            self.textSurface = self.textHollow(self.font, self.text, self.color, self.stroke)
        
        # Setup
        if setup == True:
            Setup.text = True
            Setup.list_text.append(self)
            
        elif setup == False:
            gameDisplay.blit(self.textSurface, self.textRect)


    def textHollow(self, font, message, fontcolor, stroke):
        notcolor = [c^0xFF for c in fontcolor]
        base     = font.render(message, 0, fontcolor, notcolor)
        size     = base.get_width() + stroke, base.get_height() + stroke
        img      = pygame.Surface(size, 16)
        img.fill(notcolor)
        base.set_colorkey(0)

        for a in range(-stroke, 3+stroke):
            for b in range(-stroke, 3+stroke):
                img.blit(base, (a, b))

        base.set_colorkey(0)
        base.set_palette_at(1, notcolor)
        img.blit(base, (1, 1))
        img.set_colorkey(notcolor)
        return img

    def textOutline(self, font, message, fontcolor, outlinecolor, stroke):
        base    = font.render(message, 0, fontcolor)
        outline = self.textHollow(font, message, outlinecolor, stroke)
        img     = pygame.Surface(outline.get_size(), 16)
        img.blit(base, (1, 1))
        img.blit(outline, (0, 0))
        img.set_colorkey(0)
        return img
            
    def update(self):
        gameDisplay.blit(self.textSurface, self.textRect)



def text_title():
    font = pygame.font.SysFont(None, 100)
    color = color_button
    return font, color

def Text_Button():
    font = pygame.font.SysFont(None, 40)
    color = color_blue
    return font, color

def text_interface():
    font = pygame.font.SysFont(None, 35)
    color = color_black
    return font, color

def text_interface_2():
    font = pygame.font.SysFont(None, 30)
    color = color_black
    return font, color



############################################################


"""
    Tools Functions
"""
def quit_game():
    pygame.quit()
    quit()


def file_len(file):
    with open(file) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


def load_file(path, image=False):
    """
    Load    : All texts/images in directory. The directory must only contain texts/images.
    Path    : The relative or absolute path to the directory to load texts/images from.
    Image   : Load and convert image in the direcoty path.
    Return  : List of files.
    """
    file = []
    for file_name in os.listdir(path):
        if image == False:
            file.append(path + os.sep + file_name)
        if image == True:
            file.append(pygame.image.load(path + os.sep + file_name).convert())
    return file

                  
def transparent_image(image, x, y, opacity, screen):
    image = image.convert_alpha()
    alpha_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    alpha_surface.fill((255, 255, 255, opacity))
    image.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return screen.blit(image, (x, y))


class Text_Input():
    def __init__(self, pos):
        # Text Input
        self.textinput  = pygame_textinput.TextInput()
        self.input_line = self.textinput.get_text()
        
        # Input box position
        self.input_center   = pos[0]
        self.input_x        = pos[1]
        self.input_y        = pos[2]
        self.input_width    = pos[3]
        self.input_height   = pos[4]
        self.input_border   = pos[5]
    
        if self.input_center == True:
            self.input_x = self.input_x - self.input_width/2
            self.input_y = self.input_y - self.input_height/2

    def update(self):
        if self.textinput.update(Setup.events):
            """
            Input_Line  : Text entered by the keyboard
            Textinput   : Text Surface
            """
            self.input_line = self.textinput.get_text()
            self.textinput  = pygame_textinput.TextInput()
        
            if self.input_line != "":
                return self.input_line

        self.update_display()

    def update_display(self):
        """
         : Cutscene's User Interface
        Text        : Character's Dialogue
        Input Box   : Display Input Field & Text Entered
        """
        pygame.draw.rect(gameDisplay, color_grey,   [self.input_x, self.input_y, self.input_width, self.input_height])
        pygame.draw.rect(gameDisplay, color_black,  [self.input_x, self.input_y, self.input_width, self.input_height], self.input_border)

        # Text Center
        rect    = self.textinput.get_surface()
        text_w  = rect.get_width()//2
        text_h  = rect.get_height()//2
        box_w   = self.input_x + self.input_width/2
        box_h   = self.input_y + self.input_height/2
        size    = (box_w-text_w, box_h-text_h)
        gameDisplay.blit(self.textinput.get_surface(), size)


def load_tile_table(filename, width, height, colorkey=(0,0,0)):
    image = pygame.image.load(filename).convert()
    image.set_colorkey(colorkey)
    image_width, image_height = image.get_size()
    tile_table = []
    for tile_x in range(int(image_width/width)):
        line = []
        tile_table.append(line)
        for tile_y in range(int(image_height/height)):
            rect = (tile_x*width, tile_y*height, width, height)
            line.append(image.subsurface(rect))
    return tile_table



############################################################
"""
    Settings
"""
# Title
project_title = "Adventurers of Elrualia"


# Screen Size
Screen_size = display_width, display_height = 1280, 720
gameDisplay = ScaledGame(project_title, Screen_size)


"""
    Ressources
"""
# Colors
color_red           = 255, 20,  0
color_green         = 60,  210, 120
color_blue          = 0,   160, 230
color_grey          = 150, 170, 210
color_white         = 255, 255, 255
color_black         = 1,   0,   0

color_button        = 140, 205, 245
color_title_screen  = 30,  30,  30

background          = pygame.image.load("Data\Graphics\Background.png").convert()

tile_woods      = load_tile_table("Data\Tilesheet\Tile_woods.png", 40, 40)
tile_desert     = load_tile_table("Data\Tilesheet\Tile_desert.png", 40, 40)
tile_grass      = load_tile_table("Data\Tilesheet\Tile_grass.png", 40, 40)
tile_mountain_1 = load_tile_table("Data\Tilesheet\Tile_mountain_1.png", 40, 40)
tile_mountain_2 = load_tile_table("Data\Tilesheet\Tile_mountain_2.png", 40, 40)
tile_mountain_3 = load_tile_table("Data\Tilesheet\Tile_mountain_3.png", 40, 40)
tile_ocean      = load_tile_table("Data\Tilesheet\Tile_ocean.png", 40, 40)
tile_road       = load_tile_table("Data\Tilesheet\Tile_road.png", 40, 40)
tile_soil       = load_tile_table("Data\Tilesheet\Tile_soil.png", 40, 40)

############################################################
"""
    Game Functions
"""
def Main_Screen():
    MainIG.title_update()

    gameExit = False
    while not gameExit:
        gameDisplay.update()
        Setup.update_1()
        MainIG.update()
        Setup.update_2()
    
        for event in Setup.events:    
            if event.type == pygame.QUIT:
                quit_game()



class MainIG():
    def __init__(self):
        # Setup
        self.background     = background

        # State
        self.title          = False
        self.main           = False

        # List
        self.list_music     = load_file("Data\Music")

        # Grid
        self.tile_list      = [tile_woods, tile_desert, tile_grass, tile_mountain_1, tile_mountain_2, tile_mountain_3, tile_ocean, tile_road, tile_soil]
        self.grid_size      = 40
        self.grid_list      = [ [[2,0,0]]*int(display_height/self.grid_size) ] * int(display_width/self.grid_size)

        # Map
        self.current_map    = 0
        self.map = []
        for index in load_file("Data\Map"):
            self.map.append(pytmx.load_pygame(index, pixelalpha=True))

    def update(self):
        if self.main == True:
            self.main_update()

    def update_init(self, music=None, main=False):
        Setup.update_init(self.background, music)
        self.main   = main


    def title_update(self):
        # Setup
        self.update_init(None)

        # Main
        Text((project_title, text_title), (True, display_width/2, display_height/4), True, color_black, 3, setup=True)
        Button(("Start", text_interface), (None, None), (True, 1*display_width/4, 3*display_height/4, 150, 50, 5, True), (color_green, color_red), True, self.main_update)
        Button(("Music", text_interface), (None, None), (True, 2*display_width/4, 3*display_height/4, 150, 50, 5, True), (color_green, color_red), None, None)
        Button(("Exit",  text_interface), (None, None), (True, 3*display_width/4, 3*display_height/4, 150, 50, 5, True), (color_green, color_red), None, quit_game)
        

    def music_update(self):
        # Setup
        self.update_init(self.list_music[0])

        # Main         
        Text(("Music Gallery", text_title), (True, display_width/2, display_height/12), True, color_black, 3, setup=True)
        Button(("Return", text_interface), (True, 740, 570, 100, 40, 1, True), (None, None), (color_button, color_red), True, self.title_update)

        index = 0
        for row in range(round(0.5+len(self.list_music)/5)):
            for col in range(5):
                if index < len(self.list_music):
                    Button(("Music %i" % (index+1), Text_Button), (None, None), (False, display_width/64 + display_width/5*col, display_height/6 + display_height/9*row, display_width/6, display_height/12, 4, True), (color_green, color_red), self.list_music[index], Setup.update_music)
                    index += 1


    def main_update(self, init=False):
        if init == True:
            self.background = (255, 255, 255)
            self.update_init(main=True)
            Button(("Map", text_interface), (None, None), (False, 0, 670, 100, 50, 5, True), (color_green, color_red), None, self.map_update)

            Button(("Debug", text_interface), (None, None), (False, 1180, 670, 100, 50, 5, True), (color_green, color_red), None, self.debug_update)

        elif init == False:
            tile_terrain    = self.map[self.current_map].get_layer_by_name("Terrain")
            tile_obstacle   = self.map[self.current_map].get_layer_by_name("Obstacle")

            for x, y, image in tile_terrain.tiles():
                gameDisplay.blit(image, (x*self.grid_size, y*self.grid_size))
                
            for x, y, image in tile_obstacle.tiles():
                gameDisplay.blit(image, (x*self.grid_size, y*self.grid_size))
        

    def map_update(self):
        self.current_map += 1

        if self.current_map == len(self.map):
            self.current_map = 0
        
MainIG = MainIG()

Main_Screen()
