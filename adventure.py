import pygame, pytmx
from os import path
from pytmx.util_pygame import load_pygame
pygame.init()
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
black = (0, 0, 0)
white = (255, 255, 255)
screen_width  = 1024
screen_height = 640
screen = pygame.display.set_mode([screen_width, screen_height])
pygame.display.set_caption('Adventurer')
clock = pygame.time.Clock()
tilesize = 128
platform_img = [pygame.image.load('platform'+str(i)+'.png') for i in range(1, 10)]
right_player_img = [pygame.image.load('pwalk'+str(i)+'.png') for i in range(1, 12)]
left_player_img = [pygame.transform.flip(right_player_img[i], 1, 0) for i in range(0, 11)]
player_jump_img = pygame.image.load('pjump.png')
player_stand_img = pygame.image.load('pstand.png')
waterimg=[pygame.image.load('w'+str(i)+'.png') for i in range(1,18)]

class Player(pygame.sprite.Sprite):
   def __init__(self, game, x, y):
      self.groups = game.all_sprites
      pygame.sprite.Sprite.__init__(self, self.groups)
      self.game = game
      self.image = player_stand_img
      self.image = pygame.transform.scale(self.image, (47, 64))
      self.rect = self.image.get_rect()
      self.rect.x = x 
      self.rect.y = y 
      self.vx, self.vy =0, 0
      self.right_walk_count = 0
      self.left_walk_count = 0
      self.no_of_frames = len(right_player_img) * 2
      self.frames_per_second = 2
      self.left_faced = 0
      self.right_faced =1

   def gravity(self):
      if self.vy == 0:
         self.vy = 5
      else:
         self.vy += 0.35

   def jump(self):
      self.rect.y += 2
      hits = pygame.sprite.spritecollide(self, self.game.platforms, 0)
      self.rect.y -= 2
      if hits or self.rect.bottom >= screen_height:
         self.vy = - 12

   def update(self):
      self.vx =0
      self.gravity()
      keys = pygame.key.get_pressed()
      if keys[pygame.K_LEFT]:
         self.left_faced =1
         self.right_faced =0
         self.vx = -5
         if self.left_walk_count + 1 < self.no_of_frames:
            self.image = left_player_img[self.left_walk_count // self.frames_per_second]
            self.image = pygame.transform.scale(self.image, (47, 64))
            self.left_walk_count +=1
         else:
            self.left_walk_count = 0
      elif keys[pygame.K_RIGHT]:
         self.left_faced = 0
         self.right_faced = 1
         self.vx = 5
         if self.right_walk_count + 1 < self.no_of_frames:
            self.image = right_player_img[self.right_walk_count // self.frames_per_second]
            self.image = pygame.transform.scale(self.image, (47, 64))
            self.right_walk_count +=1
         else:
            self.right_walk_count = 0
      else:
         if self.right_faced:
            self.image = player_stand_img
            self.image = pygame.transform.scale(self.image, (47, 64))
         if self.left_faced:
            self.image = player_stand_img
            self.image = pygame.transform.flip(self.image, 1, 0)
            self.image = pygame.transform.scale(self.image, (47, 64))
      if keys[pygame.K_UP]:
         self.jump()
      if self.vy < 0 and self.right_faced:
         self.image = player_jump_img
         self.image = pygame.transform.scale(self.image, (47, 64))
      if self.vy < 0 and self.left_faced:
         self.image = player_jump_img
         self.image = pygame.transform.flip(self.image, 1, 0)
         self.image = pygame.transform.scale(self.image, (47, 64))
      self.rect.x += self.vx
      hits = pygame.sprite.spritecollide(self, self.game.platforms, 0)
      for hit in hits:
         if self.vx > 0:
            self.rect.right = hit.rect.left
         elif self.vx < 0:
            self.rect.left = hit.rect.right
         self.vx = 0
      self.rect.y +=self.vy
      hits1 = pygame.sprite.spritecollide(self, self.game.platforms, 0)
      for hit in hits1:
         if self.vy > 0:
            self.rect.bottom = hit.rect.top
         elif self.vy < 0:
            self.rect.top = hit.rect.bottom
         self.vy = 0
      if self.rect.left <= 0:
         self.rect.left = 0
      if self.rect.right >= self.game.map.width - 20:
         self.rect.right = self.game.map.width - 20
      if self.rect.top <= 0:
         self.rect.top = 0
         self.vy = 0
      if self.rect.bottom >= screen_height:
         self.rect.bottom = screen_height

   def nextlevel(self):
      if self.rect.right >= self.game.map.width - 20:
         self.kill()
         return 1
         
class Platform(pygame.sprite.Sprite):
   def __init__(self, game, x, y, w, h):
      self.groups =  game.platforms
      pygame.sprite.Sprite.__init__(self, self.groups)
      self.rect  = pygame.Rect(x, y, w, h)
      self.rect.x = x 
      self.rect.y = y 

class MovingPlatform(pygame.sprite.Sprite):
   def __init__(self, game, x, y, vx = 0, vy = 0, leftlimit = 0, rightlimit = 0, toplimit = 0, bottomlimit = 0):
      self.groups = game.all_sprites, game.platforms
      pygame.sprite.Sprite.__init__(self, self.groups)
      self.game = game
      self.image = platform_img[8]
      self.image = pygame.transform.scale(self.image, (tilesize, tilesize))
      self.rect  = self.image.get_rect()
      self.rect.x = x 
      self.rect.y = y 
      self.leftlimit = x - leftlimit * tilesize
      self.rightlimit = x + rightlimit * tilesize + tilesize
      self.vx = vx
      self.toplimit = y - toplimit * tilesize
      self.bottomlimit = y + bottomlimit * tilesize + tilesize
      self.vy = vy

   def update(self):
         self.rect.x += self.vx
         hits = pygame.sprite.spritecollide(self.game.player, self.game.platforms, 0)
         for hit in hits:            
            if self.vx < 0:
              self.game.player.rect.right =  hit.rect.left 
            elif self.vx > 0:
               self.game.player.rect.left = hit.rect.right
         if self.rect.right >= self.rightlimit:
            self.vx  *= -1
         elif self.rect.left <= self.leftlimit:
            self.vx *= -1
         self.rect.y += self.vy
         hits1 = pygame.sprite.spritecollide(self.game.player, self.game.platforms, 0)
         for hit in hits1:         
            if self.vy < 0:              
                self.game.player.rect.bottom = hit.rect.top 
            elif self.vy > 0:
                self.game.player.rect.top = hit.rect.bottom 
         if self.rect.bottom >= self.bottomlimit:
            self.vy  *= -1
         elif self.rect.top <= self.toplimit:
            self.vy *= - 1
         hits2 = pygame.sprite.collide_rect(self.game.player, self)
         if self.vy == 0 and hits2:
            self.rect.y = self.game.player.rect.bottom
            
         
class Water(pygame.sprite.Sprite):
   def __init__(self, game, x, y):
      self.groups = game.waters, game.all_sprites
      pygame.sprite.Sprite.__init__(self, self.groups)
      self.image = waterimg[0]
      self.rect = self.image.get_rect()
      self.rect.x = x
      self.rect.y = y
      self.wc = 0
      
   def update(self):
      if self.wc + 1 < 34:
         self.image = waterimg[self.wc // 2]
         self.wc += 1
      else:
         self.wc = 0
         
class TiledMap:
   def __init__(self, filename):
      tm = pytmx.load_pygame(filename, pixelalpha = True)
      self.width = tm.width * tm.tilewidth
      self.height = tm.height * tm.tileheight
      self.tmxdata = tm
      
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
   
class Map:
   def __init__(self, filename):
      self.data = [ ]
      with open(filename, 'r+') as f:
         for line in f:
            self.data.append(line)
      self.tilewidth = len(self.data[0])
      self.tileheight = len(self.data)
      self.width = self.tilewidth * tilesize
      self.height = self.tileheight * tilesize

class Camera:
   def __init__(self, width, height):
      self.camera = pygame.Rect(0, 0, width, height)
      self.width = width
      self.height = height

   def apply(self,entity):
      return entity.rect.move(self.camera.topleft)

   def apply_rect(self, rect):
      return rect.move(self.camera.topleft)
   
   def update(self, target):
      x = -target.rect.x + int(screen_width / 2)
      y = -target.rect.y +int(screen_height / 2)
      x = min(0, x)
      y = min(0, y)
      x = max(-(self.width - screen_width), x)
      y = max(-(self.height - screen_height), y)
      self.camera = pygame.Rect(x, y, self.width, self.height)
class Game:
    def __init__(self):
            pass

##    def loadmap(self, filename = 'level1.tmx'):
##       print(mapname)
##       self.map = TiledMap(filename)
##       self.map_img  = self.map.make_map()
##       self.map_rect = self.map_img.get_rect()

    def new(self, mapname = "level1.tmx"):
##        self.loadmap()
        print(mapname)
        self.map = TiledMap(mapname)
        self.map_img  = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.waters = pygame.sprite.Group()
        self.camera = Camera(self.map.width, self.map.height)
        for tile_object in self.map.tmxdata.objects:
           if tile_object.name == 'player':
              self.player = Player(self, tile_object.x, tile_object.y)
           if tile_object.name == 'platform':
              Platform(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
           if tile_object.name == 'mplatformx11':
              MovingPlatform(self, tile_object.x, tile_object.y, vx = 2, vy = 0, leftlimit = 1, rightlimit = 1, toplimit = 0, bottomlimit = 0)
           if tile_object.name == 'mplatformx12':
              MovingPlatform(self, tile_object.x, tile_object.y, vx = 2, vy = 0, leftlimit = 1, rightlimit = 2, toplimit = 0, bottomlimit = 0) 
           if tile_object.name == 'mplatformy':
              MovingPlatform(self, tile_object.x, tile_object.y)
           if tile_object.name == 'mplatformxy11':
              MovingPlatform(self, tile_object.x, tile_object.y, vx = - 2, vy = 2, leftlimit = 1, rightlimit = 1, toplimit = 1, bottomlimit = 1)

           if tile_object.name == 'water':
              Water(self, tile_object.x, tile_object.y)
              
    def events(self):
        for event in pygame.event.get():            
            if event.type==pygame.QUIT:
                pygame.quit()
                quit()

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)
        if self.player.nextlevel():
           self.new(mapname = "level2.tmx")
           
    def draw(self):
       screen.blit(self.map_img, (self.camera.apply_rect(self.map_rect)))
       for sprite in self.all_sprites:
          screen.blit(sprite.image, self.camera.apply(sprite))
       pygame.display.flip()

    def run(self):
        while 1:
            clock.tick(60)
            self.events()
            self.update()
            self.draw()
g = Game()
while g.run:
    g.new()
    g.run()
