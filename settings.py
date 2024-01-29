import pygame as pg
vec = pg.math.Vector2

# colors
white = (255, 255, 255)
black = (0, 0, 0)
darkgrey = (40, 40, 40)
lightgrey = (100, 100, 100)
green = (0, 255, 0)
red = (255, 0, 0)
yellow = (255, 255, 0)
brown = (106,55, 5)


# game settings
width = 1280    
height = 768
fps = 60
title = "farmyard rush"
bgc = brown

# tile settings
tilesize = 64
gridwidth = width/ tilesize
gridheight = height / tilesize  


wall_img = 'browntile.png'

#player settings
playerspeed = 250
player_hp = 100
player_rotational_speed = 200
player_img = 'adventureman.png'
player_hit_rect = pg.Rect(0 , 0, 20, 20) 
b_offset = vec(30, 10)


#gun settings
bullet_img = 'bullet.png'
weapons = {}
weapons['pistol'] = {'bullet_speed': 500,
                     'bullet_life': 1000,
                     'bullet_fire_rate': 150,
                     'recoil': 5,
                     'rspread': 5,
                     'bullet_dmg': 10,
                     'bullet_size': 'lg',
                     'bullet_count': 1}

weapons['shotgun'] = {'bullet_speed': 400,
                      'bullet_life': 500,
                      'bullet_fire_rate': 900,
                      'recoil': 300,
                      'rspread': 20,
                      'bullet_dmg': 5,
                      'bullet_size': 'sm',
                      'bullet_count': 12}

bullet_speed = 600
bullet_life = 1000
bullet_fire_rate = 150
recoil = 180
recoil_pattern = 5 
bullet_dmg = 5

#Enemy settings
enemy_img = 'blueguyhold.png'
enemy_speeds = [180, 110, 150, 95, 150]
enemy_hit_rect = pg.Rect(0, 0, 20, 20)
enemy_hp = 100
enemy_dmg = 5
enemy_knock = 15
avoid_area = 40
detect_area = 350

#FX
muzzle_flashes = ['whitePuff05.png', 'whitePuff06.png','whitePuff07.png','whitePuff08.png']
flash_timing = 40
splat = 'splat.png'
damage_alpha = [i for i in range(0,255, 25)]
#Layers 
player_layer = 2
wall_layer = 1
bullet_layer = 3
enemy_layer = 2
vfx_layer = 4
items_layer = 1

#items
item_imgs = {'health': 'medkit.png',
             'shotgun': 'obj_shotgun.png'}
medkit_amount = 30
bob_range = 15
bob_speed = 0.7 

#sounds
BG_MUSIC = 'bgm.ogg'
PLAYER_HIT_SOUNDS = ['phit/8.wav', 'phit/9.wav', 'phit/10.wav', 'phit/11.wav']
ENEMY_MOAN_SOUNDS = ['brains2.wav', 'brains3.wav', 'enemy-roar1.wav', 'enemy-roar2.wav',
                      'enemy-roar3.wav', 'enemy-roar5.wav', 'enemy-roar6.wav', 'enemy-roar7.wav']
ENEMY_HIT_SOUNDS = ['splat.wav']
WEAPON_SOUNDS = {'pistol': ['pistol.wav'],
                     'shotgun': ['shotgun.wav'],
}
EFFECTS_SOUNDS = {'level_start': 'level_start.wav',
                  'health_up': 'medkit.wav',
                  'gun_pickup': 'gun_pickup.wav'}
