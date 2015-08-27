import pygame, sys, time, random
from pygame.locals import *

class Player(pygame.sprite.Sprite):
    velocity = 0
    target_droppable = None
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.paddle_flat = pygame.image.load('artwork/paddle.png')
        self.paddle_left = pygame.image.load('artwork/paddle_left_full.png')
        self.paddle_right = pygame.image.load('artwork/paddle_right_full.png')
        self.image = self.paddle_flat
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y

    def move(self, x):
        if x < 0:
            self.image = self.paddle_left
        if x > 0:
            self.image = self.paddle_right
        self.velocity = x

    def stop(self):
        self.image = self.paddle_flat
        self.velocity = 0

    def update(self):
        if self.target_droppable:
            if self.velocity == 0 and abs(self.x - self.target_droppable.x) > 10:
                if self.x > self.target_droppable.x:
                    self.move(-1)
                elif self.x < self.target_droppable.x:
                    self.move(1)
            elif self.velocity < 0:
                if self.x <= self.target_droppable.x:
                    self.stop()
            elif self.velocity > 0:
                if self.x >= self.target_droppable.x:
                    self.stop()

        if 100 <= self.x + self.velocity <= 600:
            if 0 < self.velocity < 15:
                self.velocity += .75
            if -15 < self.velocity < 0:
                self.velocity -= .75
            self.x += self.velocity
            self.rect.center = (self.x, self.y)

class Droppable(pygame.sprite.Sprite):
    def __init__(self, animations, x, y, velocity, points):
        pygame.sprite.Sprite.__init__(self)
        self.animations = animations
        self.animation_counter = 0
        self.image = self.animations[self.animation_counter]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.velocity = velocity
        self.points = points

    def update(self):
        if self.animation_counter < 3:
            self.animation_counter += 1
        else:
            self.animation_counter = 0
        self.image = self.animations[self.animation_counter]
        self.y += self.velocity
        self.rect.center = (self.x, self.y)
        if self.y >=650:
            self.image.fill(View.RED) # Kill animation needed

class Map(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([610,610])
        self.image.set_colorkey(View.TRANS)
        self.image.fill(View.TRANS)
        self.rect = self.image.get_rect()
        self.rect.center = (350,350)
        pygame.draw.rect(self.image, View.BLACK, (5,5,600,600), 3)

class ScoreCounter(pygame.sprite.Sprite):
    def __init__(self, display_text):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([150, 150])
        self.image.set_colorkey(View.TRANS)
        self.image.fill(View.TRANS)
        self.rect = self.image.get_rect()
        self.rect.center = (900,300)
        font = pygame.font.SysFont("Courier New", 50)
        text = font.render(str(display_text), 1, View.BLACK, View.WHITE)
        textpos = text.get_rect()
        textpos.centerx = 25
        self.image.blit(text, textpos)

class Spritesheet(object):
    def __init__(self, filename):
        self.sheet = pygame.image.load(filename).convert()

    def image_at(self, rectangle, colorkey = None):
        '''Load image from x, y, x offset, y offset'''
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0,0), rect)
        if colorkey is not None:
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def images_at(self, rectangles, colorkey = None):
        '''Load multiple images into a list, supple a list of rectangles'''
        return [self.image_at(rect, colorkey) for rect in rectangles]

class View:
    BLACK = (  0,   0,   0)
    WHITE = (255, 255, 255)
    BLUE =  (  0,   0, 255)
    GREEN = (  0, 255,   0)
    RED =   (255,   0,   0)
    TRANS = (  1,   1,   1)
    size =  [1280, 720]

    screen = None
    done = False
    clock = pygame.time.Clock()
    mouse_x = 0
    mouse_y = 0
    last_droppable_spawn = time.perf_counter()
    paddle = None
    score = 0
    user_playing = True

    all_sprites_group = pygame.sprite.Group()
    ship_group = pygame.sprite.Group()
    droppable_group = pygame.sprite.Group()
    score_counter = None

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode(self.size)
        self.paddle = Player(360, 600)
        self.paddle.add(self.all_sprites_group, self.ship_group)
        self.draw_map()
        self.draw_score()
        self.ping_sfx = pygame.mixer.Sound('ping.wav')
        self.miss_sfx = pygame.mixer.Sound('miss.wav')
        self.droppable_sprite_sheet = Spritesheet('artwork/droppable_sprite_sheet.png')

    def draw_map(self):
        basic_map = Map() 
        self.all_sprites_group.add(basic_map)

    def draw_score(self):
        if self.score_counter:
            self.score_counter.kill()
        self.score_counter = ScoreCounter(self.score)
        self.all_sprites_group.add(self.score_counter)

    def set_target_droppable(self):
        target = self.lowest_droppable()
        return target

    def lowest_droppable(self):
        current_lowest = None
        for droppable in self.droppable_group:
            if current_lowest:
                if droppable.y > current_lowest.y:
                    current_lowest = droppable
            else:
                current_lowest = droppable
        return current_lowest

    def spawn_droppable(self):
        random_x = random.randint(1,6)
        random_droppable = random.randint(1,10)
        if random_droppable <= 7: # 70% chance for regular speed droppable
            droppable = Droppable(
                self.droppable_sprite_sheet.images_at([
                    (0,0,50,50),
                    (50,0,50,50),
                    (100,0,50,50),
                    (150,0,50,50)],
                    colorkey = self.BLACK),
                random_x * 100,
                50,
                5,
                1)
        else: # 30% chance for fast droppable
            droppable = Droppable(
                self.droppable_sprite_sheet.images_at([
                    (0,50,50,50),
                    (50,50,50,50),
                    (100,50,50,50),
                    (150,50,50,50)],
                    colorkey = self.BLACK),
                random_x * 100,
                50,
                10,
                3)
        droppable.add(self.all_sprites_group, self.droppable_group)
        self.last_droppable_spawn = time.perf_counter()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP and event.button == 1:
                mouse_x,mouse_y = event.pos
                x = int(mouse_x / 200)
                y = int(mouse_y / 200)
            elif event.type == MOUSEBUTTONUP and event.button == 3:
                mouse_x,mouse_y = event.pos
                x = int(mouse_x / 200)
                y = int(mouse_y / 200)
            elif event.type == pygame.QUIT:
                self.quit()
            elif event.type == KEYDOWN and event.key == K_DOWN:
                    self.user_playing = True
                    self.paddle.stop()
                    self.paddle.target_droppable = None
            if self.user_playing:
                if event.type == KEYDOWN and event.key == K_UP:
                    self.user_playing = False
                elif event.type == KEYDOWN and event.key == K_LEFT:
                    self.paddle.move(-1)
                elif event.type == KEYDOWN and event.key == K_RIGHT:
                    self.paddle.move(1)
                elif event.type == KEYUP and event.key == K_LEFT or event.type == KEYUP and event.key == K_RIGHT:
                    self.paddle.stop()

    def update(self):
        if time.perf_counter() - self.last_droppable_spawn > 0.5:
            self.spawn_droppable()

        collision = pygame.sprite.spritecollideany(self.paddle, self.droppable_group)
        if collision:
            self.ping_sfx.play()
            self.score += collision.points
            self.draw_score()
            if collision == self.paddle.target_droppable:
                self.paddle.target_droppable = None
            collision.kill()

        miss = [droppable for droppable in self.droppable_group if droppable.y >= 650]
        if miss:
            for droppable in miss:
                self.miss_sfx.play()
                self.score -= droppable.points
                self.draw_score()
                if droppable == self.paddle.target_droppable:
                    self.paddle.target_droppable = None
                droppable.kill()

        if not self.user_playing:
            if not self.paddle.target_droppable and self.droppable_group:
                self.paddle.target_droppable = self.set_target_droppable()

        self.all_sprites_group.update()

    def display(self):
        self.screen.fill(self.WHITE)
        self.all_sprites_group.draw(self.screen)
        pygame.display.update()

    def quit(self):
        """Clean up assets and unload graphic objects"""
        pygame.quit()
        sys.exit()

def main():
    """simple game loop"""
    view = View()
    while 1:
        view.handle_events()
        view.update()
        view.display()
    view.quit()
main()