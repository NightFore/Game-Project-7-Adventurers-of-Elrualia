import pygame
import os
import pytmx
from pygame.locals import *
vec = pygame.math.Vector2
"""
    Settings
"""
# Game Settings
project_title = "Adventurers of Elrualia"
screen_size = WIDTH, HEIGHT = 1280, 768
FPS = 60

TILESIZE    = 32
GRIDWIDTH   = WIDTH  / TILESIZE
GRIDHEIGHT  = HEIGHT / TILESIZE


# Player Settings
PLAYER_SPEED    = 300
PLAYER_IMG      = "Data\Graphics\Player_pipoya_female_13_2.png"
PLAYER_HIT_RECT = pygame.Rect(0, 0, 35, 35)

# Mob Settings
MOB_SPEED   = 150
MOB_IMG     = "Data\Graphics\Mobs_enemy_04_1.png"


"""
    Colors
"""
RED         = 255, 0,   0

GREEN       = 0,   255, 0
DARKGREEN   = 60,  210, 120

BLUE        = 0,   0,   255
LIGHTBLUE   = 140, 205, 245

GREY        = 150, 170, 210
LIGHTGREY   = 100, 100, 100

BLACK       = 0,   0,   0
WHITE       = 255, 255, 255

BGCOLOR     = 200, 200, 200



"""
    Helpful Functions
"""
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



def load_tile_table(filename, width, height, colorkey=(0,0,0)):
    image = pygame.image.load(filename).convert()
    image.set_colorkey(colorkey)
    image_width, image_height = image.get_size()
    tile_table = []
    for tile_y in range(int(image_height/height)):
        line = []
        tile_table.append(line)
        for tile_x in range(int(image_width/width)):
            rect = (tile_x*width, tile_y*height, width, height)
            line.append(image.subsurface(rect))
    return tile_table



def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)





"""
    Game
"""
class Game:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(300, 75)
        self.gameDisplay    = ScaledGame(project_title, screen_size, 60)
        self.clock          = pygame.time.Clock()
        self.dt             = self.clock.tick(FPS) / 1000
        self.load_data()
        self.new()

    def load_data(self):
        self.map            = Map("Data\Map\Map_1.tmx")
        self.player_img     = load_tile_table(PLAYER_IMG, 32, 32)
        self.mob_img        = load_tile_table(MOB_IMG, 32, 32)

    def new(self):
        self.all_sprites    = pygame.sprite.Group()
        self.mobs           = pygame.sprite.Group()
        self.walls          = pygame.sprite.Group()
        for x in range(10, 20):
            Wall(self, x, 5)
        self.player         = Player(self, 10, 10)
        self.mob            = Mob(self, 12, 12)
        self.camera         = Camera(self.map.width, self.map.height)

    def run(self):
        self.gameExit = False
        while not self.gameExit:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()
            

    def quit_game(self):
        pygame.quit()
        quit()


    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()


    def update(self):
        self.gameDisplay.update()
        self.all_sprites.update()
        self.camera.update(self.player)


    def draw(self):
        self.gameDisplay.fill(BGCOLOR)
        self.draw_grid()
        for sprite in self.all_sprites:
            self.gameDisplay.blit(sprite.image, self.camera.apply(sprite))
        pygame.display.flip()


    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pygame.draw.line(self.gameDisplay, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pygame.draw.line(self.gameDisplay, LIGHTGREY, (0, y), (WIDTH, y))



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

    def __init__(self, title, game_size, FPS, first_screen=False):
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
        self.FPS = FPS
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
        for event in pygame.event.get():
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
        self.clock.tick(self.FPS)



class Map():
    def __init__(self, filename):
        self.tmxdata    = pytmx.load_pygame(filename, pixelalpha=True)
        self.tilewidth  = self.tmxdata.tilewidth
        self.tileheight = self.tmxdata.tileheight
        self.width      = self.tilewidth  * TILESIZE
        self.height     = self.tileheight * TILESIZE



class Camera():
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width  = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(WIDTH  / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # Limit to map size
        x = min(0, x)                           # Left
        x = max(-(self.width-WIDTH), x)         # Right
        y = min(0, y)                           # Top
        y = max(-(self.height - HEIGHT), y)     # Bottom
        self.camera = pygame.Rect(x, y, self.width, self.height)
    


class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        
        self.index              = 0
        self.images             = self.game.player_img
        self.images_bottom      = self.images[0]
        self.images_left        = self.images[1]
        self.images_right       = self.images[2]
        self.images_top         = self.images[3]
        self.images             = self.images_bottom
        self.image              = self.images_bottom[self.index]
        self.rect               = self.image.get_rect()
        self.hit_rect           = PLAYER_HIT_RECT
        self.hit_rect.center    = self.rect.center
    
        self.dt                 = game.dt
        self.current_time       = 0
        self.current_frame      = 0
        self.animation_time     = 0.15
        self.animation_frames   = 6

        
    def get_keys(self):
        self.vel = vec(0, 0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -PLAYER_SPEED
            self.images = self.images_left
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = +PLAYER_SPEED
            self.images = self.images_right
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vel.y = -PLAYER_SPEED
            self.images = self.images_top
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vel.y = +PLAYER_SPEED
            self.images = self.images_bottom

        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

    def collide_with_walls(self, dir):
        if dir == "x":
            hits = pygame.sprite.spritecollide(self, self.game.walls, False, collide_hit_rect)
            if hits:
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.hit_rect.width / 2
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right + self.hit_rect.width / 2
                self.vel.x = 0
                self.hit_rect.centerx = self.pos.x
            
        if dir == "y":
            hits = pygame.sprite.spritecollide(self, self.game.walls, False, collide_hit_rect)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.hit_rect.height / 2
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom + self.hit_rect.height / 2
                self.vel.y = 0
                self.hit_rect.centery = self.pos.y

    def update_time_dependent(self):
        self.current_time += self.dt
        if self.current_time >= self.animation_time:
            self.current_time = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

    def update_frame_dependent(self):
        self.current_frame += 1
        if self.current_frame >= self.animation_frames:
            self.current_frame = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

    def update(self):
        self.get_keys()
        self.update_time_dependent()
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        self.collide_with_walls("x")
        self.hit_rect.centery = self.pos.y
        self.collide_with_walls("y")
        self.rect.center = self.hit_rect.center



class Mob(pygame.sprite.Sprite):
    def __init__(self, game, x ,y):
        self.groups = game.all_sprites, game.mobs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        self.rot = 0
        
        self.index              = 0
        self.images             = self.game.mob_img
        self.images_bottom      = self.images[0]
        self.images_left        = self.images[1]
        self.images_right       = self.images[2]
        self.images_top         = self.images[3]
        self.images             = self.images_bottom
        self.image              = self.images_bottom[self.index]
        self.rect               = self.image.get_rect()
    
        self.dt                 = game.dt
        self.current_time       = 0
        self.current_frame      = 0
        self.animation_time     = 0.15
        self.animation_frames   = 6

    def update_angle(self):
        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        if -135 <= self.rot <= -45:
            self.images = self.images_bottom
        if -180 <= self.rot <= -135 or 135 <=  self.rot <= 180:
            self.images = self.images_left
        if -0 <= self.rot <= 45 or -45 <=  self.rot <= 0:
            self.images = self.images_right
        if 45 <=  self.rot <= 135:
            self.images = self.images_top
        

    def update_time_dependent(self):
        self.current_time += self.dt
        if self.current_time >= self.animation_time:
            self.current_time = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

    def update_frame_dependent(self):
        self.current_frame += 1
        if self.current_frame >= self.animation_frames:
            self.current_frame = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

    def update(self):
        self.update_angle()
        self.update_time_dependent()
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.acc = vec(MOB_SPEED, 0).rotate(-self.rot)
        self.vel += self.acc * self.game.dt
        self.pos +=  self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
        self.rect.center = self.pos



class Wall(pygame.sprite.Sprite):
    def __init__(self, game, x ,y):
        self.groups = game.all_sprites, game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE


g = Game()
g.run()
