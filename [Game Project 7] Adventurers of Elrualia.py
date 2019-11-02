import pygame
import os
import pytmx
import pytweening as tween
from pygame.locals import *
from os import path
from random import choice, random
vec = pygame.math.Vector2

"""
    Settings
"""
# Game Settings
project_title = "Adventurers of Elrualia"
screen_size = WIDTH, HEIGHT = 800, 600
FPS = 60

TILESIZE    = 32
GRIDWIDTH   = WIDTH  / TILESIZE
GRIDHEIGHT  = HEIGHT / TILESIZE

# Player Settings
PLAYER_IMG      = "character_pipoya_male_01_2.png"
PLAYER_INDEX    = 1
PLAYER_HIT_RECT = pygame.Rect(0, 0, 35, 35)
PLAYER_HEALTH   = 3
PLAYER_SPEED    = 300

# Mob Settings
MOB_IMG         = "Mobs_enemy_04_1.png"
MOB_HIT_RECT    = pygame.Rect(0, 0, 30, 30)
MOB_HEALTH      = 2
MOB_SPEED       = 125
MOB_DAMAGE      = 1
MOB_KNOCKBACK   = 20
MOB_RADIUS      = 30
DETECT_RADIUS   = 300

# Sword Settings
SWORD_IMG       = "Sword_PixelHole_x2.png"
SWORD_HIT_RECT  = pygame.Rect(0, 0, 30, 30)
SWORD_SPEED     = 50
SWORD_DAMAGE    = 1
SWORD_KNOCKBACK = 20
SWORD_LIFETIME  = 300
SWORD_RATE      = 500
SWORD_OFFSET    = vec(20, 0)

# Tweening
BOB_RANGE = 10
BOB_SPEED = 0.3

# Layer Settings
LAYER_WALL      = 1
LAYER_ITEMS     = 1
LAYER_PLAYER    = 2
LAYER_MOB       = 2
LAYER_SWORD     = 3
LAYER_EFFECTS   = 4

# Items
ITEM_IMAGES     = {"heart": ["items_beyonderboy_heart_1.png"], "coin": ["items_beyonderboy_coin_1.png", "items_beyonderboy_coin_2.png", "items_beyonderboy_coin_3.png", "items_beyonderboy_coin_4.png", "items_beyonderboy_coin_5.png", "items_beyonderboy_coin_6.png", ]}
ITEM_DROPS      = ["heart", "coin"]

IMAGE_HEART     = "items_beyonderboy_heart.png"
IMAGE_COIN      = "items_beyonderboy_coin.png"

HEART_AMOUNT    = 1

# Effects
EFFECT_IMAGES   = {"pick_up": ["effect_beyonderboy_pick_up_item_1.png", "effect_beyonderboy_pick_up_item_2.png", "effect_beyonderboy_pick_up_item_3.png", "effect_beyonderboy_pick_up_item_4.png", "effect_beyonderboy_pick_up_item_5.png", "effect_beyonderboy_pick_up_item_6.png"]}


# Sounds
BG_MUSIC            = "music_aaron_krogh_310_world_map.mp3"

SOUNDS_PICK_UP      = "sfx_maoudamashii_system23.wav"
SOUNDS_SWORD_ATTACK = ["Battle_Slash_battle01.wav", "Battle_Slash_battle03.wav", "Battle_Slash_battle17.wav"]

VOICE_PLAYER_ATTACK = ["voice_wingless_seraph_jakigan_07_attack.wav", "voice_wingless_seraph_jakigan_08_attack.wav"] 
VOICE_PLAYER_DAMAGE = ["voice_wingless_seraph_jakigan_14_damage.wav", "voice_wingless_seraph_jakigan_15_damage.wav", "voice_wingless_seraph_jakigan_16_damage.wav"]

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

COLOR_INTERFACE = 140, 205, 245



"""
    Helpful Functions
"""
def update_time_dependent(sprite):
    sprite.current_time += sprite.dt
    if sprite.current_time >= sprite.animation_time:
        sprite.current_time = 0
        sprite.index = (sprite.index + 1) % len(sprite.images)
        sprite.image = sprite.images[sprite.index]
    sprite.rect = sprite.image.get_rect()
    sprite.rect.center = sprite.pos
    sprite.image = pygame.transform.rotate(sprite.image, 0)

def update_bobbing(sprite):
    offset = BOB_RANGE * (sprite.tween(sprite.step / BOB_RANGE) - 0.5)
    sprite.rect.centery = sprite.pos.y + offset * sprite.dir
    sprite.step += BOB_SPEED
    if sprite.step > BOB_RANGE:
        sprite.step = 0
        sprite.dir *= -1


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



def text_interface():
    font = pygame.font.SysFont(None, 32)
    color = WHITE
    return font, color



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



"""
    Game
"""
class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        pygame.init()
        pygame.key.set_repeat(300, 75)
        self.gameDisplay    = ScaledGame(project_title, screen_size, 60)
        self.clock          = pygame.time.Clock()
        self.dt             = self.clock.tick(FPS) / 1000
        self.load_data()
        self.new()

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.gameDisplay.blit(text_surface, text_rect)

    def load_data(self):
        game_folder         = path.dirname(__file__)
        data_folder         = path.join(game_folder, "data")
        graphics_folder     = path.join(data_folder, "graphics")
        map_folder          = path.join(data_folder, "map")
        sfx_folder          = path.join(data_folder, "sfx")
        voice_folder        = path.join(data_folder, "voice")
        music_folder        = path.join(data_folder, "music")

        self.font           = None
        self.dim_screen     = pygame.Surface(self.gameDisplay.get_size()).convert_alpha()
        self.dim_screen.fill((100, 100, 100, 120))

        self.map            = Map(path.join(map_folder, "Map_1.tmx"))
        self.map_img        = self.map.make_map()
        self.map_rect       = self.map_img.get_rect()
        
        self.player_img     = load_tile_table(path.join(graphics_folder, PLAYER_IMG), 32, 32)
        self.image_heart    = pygame.image.load(path.join(graphics_folder, IMAGE_HEART)).convert_alpha()
        self.image_coin     = pygame.image.load(path.join(graphics_folder, IMAGE_COIN)).convert_alpha()
        self.mob_img        = load_tile_table(path.join(graphics_folder, MOB_IMG), 32, 32)
        self.sword_img      = pygame.image.load(path.join(graphics_folder, SWORD_IMG)).convert_alpha()

        # Image Items
        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = load_image(graphics_folder, ITEM_IMAGES[item])

        # Image Effects
        self.effect_images = {}
        for effect in EFFECT_IMAGES:
            self.effect_images[effect] = load_image(graphics_folder, EFFECT_IMAGES[effect])

        # Sound Effects
        self.sounds_effects = {}
        self.sounds_effects["pick_up"]  = pygame.mixer.Sound(path.join(sfx_folder, SOUNDS_PICK_UP))
        self.sounds_effects["sword"]    = []
        for sound in SOUNDS_SWORD_ATTACK:
            self.sounds_effects["sword"].append(pygame.mixer.Sound(path.join(sfx_folder, sound)))

        # Sound Voices
        self.sounds_voice = {}
        self.sounds_voice["player_attack"] = []
        self.sounds_voice["player_damage"] = []
        for voice in VOICE_PLAYER_ATTACK:
            self.sounds_voice["player_attack"].append(pygame.mixer.Sound(path.join(voice_folder, voice)))
        for voice in VOICE_PLAYER_DAMAGE:
            self.sounds_voice["player_damage"].append(pygame.mixer.Sound(path.join(voice_folder, voice)))

        # Sound Musics
        pygame.mixer.music.load(path.join(music_folder, BG_MUSIC))


    def new(self):
        self.paused         = False
        self.draw_debug     = False
        self.camera         = Camera(self.map.width, self.map.height)
        self.all_sprites    = pygame.sprite.LayeredUpdates()
        self.mobs           = pygame.sprite.Group()
        self.sword          = pygame.sprite.Group()
        self.walls          = pygame.sprite.Group()
        self.items          = pygame.sprite.Group()
        self.effects        = pygame.sprite.Group()

        # Map Obstacles
        for tile_layer in self.map.tmxdata.layers:
            if tile_layer.name == "collision":
                for x, y, image in tile_layer.tiles():
                    Obstacle(self, x, y, self.map.tmxdata.tilewidth, self.map.tmxdata.tileheight)

        # Map Objects
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
        pygame.mixer.music.play(-1)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            if not self.paused:
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
                if event.key == pygame.K_p:
                    self.paused = not self.paused


    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)

        # Player => Mobs
        hits = pygame.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            choice(self.sounds_voice["player_damage"]).play()
            self.player.health -= MOB_DAMAGE
            self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False

        # Player => Items
        hits = pygame.sprite.spritecollide(self.player, self.items, True)
        for hit in hits:
            Effect(self, hit.pos, "pick_up")
            self.sounds_effects["pick_up"].play()
            if hit.type == "heart":
                self.player.add_health(HEART_AMOUNT)
            if hit.type == "coin":
                self.player.coin += 1

        # Sword => Mobs
        hits_1 = pygame.sprite.groupcollide(self.mobs, self.sword, False, False, collide_hit_rect)
        hits_2 = pygame.sprite.groupcollide(self.sword, self.mobs, False, False, collide_hit_rect)
        for mobs in hits_1:
            for sword in hits_2:
                if sword.hit == False:
                    sword.hit = True
                    choice(self.sounds_effects["sword"]).play()
                    mobs.health -= SWORD_DAMAGE
                    mobs.pos += vec(SWORD_KNOCKBACK, 0).rotate(-sword.rot)
                    mobs.vel = vec(0, 0)

    
    def draw(self):
        self.gameDisplay.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        self.player.draw_health()
        self.player.draw_coin()
        for sprite in self.all_sprites:
            self.gameDisplay.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                pygame.draw.rect(self.gameDisplay, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)
        if self.draw_debug:
            for wall in self.walls:
                pygame.draw.rect(self.gameDisplay, CYAN, self.camera.apply_rect(wall.rect), 1)
        if self.paused:
            self.gameDisplay.blit(self.dim_screen, (0, 0))
            self.draw_text("Paused", self.font, 105, RED, WIDTH/2, HEIGHT/2, align="center")
        self.gameDisplay.update()



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

        # Updates screen properly
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



class Text():
    def __init__(self, text, pos, hollow=False, outline=False, stroke=0):
        """
        Text     : text, font
        Position : center, x ,y
        Hollow   : Create a hollow text surface
        Outline  : Create a surface around the text
        """
        # Text
        self.display            = text[0]
        self.text               = str(text[1])
        self.font, self.color   = text[2]()

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

        if isinstance(self.outline, tuple) == True:
            self.textSurface = self.textOutline(self.font, self.text, self.color, self.outline)

        elif hollow == True:
            self.textSurface = self.textHollow(self.font, self.text, self.color)
        
        self.display.blit(self.textSurface, self.textRect)

    def textHollow(self, font, message, fontcolor):
        notcolor = [c^0xFF for c in fontcolor]
        base = font.render(message, 0, fontcolor, notcolor)
        size = base.get_width() + 2, base.get_height() + 2
        img = pygame.Surface(size, 16)
        img.fill(notcolor)
        base.set_colorkey(0)
        img.blit(base, (0, 0))
        img.blit(base, (2, 0))
        img.blit(base, (0, 2))
        img.blit(base, (2, 2))
        base.set_colorkey(0)
        base.set_palette_at(1, notcolor)
        img.blit(base, (1, 1))
        img.set_colorkey(notcolor)
        return img

    def textOutline(self, font, message, fontcolor, outlinecolor):
        if outlinecolor == (0,0,0):
            outlinecolor = (0,0,1)
        base = font.render(message, 0, fontcolor)
        outline = self.textHollow(font, message, outlinecolor)
        img = pygame.Surface(outline.get_size(), 16)
        img.blit(base, (1, 1))
        img.blit(outline, (0, 0))
        img.set_colorkey(0)
        return img


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
        # Setup
        self.game               = game
        self.groups             = self.game.all_sprites
        self._layer             = LAYER_PLAYER
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Settings
        self.maxhealth          = PLAYER_HEALTH
        self.health             = self.maxhealth
        self.coin               = 0

        self.last_slash         = 0
        self.moving             = False

        # Surface
        self.rot                = 0
        self.pos                = vec(x, y)
        self.vel                = vec(0, 0)

        self.base_index         = 1
        self.index              = self.base_index
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
        keys = pygame.key.get_pressed()

        # Movement
        self.vel = vec(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -PLAYER_SPEED
            self.images = self.images_left
            self.rot = 180
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = +PLAYER_SPEED
            self.images = self.images_right
            self.rot = 0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vel.y = -PLAYER_SPEED
            self.images = self.images_top
            self.rot = 90
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vel.y = +PLAYER_SPEED
            self.images = self.images_bottom
            self.rot = -90
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071
        self.moving = (self.vel.x != 0 or self.vel.y != 0)

        # Weapon
        if keys[pygame.K_SPACE]:
            if pygame.time.get_ticks() - self.last_slash >= SWORD_RATE:
                Sword(self.game, self)

    def draw_health(self):
        for x in range(int(self.health)):
            self.game.gameDisplay.blit(self.game.image_heart, (10 + x*32, 5))

    def draw_coin(self):
        self.game.gameDisplay.blit(self.game.image_coin, (10, 40))
        Text((self.game.gameDisplay, self.coin, text_interface), (False, 52, 46))
        
    def add_health(self, amount):
        if self.health < PLAYER_HEALTH:
            self.health += amount
            if self.health > PLAYER_HEALTH:
                self.health = PLAYER_HEALTH

    def update(self):
        self.get_keys()
        if self.moving == True or self.index != self.base_index:
            update_time_dependent(self)
        else:
            self.current_time += self.dt
        
        self.pos += self.vel * self.game.dt
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, "x")
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, "y")
        self.rect.center = self.hit_rect.center

        if self.health <= 0:
            self.kill()



class Mob(pygame.sprite.Sprite):
    def __init__(self, game, x ,y):
        # Setup
        self.game               = game
        self.groups             = self.game.all_sprites, self.game.mobs
        self._layer             = LAYER_MOB
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Settings
        self.maxhealth          = MOB_HEALTH
        self.health             = self.maxhealth
        self.target             = game.player
    
        # Surface
        self.rot = 0
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        
        self.index              = 0
        self.images             = self.game.mob_img.copy()
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

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < MOB_RADIUS:
                    if self.acc != -dist.normalize():
                        self.acc += dist.normalize()
                    else:
                        self.acc += vec(choice((self.acc.y, -self.acc.y)), choice((self.acc.x, -self.acc.x)))

    def update(self):
        self.update_angle()
        update_time_dependent(self)
    
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() <= DETECT_RADIUS**2:
            self.rot = target_dist.angle_to(vec(1, 0))
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
            Item(self.game, self.pos, choice(ITEM_DROPS))
            self.kill()


class Sword(pygame.sprite.Sprite):
    def __init__(self, game, character):
        # Setup
        self.game               = game
        self.groups             = self.game.all_sprites, self.game.sword
        self._layer             = LAYER_SWORD
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Settings
        self.character              = character
        self.hit                    = False
        self.spawn_time             = pygame.time.get_ticks()    
        self.character.last_slash   = self.spawn_time
        choice(self.game.sounds_voice["player_attack"]).play()

        # Surface
        self.rot                = self.character.rot
        self.pos                = vec(self.character.pos + SWORD_OFFSET.rotate(-self.rot))
        self.vel                = vec(1, 0).rotate(-self.rot) * SWORD_SPEED
        
        self.image              = pygame.transform.rotate(self.game.sword_img, self.rot-90)

        self.rect               = self.image.get_rect()
        self.rect.center        = self.pos
        self.hit_rect           = SWORD_HIT_RECT
        self.hit_rect.center    = self.rect.center

    def update(self):
        self.pos += self.vel * self.game.dt + self.character.vel * self.character.dt
        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos.x
        self.hit_rect.centery = self.pos.y
        if pygame.time.get_ticks() - self.spawn_time > SWORD_LIFETIME:
            self.kill()



class Obstacle(pygame.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        # Settings
        self.game   = game
        self.groups = self.game.walls
        self._layer = LAYER_WALL
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Surface
        self.rect = pygame.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = self.x * w
        self.rect.y = self.y * h



class Item(pygame.sprite.Sprite):
    def __init__(self, game, pos, type):
        # Setup
        self.game               = game
        self.groups             = self.game.all_sprites, self.game.items
        self._layer             = LAYER_ITEMS
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Settings
        self.type               = type

        # Surface
        self.pos                = pos
        
        self.image              = self.game.item_images[self.type][0]
    
        self.rect               = self.image.get_rect()
        self.rect.center        = self.pos
        self.hit_rect           = self.image.get_rect()
        self.hit_rect.center    = self.rect.center

        self.tween = tween.linear
        self.step = 0
        self.dir = 1

    def update(self):
        update_bobbing(self)




class Effect(pygame.sprite.Sprite):
    def __init__(self, game, pos, type):
        # Setup
        self.game               = game
        self.groups             = self.game.all_sprites, self.game.effects
        self._layer             = LAYER_EFFECTS
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Settings
        self.type               = type

        # Surface
        self.pos                = pos
        
        self.index              = 0
        self.images             = self.game.effect_images[self.type]
        self.image              = self.images[self.index]
    
        self.rect               = self.image.get_rect()
        self.rect.center        = self.pos
        self.hit_rect           = self.image.get_rect()
        self.hit_rect.center    = self.rect.center
    
        self.dt                 = game.dt
        self.current_time       = 0
        self.animation_time     = 0.10

    def update(self):
        update_time_dependent(self)
    
        if (self.index + 1) % len(self.images) == 0:
            self.kill()

g = Game()
while True:
    g.new()
    g.run()
