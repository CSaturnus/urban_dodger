import pygame
import random
import asyncio

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 500, 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 120

WHITE = (255, 255, 255)
BLACK = (0,0,0)
GREEN = (0, 255, 0)

car_front_sprite = pygame.image.load('assets/sprite/car_front.png')
car_side_sprite = pygame.image.load('assets/sprite/car_side.png')
exclamation_mark_sprite = pygame.image.load('assets/sprite/exclamation_mark.png')
arrow_sprite = pygame.image.load('assets/sprite/arrow.png')
brick_stone_sprite = pygame.image.load('assets/sprite/brick_stone.png')

alarm = pygame.mixer.Sound('assets/music/8-bit-alarm.ogg')
pygame.mixer.Sound.set_volume(alarm, 0.05)

car_engine = pygame.mixer.Sound('assets/music/car_engine.ogg')
pygame.mixer.Sound.set_volume(car_engine, 0.3)

music = pygame.mixer.music.load('assets/music/The-return.ogg')

class Brick():
    def __init__(self, screen, sprite, posx):
        self.screen = screen

        self.posx = posx
        self.posy = -50

        self.speed_posy = 0
        self.acceleration = 0.03
        self.width = 75
        self.height = 50
        self.sprite = sprite
        self.rect = self.sprite.get_rect(center=(self.posx + self.width//2, self.posy+ self.height//2)) 

        self.terminate = False

    def fall(self):
        self.speed_posy += self.acceleration
        self.posy += self.speed_posy
        self.rect = self.sprite.get_rect(center=(self.posx + self.width//2, self.posy+ self.height//2)) 
        if self.posy > HEIGHT + 100:
            self.terminate = True

    def display(self):
        self.screen.blit(self.sprite, self.rect)

class CarSide():
    def __init__(self, screen, sprite, left_or_right = 0):
        self.screen = screen
        self.posy = HEIGHT - 300

        self.width = 250
        self.height = 250

        self.left_or_right = left_or_right

        if left_or_right == 1: # going right to left
            self.speed = -7
            self.sprite = sprite
            self.posx = WIDTH
        
        else:
            self.sprite = pygame.transform.flip(sprite, True, False)
            self.speed = 7
            self.posx = -self.width


        self.rect = self.sprite.get_rect(center=(self.posx + self.width//2, self.posy+ self.height//2))
        if self.left_or_right == 1:
            self.rect_hit = pygame.Rect(self.posx, self.posy, self.width - 20, self.height - 15)

        self.terminate = False

    def car_approaching(self):
        
        self.posx += self.speed
        self.rect = self.sprite.get_rect(center=(self.posx + self.width//2, self.posy+ self.height//2))
        if self.left_or_right == 1:
            self.rect_hit = pygame.Rect(self.posx + 20, self.posy + 10, self.width - 20, self.height - 10)
        else:
            self.rect_hit = pygame.Rect(self.posx, self.posy + 10, self.width - 20, self.height - 10)
            
        if self.posx > WIDTH or self.posx < -self.width:
            self.terminate = True

    def display(self):
#        pygame.draw.rect(self.screen, GREEN, self.rect_hit)
        self.screen.blit(self.sprite, self.rect)
        
class CarFront():
    def __init__(self, screen, sprite, posx, posy, width=250, height=250, left_or_right = 0):
        self.screen = screen

        self.posx = posx
        self.posy = posy

        self.width = width
        self.height = height

        self.approaching_y = 0
        self.approaching_x = 0

        self.left_or_right = left_or_right

        self.sprite_initial = sprite
        self.sprite_transform = sprite

        self.rect = self.sprite_initial.get_rect(center=(self.posx + self.width//2, self.posy+ self.height//2)) 

        self.terminate = False

    def car_approaching(self):
        speed_factor = 0.05

        self.approaching_x += (255 - self.approaching_x) * speed_factor
        self.approaching_y += (255 - self.approaching_y) * speed_factor

        if self.approaching_x >= 250:
            self.approaching_x = 250
        if self.approaching_y >= 250:
            self.approaching_y = 250
            self.terminate = True

        self.sprite_transform = pygame.transform.scale(self.sprite_initial, (int(self.approaching_x), int(self.approaching_y)))
        sprite_width = self.sprite_transform.get_width()
        sprite_height = self.sprite_transform.get_height()
        self.rect = self.sprite_transform.get_rect(center=(self.posx + self.width//2 + self.left_or_right * self.width, HEIGHT - 50 - sprite_height//2))

    def display(self):
        self.screen.blit(self.sprite_transform, self.rect)
        
class Player():
    def __init__(self, screen, posx, posy, width = 25, height = 25, score = 0):
        self.screen = screen
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height

        self.velocity = [0, 0]
        self.acceleration = [0, 0]
        self.gravity = 0.5
        self.acceleration_x = 0.5
        self.jump_power = 20
        self.on_ground = False
        self.score = 0

        self.rect = pygame.Rect(self.posx, self.posy, self.width, self.height)

    def move(self, keys):

        self.acceleration[0] = 0
        self.acceleration[1] = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.acceleration[0] -= self.acceleration_x
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.acceleration[0] += self.acceleration_x

        self.velocity[0] += self.acceleration[0]
        self.velocity[0] *= 0.9

        if keys[pygame.K_SPACE] and self.on_ground or keys[pygame.K_w] and self.on_ground:
            self.acceleration[1] = 0
            self.acceleration[1] -= self.jump_power
            self.on_ground = False

        if self.on_ground == False:
            self.acceleration[1] += self.gravity
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.acceleration[1] += self.gravity
        self.velocity[1] += self.acceleration[1]

        self.posx += self.velocity[0]
        self.posy += self.velocity[1]

        if self.posx < 0:
            self.posx = 0
        elif self.posx > WIDTH - self.width:
            self.posx = WIDTH - self.width

        self.rect.topleft = (self.posx, self.posy)

    def check_collision(self, plattform):
        if self.rect.colliderect(plattform.rect):
            if self.velocity[1] >= 0:
                self.posy = plattform.rect.y - self.height
                self.velocity[1] = 0
                self.on_ground = True

    def display(self):

        pygame.draw.rect(self.screen, WHITE, self.rect)
        
class Plattform():
    def __init__(self, screen, posx, posy, width = WIDTH, height = 500):
        self.screen = screen
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height

        self.rect = pygame.Rect(self.posx, self.posy, self.width, self.height)

    def display(self):
        pygame.draw.rect(self.screen, WHITE, self.rect)

class Exclamation_mark():
    def __init__(self, screen, sprite, posx, posy, width=125, height=125, left_or_right = 0):

        self.screen = screen
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.left_or_right = left_or_right

        self.sprite_initial = sprite

        self.rect = self.sprite_initial.get_rect(center=(self.posx, self.posy)) 

    def display(self):
        if self.left_or_right == 0:
            self.rect = self.sprite_initial.get_rect(center=(self.posx, self.posy)) 
        else:
            self.rect = self.sprite_initial.get_rect(center=(self.left_or_right * WIDTH - self.posx, self.posy)) 
        self.screen.blit(self.sprite_initial, self.rect)

class Arrow():
    def __init__(self, screen, sprite, posx, posy, width=125, height=125, left_or_right = 0):

        self.screen = screen
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.left_or_right = left_or_right

        self.sprite_initial = sprite

        self.rect = self.sprite_initial.get_rect(center=(self.posx, self.posy)) 

    def display(self):
        if self.left_or_right == 0:
            self.sprite = pygame.transform.flip(self.sprite_initial, True, False)
            self.rect = self.sprite_initial.get_rect(center=(self.posx, self.posy)) 
        else:
            self.rect = self.sprite_initial.get_rect(center=(self.left_or_right * WIDTH - self.posx, self.posy))
            self.sprite = self.sprite_initial
        self.screen.blit(self.sprite, self.rect)

class Text():
    def __init__(self, screen, posx, posy, text, fontsize = 50):
        self.posx = posx
        self.posy = posy
        self.text = text
        self.screen = screen
        self.font = pygame.font.Font('assets/font/PIXY.otf', fontsize)

        self.surface = self.font.render(self.text, True, WHITE)
        self.rect = self.surface.get_rect(center=(self.posx, self.posy))

    def display(self):
        self.screen.blit(self.surface, self.rect)

async def gameplay():
    running = True
    clock = pygame.time.Clock()

    platform = Plattform(screen, 0, HEIGHT-50)
    player = Player(screen, WIDTH//2, HEIGHT-50-100)

    car_sound_alarm_flag = True

    car_front_list = []
    car_front_rng = random.randint(5*FPS, 10*FPS)
    car_front_counter = 0
    car_front_left_or_right = random.randint(0, 1)

    car_side_list = []
    car_side_rng = random.randint(5*FPS, 10*FPS)
    car_side_counter = 0
    car_side_left_or_right = random.randint(0, 1)

    exclamation_mark_counter = 0 
    exclamation_mark = Exclamation_mark(screen, exclamation_mark_sprite, 125, HEIGHT-50-125, left_or_right=car_front_left_or_right)

    arrow_counter = 0
    arrow = Arrow(screen, arrow_sprite, 125, HEIGHT-50-125, left_or_right=car_side_left_or_right)

    car_side_counter_allow = True
    car_front_counter_allow = True

    brick_stone_list = []
    brick_stone_cycle = 1
    brick_counter = 0

    pygame.mixer.music.play(-1)  # -1 means loop indefinitely
    pygame.mixer.music.set_volume(0.08)

    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.move(keys)
        player.check_collision(platform)

        
        brick_counter += 1
        if brick_counter > brick_stone_cycle * FPS:
            brick_stone_list.append(Brick(screen, brick_stone_sprite, posx = random.random() * (WIDTH-75)))
            brick_counter = 0
            brick_stone_cycle -= 0.05
            if brick_stone_cycle < 0.5:
                brick_stone_cycle = 0.5

        if car_side_counter_allow:
            car_side_counter +=1

        if car_side_counter > car_side_rng:
            arrow_counter += 1
            car_front_counter_allow = False

            if arrow_counter < 2*FPS//6 or (arrow_counter > 2*FPS//3 and arrow_counter < 2*FPS//2) or (arrow_counter > 2*FPS*4//6 and arrow_counter < 2*FPS*5//6):
                arrow.display()
                if car_sound_alarm_flag:
                    pygame.mixer.Sound.play(alarm)                    
                car_sound_alarm_flag = False
            else:
                car_sound_alarm_flag = True

            if arrow_counter > 2*FPS*5//6:
                pygame.mixer.Sound.play(car_engine)  
                car_side_list.append(CarSide(screen, sprite = car_side_sprite,left_or_right=car_side_left_or_right))
                car_side_rng = random.randint(1*FPS, 5*FPS)
                car_side_left_or_right = random.randint(0, 1)
                arrow.left_or_right = car_side_left_or_right
                car_side_counter = 0
                arrow_counter = 0

        if car_front_counter_allow:
            car_front_counter +=1
        if car_front_counter > car_front_rng:
            exclamation_mark_counter += 1
            car_side_counter_allow = False

            if exclamation_mark_counter < 2*FPS//6 or exclamation_mark_counter > 2*FPS//3 and exclamation_mark_counter < 2*FPS//2 or exclamation_mark_counter > 2*FPS*4//6 and exclamation_mark_counter < 2*FPS*5//6:
                exclamation_mark.display()
                if car_sound_alarm_flag:
                    pygame.mixer.Sound.play(alarm)                    
                car_sound_alarm_flag = False
            else:
                car_sound_alarm_flag = True

            if exclamation_mark_counter > 2*FPS:
                pygame.mixer.Sound.play(car_engine)
                car_front_list.append(CarFront(screen, car_front_sprite, 0, HEIGHT-50, left_or_right = car_front_left_or_right))
                car_front_rng = random.randint(1*FPS, 5*FPS)
                car_front_left_or_right = random.randint(0, 1)
                exclamation_mark.left_or_right = car_front_left_or_right
                car_front_counter = 0
                exclamation_mark_counter = 0

        for brick in brick_stone_list[:]:
            brick.fall()
            if brick.terminate:
                player.score += 1
                brick_stone_list.remove(brick)

        for car_side in car_side_list[:]:
            car_side.car_approaching()
            if car_side.terminate:
                player.score += 5
                car_side_list.remove(car_side)
                car_front_counter_allow = True
                print("works")

        for car_front in car_front_list[:]:
            car_front.car_approaching()
            if car_front.terminate:
                player.score += 5
                car_front_list.remove(car_front)
                car_side_counter_allow = True

        text_title = Text(screen, WIDTH - 125, 25, f"score: {player.score}", 30)

        player.display()
        platform.display()
        for brick in brick_stone_list:
            brick.display()
        for car_front in car_front_list:
            car_front.display()
        for car_side in car_side_list:
            car_side.display()
        
        for car_front in car_front_list[:]:
            if car_front.rect.colliderect(player.rect) and car_front.approaching_y > 200:
                return player.score
        
        for car_side in car_side_list[:]:
            if car_side.rect_hit.colliderect(player.rect):
                return player.score
        
        for brick in brick_stone_list[:]:
            if brick.rect.colliderect(player.rect):
                return player.score

        text_title.display()

        pygame.display.update()
        clock.tick(FPS)
        await asyncio.sleep(0)

    pygame.quit()

async def main():
    running = True
    clock = pygame.time.Clock()

    High_score = 0

    text_title = Text(screen, WIDTH//2, 100, "Urban dodge", 50)
    text_start = Text(screen, WIDTH//2, 300, "Start", 40)
    text_score = Text(screen, WIDTH//2, 150, f"High score: {High_score}", 20)
    mouse_pos = (0,0)

    while running:
        screen.fill(BLACK)

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if (event.type == pygame.MOUSEBUTTONDOWN and text_start.rect.collidepoint(mouse_pos)) or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                score = await gameplay()
                if score > High_score:
                    High_score = score
                    text_score = Text(screen, WIDTH//2, 150, f"High score: {High_score}", 20) 


        if High_score > 0:
            text_score.display()
        text_start.display()
        text_title.display()
        pygame.display.update()
        clock.tick(FPS)
        await asyncio.sleep(0)

    pygame.quit()     

asyncio.run(main())