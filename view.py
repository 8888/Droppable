import pygame, sys, time, random
from pygame.locals import *

class Player(pygame.sprite.Sprite):
    velocity = 0
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
        if 120 <= self.x + self.velocity <= 580:
            if 0 < self.velocity < 15:
                self.velocity += .75
            if -15 < self.velocity < 0:
                self.velocity -= .75
            self.x += self.velocity
            self.rect.center = (self.x, self.y)

class Droppable(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([40, 40])
        self.image.set_colorkey(View.TRANS)
        self.image.fill(View.TRANS)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        pygame.draw.circle(
            self.image,
            View.GREEN,
            (20, 20),
            20,
            0)
        self.x = x
        self.y = y
        self.missed = False

    def update(self):
        if self.missed:
            self.kill()
        self.y += 5
        self.rect.center = (self.x, self.y)
        if self.y >=650:
            self.image.fill(View.RED)
            self.missed = True

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

class View:
    BLACK = (  0,   0,   0)
    WHITE = (255, 255, 255)
    BLUE =  (  0,   0, 255)
    GREEN = (  0, 255,   0)
    RED =   (255,   0,   0)
    TRANS = (  1,   1,   1)
    size = [1280, 720]

    screen = None
    done = False
    clock = pygame.time.Clock()
    mouse_x = 0
    mouse_y = 0
    last_droppable_spawn = time.perf_counter()
    paddle = None
    score = 0

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

    def draw_map(self):
        basic_map = Map() 
        self.all_sprites_group.add(basic_map)

    def draw_score(self):
        if self.score_counter:
            self.score_counter.kill()
        self.score_counter = ScoreCounter(self.score)
        self.all_sprites_group.add(self.score_counter)        

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
            elif event.type == KEYDOWN and event.key == K_LEFT:
                self.paddle.move(-1)
            elif event.type == KEYDOWN and event.key == K_RIGHT:
                self.paddle.move(1)
            elif event.type == KEYUP and event.key == K_LEFT or event.type == KEYUP and event.key == K_RIGHT:
                self.paddle.stop()

    def update(self):
        if time.perf_counter() - self.last_droppable_spawn > 2.0:
            random_x = random.randint(1,6)
            droppable = Droppable(random_x * 100, 100)
            droppable.add(self.all_sprites_group, self.droppable_group)
            self.last_droppable_spawn = time.perf_counter()

        collision = pygame.sprite.spritecollideany(self.paddle, self.droppable_group)
        if collision:
            self.ping_sfx.play()
            self.score += 1
            self.draw_score()
            collision.kill()

        miss = [droppable for droppable in self.droppable_group if droppable.y >= 650]
        if miss:
            self.miss_sfx.play()
            self.score -= 1
            self.draw_score()

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