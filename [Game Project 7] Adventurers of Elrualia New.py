import pygame
import os
import pytmx
import random
import pytweening as tween
from pygame.locals import *
from os import path
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
PLAYER_IMG      = "Player_pipoya_female_13_2.png"
PLAYER_HIT_RECT = pygame.Rect(0, 0, 35, 35)
PLAYER_HEALTH   = 100
PLAYER_SPEED    = 300


# Mob Settings
MOB_IMG         = "Mobs_enemy_04_1.png"
MOB_HIT_RECT    = pygame.Rect(0, 0, 30, 30)
MOB_HEALTH      = 25
MOB_SPEED       = 125
MOB_DAMAGE      = 10
MOB_RADIUS      = 30
MOB_KNOCKBACK   = 20

# Sword Settings
SWORD_IMG       = "Sword_PixelHole_x2.png"
SWORD_HIT_RECT  = pygame.Rect(0, 0, 30, 30)
SWORD_SPEED     = 50
SWORD_DAMAGE    = 10
SWORD_KNOCKBACK = 20
SWORD_LIFETIME  = 300
SWORD_RATE      = 500
SWORD_OFFSET    = vec(20, 0)

# Items Settings
ITEM_IMAGES     = {"heart": ["items_beyonderboy_heart_1.png"]}

# Tweening
BOB_RANGE = 20
BOB_SPEED = 0.6

# Layer Settings
LAYER_WALL      = 1
LAYER_ITEMS     = 1
LAYER_PLAYER    = 2
LAYER_MOB       = 2
LAYER_SWORD     = 3
LAYER_EFFECTS   = 4

"""
    Colors
"""
RED         = 255, 0,   0

GREEN       = 0,   255, 0
DARKGREEN   = 60,  210, 120

BLUE        = 0,   0,   255
LIGHTBLUE   = 140, 205, 245

YELLOW      = 255, 255, 0
CYAN        = 0,  255,  255

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

def load_image(image_path, image_list):
    images = []
    for image in image_list:
        images.append(pygame.image.load(path.join(image_path, image)).convert_alpha())
    return images



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



def collide_with_walls(sprite, group, dir):
    if dir == "x":
        hits = pygame.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
        
    if dir == "y":
        hits = pygame.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)



def draw_health(self):
    if 100*self.health/self.maxhealth > 60:
        color = GREEN
    elif 100*self.health/self.maxhealth > 30:
        color = YELLOW
    else:
        color = RED
    if self.health < 0:
        self.health = 0
    width = int(self.rect.width * self.health/self.maxhealth)
    pygame.draw.rect(self.image, color, pygame.Rect(0, 0, width, 7))
        



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
        game_folder         = path.dirname(__file__)
        data_folder         = path.join(game_folder, "data")
        map_folder          = path.join(data_folder, "Map")
        graphics_folder     = path.join(data_folder, "graphics")
        
        self.map            = Map(path.join(map_folder, "Map_1.tmx"))
        self.map_img        = self.map.make_map()
        self.map_rect       = self.map_img.get_rect()
        
        self.player_img     = load_tile_table(path.join(graphics_folder, PLAYER_IMG), 32, 32)
        self.mob_img        = load_tile_table(path.join(graphics_folder, MOB_IMG), 32, 32)
        self.sword_img      = pygame.image.load(path.join(graphics_folder, SWORD_IMG)).convert_alpha()

        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = load_image(graphics_folder, ITEM_IMAGES[item])

    def new(self):
        self.draw_debug     = False
        self.camera         = Camera(self.map.width, self.map.height)
        self.all_sprites    = pygame.sprite.LayeredUpdates()
        self.mobs           = pygame.sprite.Group()
        self.sword          = pygame.sprite.Group()
        self.walls          = pygame.sprite.Group()
        self.items          = pygame.sprite.Group()

        for tile_layer in self.map.tmxdata.layers:
            if tile_layer.name == "collision":
                for x, y, image in tile_layer.tiles():
                    Obstacle(self, x, y, self.map.tmxdata.tilewidth, self.map.tmxdata.tileheight)

        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width/2, tile_object.y + tile_object.height/2)
            if tile_object.name == "player":
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == "mob":
                self.mob = Mob(self, obj_center.x, obj_center.y)
            if tile_object.name in ["heart"]:
                Item(self, obj_center, tile_object.name)


    def run(self):
        self.playing = True
        while self.playing:
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
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit_game()
                if event.key == pygame.K_h:
                    self.draw_debug = not self.draw_debug


    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)

        # Player
        hits = pygame.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            self.player.health -= MOB_DAMAGE
            self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False

        # Sword
        hits_1 = pygame.sprite.groupcollide(self.mobs, self.sword, False, False, collide_hit_rect)
        hits_2 = pygame.sprite.groupcollide(self.sword, self.mobs, False, False, collide_hit_rect)
        for mobs in hits_1:
            for sword in hits_2:
                if sword.hit == False:
                    sword.hit = True
                    mobs.health -= SWORD_DAMAGE
                    mobs.pos += vec(SWORD_KNOCKBACK, 0).rotate(-sword.rot)
                    mobs.vel = vec(0, 0)

    
    def draw(self):
        self.gameDisplay.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        for sprite in self.all_sprites:
            self.gameDisplay.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                pygame.draw.rect(self.gameDisplay, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)
        if self.draw_debug:
            for wall in self.walls:
                pygame.draw.rect(self.gameDisplay, CYAN, self.camera.apply_rect(wall.rect), 1)
        self.gameDisplay.update()


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
        self.width      = self.tmxdata.width  * self.tmxdata.tilewidth
        self.height     = self.tmxdata.height * self.tmxdata.tileheight

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth, y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pygame.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface



class Camera():
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width  = width
        self.height = height
    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(WIDTH  / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # Limit to map size
        x = min(0, x)                           # Left
        x = max(-(self.width-WIDTH), x)         # Right
        y = min(0, y)                           # Top
        y = max(-(self.height-HEIGHT), y)       # Bottom
        self.camera = pygame.Rect(x, y, self.width, self.height)
    


class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = LAYER_PLAYER
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.maxhealth          = PLAYER_HEALTH
        self.health             = self.maxhealth
        self.side               = 0
        self.last_slash         = 0
        
        self.rot                = 0
        self.pos                = vec(x, y)
        self.vel                = vec(0, 0)
    
        self.index              = 0
        self.images             = self.game.player_img
        self.images_bottom      = self.images[0]
        self.images_left        = self.images[1]
        self.images_right       = self.images[2]
        self.images_top         = self.images[3]
        self.images             = self.images_bottom
        self.image              = self.images_bottom[self.index]
        self.rect               = self.image.get_rect()
        self.rect.center        = self.pos
        self.hit_rect           = PLAYER_HIT_RECT
        self.hit_rect.center    = self.rect.center
    
        self.dt                 = game.dt
        self.current_time       = 0
        self.animation_time     = 0.15

        
    def get_keys(self):
        self.vel = vec(0, 0)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -PLAYER_SPEED
            self.images = self.images_left
            self.side = 0
            self.rot = 180
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = +PLAYER_SPEED
            self.images = self.images_right
            self.side = 1
            self.rot = 0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vel.y = -PLAYER_SPEED
            self.images = self.images_top
            self.side = 2
            self.rot = 90
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vel.y = +PLAYER_SPEED
            self.images = self.images_bottom
            self.side = 3
            self.rot = -90
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071

        if keys[pygame.K_SPACE]:
            now = pygame.time.get_ticks()
            if now - self.last_slash > SWORD_RATE:
                self.last_slash = now
                pos = self.pos + SWORD_OFFSET.rotate(-self.rot)
                Sword(self.game, pos, self.rot, self.side)
            
    def update_time_dependent(self):
        self.current_time += self.dt
        if self.current_time >= self.animation_time:
            self.current_time = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

    def update(self):
        self.get_keys()
        self.update_time_dependent()
        
        self.image = pygame.transform.rotate(self.image, 0)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        
        self.pos += self.vel * self.game.dt
        
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, "x")
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, "y")
        self.rect.center = self.hit_rect.center

        draw_health(self)
        if self.health <= 0:
            self.kill()



class Mob(pygame.sprite.Sprite):
    def __init__(self, game, x ,y):
        self._layer = LAYER_MOB
        self.groups = game.all_sprites, game.mobs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.maxhealth          = MOB_HEALTH
        self.health             = self.maxhealth
    
        self.rot = 0
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        
        self.index              = 0
        self.images             = self.game.mob_img
        self.images_bottom      = self.images[0]
        self.images_left        = self.images[1]
        self.images_right       = self.images[2]
        self.images_top         = self.images[3]
        self.images             = self.images_bottom
        self.image              = self.images_bottom[self.index]
        self.rect               = self.image.get_rect()
        self.rect.center        = self.pos
        self.hit_rect           = MOB_HIT_RECT.copy()
        self.hit_rect.center    = self.rect.center
    
        self.dt                 = game.dt
        self.current_time       = 0
        self.animation_time     = 0.15

    def update_angle(self):
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

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < MOB_RADIUS:
                    if self.acc != -dist.normalize():
                        self.acc += dist.normalize()
                    else:
                        self.acc += vec(random.choice((self.acc.y, -self.acc.y)), random.choice((self.acc.x, -self.acc.x)))
        

    def update(self):
        self.update_angle()
        self.update_time_dependent()
        
        self.image = pygame.transform.rotate(self.image, 0)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        self.acc = vec(1, 0).rotate(-self.rot)
        self.avoid_mobs()
        self.acc.scale_to_length(MOB_SPEED)
        self.acc -= self.vel
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2

        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, "x")
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, "y")
        self.rect.center = self.hit_rect.center
    
        draw_health(self)
        if self.health <= 0:
            self.kill()


class Sword(pygame.sprite.Sprite):
    def __init__(self, game, pos, rot, side):
        self._layer = LAYER_SWORD
        self.groups = game.all_sprites, game.sword
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game               = game
        self.hit                = False
        self.spawn_time         = pygame.time.get_ticks()
    
        self.rot                = rot
        self.pos                = vec(pos)
        self.vel                = vec(1, 0).rotate(-self.rot) * SWORD_SPEED
    
        self.image              = self.game.sword_img
        self.image_bottom       = pygame.transform.rotate(self.image, +180)
        self.image_left         = pygame.transform.rotate(self.image, +90)
        self.image_right        = pygame.transform.rotate(self.image, -90)
        self.image_top          = pygame.transform.rotate(self.image, 0)
        self.image_list         = [self.image_left, self.image_right, self.image_top, self.image_bottom]
        self.image              = self.image_list[side]
        self.rect               = self.image.get_rect()
        self.rect.center        = self.pos
        self.hit_rect           = SWORD_HIT_RECT
        self.hit_rect.center    = self.rect.center

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos.x
        self.hit_rect.centery = self.pos.y
        if pygame.time.get_ticks() - self.spawn_time > SWORD_LIFETIME:
            self.kill()



class Obstacle(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self._layer = LAYER_WALL
        self.groups = game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = self.x * w
        self.rect.y = self.y * h



class Item(pygame.sprite.Sprite):
    def __init__(self, game, pos, type):
        self._layer = LAYER_ITEMS
        self.groups = game.all_sprites, game.items
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game               = game
        self.type               = type
        self.pos                = pos
        
        self.image              = self.game.item_images[self.type][0]
    
        self.rect               = self.image.get_rect()
        self.rect.center        = self.pos
        self.hit_rect           = self.image.get_rect()
        self.hit_rect.center    = self.rect.center

        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update_bobbing(self):
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1

    def update(self):
        self.update_bobbing()



g = Game()
while True:
    g.new()
    g.run()
