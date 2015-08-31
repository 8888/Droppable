import pygame, sys, time, random
from pygame.locals import *

class Player(pygame.sprite.Sprite):
    velocity = 0
    max_velocity = 15
    target_droppable = None
    animation_time = 10 #update cycles
    current_animation_cycles = 0
    def __init__(self, flat_animations, right_animations, left_animations, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.paddle_flat = flat_animations
        self.paddle_right = right_animations
        self.paddle_left = left_animations
        self.animation_counter = 0
        self.animation_row = self.paddle_flat
        self.image = self.animation_row[self.animation_counter]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y

    def move(self, x):
        '''Sets the initial velocity and direction to begin movement'''
        if x < 0:
            self.animation_row = self.paddle_left
        if x > 0:
            self.animation_row = self.paddle_right
        self.velocity = x

    def stop(self):
        '''Stops the paddle at the current location'''
        self.animation_row = self.paddle_flat
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
            if 0 < self.velocity < self.max_velocity:
                self.velocity += .75
            if -self.max_velocity < self.velocity < 0:
                self.velocity -= .75
            self.x += self.velocity
            self.rect.center = (self.x, self.y)

        if self.current_animation_cycles == self.animation_time:
            if self.animation_counter < 3:
                self.animation_counter += 1
            else:
                self.animation_counter = 0
            self.image = self.animation_row[self.animation_counter]
            self.current_animation_cycles = 0
        else:
            self.current_animation_cycles += 1

class Droppable(pygame.sprite.Sprite):
    distance_to_bottom = 650
    animation_time = 10 #update cycles
    current_animation_cycles = 0
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
        if self.current_animation_cycles == self.animation_time:
            if self.animation_counter < 3:
                self.animation_counter += 1
            else:
                self.animation_counter = 0
            self.image = self.animations[self.animation_counter]
            self.current_animation_cycles = 0
        else:
            self.current_animation_cycles += 1
        self.y += self.velocity
        self.rect.center = (self.x, self.y)
        self.distance_to_bottom = self.time_to_bottom()
        if self.y >=650:
            self.image.fill(View.RED) # Kill animation needed

    def time_to_bottom(self):
        '''Returns the amount of update cycles it takes to reach the bottom'''
        return ((650 - self.y) / self.velocity)
        
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
    def __init__(self, score, combo, best_combo, bombs_available, freeze_available):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([400, 400])
        self.image.set_colorkey(View.TRANS)
        self.image.fill(View.TRANS)
        self.rect = self.image.get_rect()
        self.rect.center = (900,300)
        font = pygame.font.SysFont("Courier New", 24)
        line1 = font.render("Score: {}".format(str(score)), 1, View.BLACK, View.WHITE)
        line2 = font.render("Combo: {}".format(str(combo)), 1, View.BLACK, View.WHITE)
        line3 = font.render("Best Combo: {}".format(str(best_combo)), 1, View.BLACK, View.WHITE)
        line4 = font.render("Bombs Available: {}".format(str(bombs_available)), 1, View.BLACK, View.WHITE)
        line5 = font.render("Freeze Available: {}".format(str(freeze_available)), 1, View.BLACK, View.WHITE)
        self.image.blit(line1, [0,0,120,30])
        self.image.blit(line2, [0,30,120,30])
        self.image.blit(line3, [0,60,120,30])
        self.image.blit(line4, [0,90,120,30])
        self.image.blit(line5, [0,120,120,30])

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
        '''Load multiple images into a list, supply a list of rectangles'''
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
    combo = 0
    best_combo = 0
    user_playing = True
    bombs_available = 0
    freeze_available = 0
    next_freeze = 25

    all_sprites_group = pygame.sprite.Group()
    droppable_group = pygame.sprite.Group()
    score_counter = None

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode(self.size)
        self.draw_map()
        self.draw_score()
        self.ping_sfx = pygame.mixer.Sound('ping.wav')
        self.miss_sfx = pygame.mixer.Sound('miss.wav')
        self.droppable_sprite_sheet = Spritesheet('artwork/droppable_sprite_sheet.png')
        self.paddle_sprite_sheet = Spritesheet('artwork/paddle_sprite_sheet.png')
        self.paddle = Player(
            self.paddle_sprite_sheet.images_at([
                (0,0,100,30),
                (100,0,100,30),
                (200,0,100,30),
                (300,0,100,30)],
                colorkey = self.BLACK),
            self.paddle_sprite_sheet.images_at([
                (0,28,100,31),
                (100,28,100,31),
                (200,28,100,31),
                (300,28,100,31)],
                colorkey = self.BLACK),
            self.paddle_sprite_sheet.images_at([
                (0,59,100,30),
                (100,59,100,30),
                (200,59,100,30),
                (300,59,100,30)],
                colorkey = self.BLACK),
            360, 
            600)
        self.paddle.add(self.all_sprites_group)

    def draw_map(self):
        '''Draws the valid playing field'''
        basic_map = Map() 
        self.all_sprites_group.add(basic_map)

    def draw_score(self):
        '''Draws the player's current score'''
        if self.score_counter:
            self.score_counter.kill()
        self.score_counter = ScoreCounter(
            self.score,
            self.combo,
            self.best_combo,
            self.bombs_available,
            self.freeze_available) 
        self.all_sprites_group.add(self.score_counter)

    def set_target_droppable(self):
        '''Sets the player sprite's target droppable when in AI mode'''
        target = self.soonest_landing_attainable_droppable()
        return target

    def lowest_droppable(self):
        '''Returns the droppable sprite with the highest Y value (closest to the bottom)'''
        current_lowest = None
        for droppable in self.droppable_group:
            if current_lowest:
                if droppable.y > current_lowest.y:
                    current_lowest = droppable
            else:
                current_lowest = droppable
        return current_lowest

    def soonest_landing_attainable_droppable(self):
        '''Returns the attainable droppable sprite that will reach the bottom soonest'''
        current_soonest = None
        for droppable in self.droppable_group:
            if droppable.distance_to_bottom > self.time_to_point(droppable):
                if current_soonest:
                    if droppable.distance_to_bottom < current_soonest.distance_to_bottom:
                        current_soonest = droppable
                else:
                    current_soonest = droppable 
        return current_soonest

    def time_to_point(self, droppable):
        '''Returns the number of update cycles it takes the paddle to reach a given sprites point'''
        return abs((droppable.x - self.paddle.x) / self.paddle.max_velocity)

    def spawn_droppable(self):
        '''Spawns a new droppable sprite after a set time interval'''
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

    def drop_bomb(self):
        for droppable in self.droppable_group:
            self.score += droppable.points
            droppable.kill()
        self.bombs_available -= 1
        self.draw_score()

    def freeze_droppables(self):
        for droppable in self.droppable_group:
            droppable.velocity /= 2
        self.freeze_available -= 1
        self.draw_score()

    def handle_events(self):
        '''Handles all user input'''
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
            elif event.type == KEYDOWN and event.key == K_UP:
                    if self.user_playing:
                        self.user_playing = False
                    else:
                        self.user_playing = True
                        self.paddle.stop()
                        self.paddle.target_droppable = None
            if self.user_playing:
                if event.type == KEYDOWN and event.key == K_LEFT:
                    self.paddle.move(-1)
                elif event.type == KEYDOWN and event.key == K_RIGHT:
                    self.paddle.move(1)
                elif event.type == KEYUP and event.key == K_LEFT or event.type == KEYUP and event.key == K_RIGHT:
                    self.paddle.stop()
                elif event.type == KEYDOWN and event.key == K_1 and self.bombs_available:
                    self.drop_bomb()
                elif event.type == KEYDOWN and event.key == K_2 and self.freeze_available:
                    self.freeze_droppables()

    def update(self):
        '''Updates game content and state'''
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
            self.combo += 1
            if self.combo > self.best_combo:
                self.best_combo = self.combo
            if self.combo % 10 == 0:
                self.bombs_available += 1

        miss = [droppable for droppable in self.droppable_group if droppable.y >= 650]
        if miss:
            for droppable in miss:
                self.miss_sfx.play()
                self.score -= droppable.points
                self.draw_score()
                if droppable == self.paddle.target_droppable:
                    print ("missed my target captain!!")
                    self.paddle.target_droppable = None
                droppable.kill()
                self.combo = 0

        if not self.user_playing:
            total_droppale_points = 0
            for droppable in self.droppable_group:
                total_droppale_points += droppable.points
            if total_droppale_points > 6 and self.bombs_available:
                self.drop_bomb()
            if self.droppable_group:
                self.paddle.target_droppable = self.set_target_droppable()

        if self.score >= self.next_freeze:
            self.freeze_available += 1
            self.next_freeze += 25
            self.draw_score()

        self.all_sprites_group.update()

    def display(self):
        '''Draw all sprites onto the visible screen'''
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