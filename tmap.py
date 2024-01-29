import pygame as pg
import pytmx
from settings import *

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect) 

class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())
        
        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * tilesize 
        self.height = self.tileheight * tilesize 

class TileMap:
    def __init__(self, filename):
     tilemap = pytmx.load_pygame(filename, pixelaplha= True)
     self.width = tilemap.width * tilemap.tilewidth
     self.height = tilemap.height * tilemap.tileheight
     self.tmxdata = tilemap
    
    def render(self, surface):
        til = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = til(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth, y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface

class camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0,0, width, height)
        self.width = width
        self.height = height
    
    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)
    

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)
    

    def update(self, target):
        x = -target.rect.centerx + int(width / 2)
        y = -target.rect.centery + int(height /2)

        #map limiter 
        x = min(0, x) #left side
        y = min(0, y) #top side
        x = max(-(self.width - width), x) #right side
        y = max(-(self.height - height), y)#bottom side
        self.camera = pg.Rect(x, y, self.width, self.height)
