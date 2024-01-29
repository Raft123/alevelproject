import pygame as pg
from random import uniform, choice, randint, random
from settings import *
from tmap import collide_hit_rect
import pytweening as pt
from itertools import chain
vec = pg.math.Vector2

def collision_walls(sprite, group, dir):
    if dir == "x":
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                    sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == "y":
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y      

class player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = player_layer
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.hit_rect = player_hit_rect
        self.hit_rect.center = self.rect.center
        self.vel = vec(0,0)
        self.pos = vec(x, y)
        self.rot = 0
        self.prev_shot = 0
        self.health = player_hp
        self.weapon = 'pistol'
        self.damaged = False
    
    def get_keys(self):
        self.rot_speed = 0
        self.vel = vec(0,0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = player_rotational_speed
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -player_rotational_speed
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel = vec(playerspeed, 0).rotate(-self.rot)   
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-playerspeed / 2, 0).rotate(-self.rot)   
        if keys[pg.K_SPACE]:
            self.shoot()

    def shoot(self):
            current = pg.time.get_ticks()
            if current - self.prev_shot > weapons[self.weapon]['bullet_fire_rate']:
                self.prev_shot = current
                dir = vec(1,0).rotate(-self.rot)
                pos = self.pos + b_offset.rotate(-self.rot)
                self.vel = vec(-weapons[self.weapon]['recoil'], 0 ).rotate(-self.rot)
                for i in range(weapons[self.weapon]['bullet_count']):
                    rspread = uniform(-weapons[self.weapon]['rspread'], weapons[self.weapon]['rspread'])
                    Bullet(self.game, pos, dir.rotate(rspread), weapons[self.weapon]['bullet_dmg'])
                    snd = choice(self.game.weapon_sounds[self.weapon])
                    if snd.get_num_channels() > 2:
                        snd.stop()
                    snd.play()
                MuzzleFlash(self.game, pos)

    def hit(self):
        self.damaged = True
        self.damaged_alpha = chain(damage_alpha * 2)
    
    def update(self):
        self.get_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        if self.damaged:
            try:
                self.image.fill((255, 0, 0, next(self.damaged_alpha)), special_flags=pg.BLEND_RGBA_MULT)
            except:
                self.damaged = False
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collision_walls(self, self.game.walls,"x")
        self.hit_rect.centery = self.pos.y
        collision_walls(self, self.game.walls,"y")
        self.rect.center = self.hit_rect.center
    def add_health(self, amount):
        self.health += amount
        if self.health > player_hp:
            self.health = player_hp

  
class Enemy(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = enemy_layer
        self.groups = game.all_sprites, game.enemies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.enemy_img.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.hit_rect = enemy_hit_rect.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x,y)
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.rect.center = self.pos
        self.rot = 0
        self.health = enemy_hp
        self.speed = choice(enemy_speeds)
        self.target = game.player

    def avoid_enemies(self):
        for enemies in self.game.enemies:
            if enemies != self:
                distance = self.pos - enemies.pos
                if 0 < distance.length() < avoid_area:
                    self.acc += distance.normalize()
    def update(self):
        target_distance = self.target.pos - self.pos
        if target_distance.length_squared() < detect_area**2:
            if random() < 0.002:
                choice(self.game.enemy_moan_sounds).play()
            self.rot = target_distance.angle_to(vec(1,0))
            self.image = pg.transform.rotate(self.game.enemy_img, self.rot)
            #self.rect = self.image.get_rect()
            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_enemies()
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
            self.hit_rect.centerx = self.pos.x
            collision_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collision_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center 
        if self.health  <= 0:
            choice(self.game.enemy_hit_sounds).play()
            self.kill()
            self.game.map_img.blit(self.game.splat, self.pos - vec(32, 32))
    
    def health_bar(self):
        if self.health > 70:
            healthc = green
        elif self.health > 45:
            healthc = yellow
        else:
            healthc = red
        width = int(self.rect.width * self.health / enemy_hp)
        self.healthbar = pg.Rect(0,0, width, 8)
        if self.health < enemy_hp:
            pg.draw.rect(self.image, healthc, self.healthbar)



class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir, damage):
        self._layer = bullet_layer
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        self.image = game.bullet_images[weapons[game.player.weapon]['bullet_size']]
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)
        self.rect.center = pos
        #rspread = uniform(-recoil_pattern, recoil_pattern)
        self.vel = dir * weapons[game.player.weapon]['bullet_speed'] * uniform(0.9, 1.1)
        self.spawn_time = pg.time.get_ticks()
        self.damage = damage

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > weapons[self.game.player.weapon]['bullet_life']:
            self.kill()


class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = wall_layer
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * tilesize
        self.rect.y = y * tilesize
        

class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        
class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = vfx_layer
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(10,40)
        self.image = pg.transform.scale(choice(game.gun_flashes), (size, size))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > flash_timing:
            self.kill()

class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type):
        self._layer = items_layer
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_imgs[type]
        self.rect = self.image.get_rect()
        self.type = type
        self.pos = pos
        self.rect.center = pos
        self.pt = pt.easeInOutSine
        self.step = 0
        self.dir = 1
    def update(self):
        #bobbing motion
        offset = bob_range * (self.pt(self.step / bob_range) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += bob_speed
        if self.step > bob_range:
            self.step = 0
            self.dir *= -1


