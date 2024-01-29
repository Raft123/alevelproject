import pygame as pg
import sys
from random import choice, random
from os import path 
from settings import *
from sprites import *
from tmap import *

#GUI functions
def draw_player_hp(surface, x, y, percentage):
    if percentage < 0:
        percentage = 0
    b_length = 100
    b_height = 25
    fill = percentage * b_length
    outline_rect = pg.Rect(x, y, b_length, b_height)
    fill_rect = pg.Rect(x, y, fill, b_height)
    if percentage  > 0.70:
        pcolor = green
    elif percentage > 0.45:
        pcolor = yellow
    else:
        pcolor = red
    pg.draw.rect(surface, pcolor, fill_rect)
    pg.draw.rect(surface, white, outline_rect, 3)


class Game:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 1, 2048)
        pg.init()
        self.screen = pg.display.set_mode((width, height))
        pg.display.set_caption(title)
        self.clock = pg.time.Clock()
        self.load_data()

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
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
        self.screen.blit(text_surface, text_rect)

    
    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        snd_folder = path.join(game_folder, 'snd')
        music_folder = path.join(game_folder, 'music')
        self.map_folder = path.join(game_folder, 'maps')
        self.title_font = path.join(img_folder, 'ENEMY.TTF')
        self.hud_font = path.join(img_folder, 'Impacted2.0.ttf')
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))
        self.player_img = pg.image.load(path.join(img_folder, player_img)).convert_alpha()
        self.bullet_images = {}
        self.bullet_images['lg'] = pg.image.load(path.join(img_folder, bullet_img)).convert_alpha()
        self.bullet_images['sm'] = pg.transform.scale(self.bullet_images['lg'], (10,10))
        self.enemy_img = pg.image.load(path.join(img_folder, enemy_img)).convert_alpha()
        self.wall_img = pg.image.load(path.join(img_folder, wall_img)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (tilesize,tilesize))
        self.splat = pg.image.load(path.join(img_folder, splat)).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (64, 64))
        self.gun_flashes = []
        for img in muzzle_flashes:
            self.gun_flashes.append(pg.image.load(path.join(img_folder, img)).convert_alpha())
        self.item_imgs = {}
        for item in item_imgs:
            self.item_imgs[item] = pg.image.load(path.join(img_folder, item_imgs[item])).convert_alpha()
    
           # Sound loading
        pg.mixer.music.load(path.join(music_folder, BG_MUSIC))
        self.effects_sounds = {}
        for type in EFFECTS_SOUNDS:
            self.effects_sounds[type] = pg.mixer.Sound(path.join(snd_folder, EFFECTS_SOUNDS[type]))
        self.weapon_sounds = {}
        for weapon in WEAPON_SOUNDS:
            self.weapon_sounds[weapon] = []
            for snd in WEAPON_SOUNDS[weapon]:
                s = pg.mixer.Sound(path.join(snd_folder, snd))
                s.set_volume(0.2)
                self.weapon_sounds[weapon].append(s)
        self.enemy_moan_sounds = []
        for snd in ENEMY_MOAN_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(0.2)
            self.enemy_moan_sounds.append(s)
        self.player_hit_sounds = []
        for snd in PLAYER_HIT_SOUNDS:
            self.player_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))
        self.enemy_hit_sounds = []
        for snd in ENEMY_HIT_SOUNDS:
            self.enemy_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))

    def new(self):
        # initializes all variables and sets up for a new game
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.map = TileMap(path.join(self.map_folder, 'tmap1.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        #for row, tiles in enumerate(self.map.data):
        #    for col, tile in enumerate(tiles):
        #        if tile == "1":
        #            Wall(self, col, row)
        #        if tile == "E":
        #            Enemy(self,col,row)
        #       if tile == "P":
        #           self.player = player(self, col, row)
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width /2, 
                             tile_object.y + tile_object.height /2)
            if tile_object.name == 'player':
                self.player = player(self, obj_center.x, obj_center.y)
            if tile_object.name == 'enemy':
                Enemy(self, obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width , tile_object.height)
            if tile_object.name in ['health', 'shotgun']:
                Item(self, obj_center, tile_object.name)
        self.camera = camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.paused = False
        self.effects_sounds['level_start'].play()

    
    def run(self):
        self.playing = True
        pg.mixer.music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(fps) / 1000
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # updates the game loop
        self.all_sprites.update()
        self.camera.update(self.player)

        #game over 
        if len(self.enemies) == 0:
            self.playing = False
        # player hits item
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == 'health' and self.player.health < player_hp:
                hit.kill()
                self.effects_sounds['health_up'].play()
                self.player.add_health(medkit_amount)
            if hit.type == 'shotgun':
                hit.kill()
                self.effects_sounds['gun_pickup'].play()
                self.player.weapon = 'shotgun'
        
        # enemy hits player
        hits = pg.sprite.spritecollide(self.player, self.enemies, False, collide_hit_rect)
        for hit in hits:
            if random() < 0.7:
                choice(self.player_hit_sounds).play()
            self.player.health -= enemy_dmg
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False
        
        if hits:
            self.player.hit()
            self.player.pos += vec(enemy_knock, 0).rotate(-hits[0].rot)
        # bullets hit enemies
        hits = pg.sprite.groupcollide(self.enemies, self.bullets, False, True)
        for enemy in hits:
            #hit.health -= weapons[self.player.weapon]['bullet_dmg'] * len(hits[hit])
            for b in hits[enemy]:
                enemy.health -= bullet_dmg
            enemy.vel = vec(0,0)
    def draw_grid(self):
        for x in range(0, width, tilesize):
            pg.draw.line(self.screen, lightgrey, (x, 0), (x, height))
        for y in range(0, height, tilesize):
            pg.draw.line(self.screen, lightgrey, (0, y), (width, y))

    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        #self.screen.fill(bgc)
        #self.draw_grid()
        for sprite in self.all_sprites:
            if isinstance(sprite, Enemy):
                sprite.health_bar()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                pg.draw.rect(self.screen, yellow, self.camera.apply_rect(sprite.hit_rect), 1)
                if self.draw_debug:
                    for wall in self.walls:
                        pg.draw.rect(self.screen, yellow, self.camera.apply_rect(wall.rect), 1)

        #pg.draw.rect(self.screen,white, self.player.hit_rect , 2)    
        #GUI functions
        draw_player_hp(self.screen, 5, 5, self.player.health / player_hp)
        self.draw_text('Enemies: {}'.format(len(self.enemies)), self.hud_font, 30, white , width - 10, 10, align = "ne")
        if self.paused:
            self.screen.blit(self.dim_screen, (0,0))
            self.draw_text("Paused", self.title_font, 105, green, width / 2, height / 2, align="center")
        pg.display.flip()


    def events(self):
        # events function 
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit() 
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_l:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_p:
                    self.paused = not self.paused
    
    def show_start_screen(self):
        pass

    def show_go_screen(self):
        self.screen.fill(black)
        self.draw_text("GAME OVER", self.title_font, 100, red, width / 2, height / 2, align = "center")
        self.draw_text("Press a key to start", self.title_font, 75, white, width / 2, height * 3 / 4, align = "center")
        pg.display.flip()
        self.wait_for_key()
    def wait_for_key(self):
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(fps)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False
# creates the game object
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()  

 