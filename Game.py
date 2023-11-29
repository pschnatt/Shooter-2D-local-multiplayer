import pygame
import os
import random
import button

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('BattleChaos')

#set framerate
clock = pygame.time.Clock()
FPS = 60

#define game variables
GRAVITY = 0.75
BLOCK_SIZE = 40
start_game = False

#define player action variables
#1st player
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

#2nd player
moving_left2 = False
moving_right2 = False
shoot2 = False
grenade2 = False
grenade_thrown2 = False

#spawn ai or not
ai_activate = False

#load images
try:
#Title
    title = pygame.image.load('button\TITLE.png').convert_alpha()

    #button
    start = pygame.image.load('button\START.png').convert_alpha()
    exit = pygame.image.load('button\EXIT.png').convert_alpha()
    ai = pygame.image.load('button\AI.png').convert_alpha()

    #bullet
    bullet_img = pygame.image.load('weapon\Ammo.png').convert_alpha()
    bullet_img = pygame.transform.scale(bullet_img, (int(bullet_img.get_width() * 0.05), int(bullet_img.get_height() * 0.05)))

    #grenade
    grenade_img = pygame.image.load('weapon\EBomb.png').convert_alpha()
    grenade_img = pygame.transform.scale(grenade_img, (int(grenade_img.get_width() * 0.05), int(grenade_img.get_height() * 0.05)))

    #loot crates
    health_box_img = pygame.image.load('lootcrate\health.png').convert_alpha()
    health_box_img = pygame.transform.scale(health_box_img, (int(health_box_img.get_width() * 0.05), int(health_box_img.get_height() * 0.05)))
    ammo_box_img = pygame.image.load('lootcrate\Ammo.png').convert_alpha()
    ammo_box_img = pygame.transform.scale(ammo_box_img, (int(ammo_box_img.get_width() * 0.05), int(ammo_box_img.get_height() * 0.05)))
    grenade_box_img = pygame.image.load('lootcrate\grenade.png').convert_alpha()
    grenade_box_img = pygame.transform.scale(grenade_box_img, (int(grenade_box_img.get_width() * 0.05), int(grenade_box_img.get_height() * 0.05)))
except:
    print("Image not found")

#Dict for each of crate img
item_boxes = {
    'Health'    : health_box_img,
    'Ammo'      : ammo_box_img,
    'Grenade'   : grenade_box_img
}


#define colours
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

#define font
font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300),3)

class Character(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        #ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        
        #load all images for the players
        animation_types = ['idle', 'run', 'jump', 'death']
        for animation in animation_types:
            #reset temporary list of images
            temp_list = []
            #count number of files in the folder 
            num_of_frames = len(os.listdir(f'{self.char_type}{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'{self.char_type}{animation}\{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


    def move(self, moving_left, moving_right):
        #reset movement variables
        dx = 0
        dy = 0

        #assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        #apply gravity
        self.vel_y += GRAVITY
        # if self.vel_y > 10:
        #     self.vel_y
        dy += self.vel_y

        #check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

        #check wall collision
        if self.rect.left + dx < 0:
            dx = 0 - self.rect.left
        if self.rect.right +dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right

        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy


    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            #reduce ammo
            self.ammo -= 1


    def ai(self):
        if self.alive and (player.alive or player2.alive):
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)#0: idle
                self.idling = True
                self.idling_counter = 50
            #check if the ai in near the player
            if self.vision.colliderect(player.rect):
                #stop running and face the player
                self.update_action(0)#0: idle
                #shoot
                self.shoot()
            if self.vision.colliderect(player2.rect):
                #stop running and face the player
                self.update_action(0)#0: idle
                #shoot
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)#1: run
                    self.move_counter += 1

                    #update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > BLOCK_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 100 #ms
        #update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        #check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class Hitman(Character):
    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 75
            bullet = Bullet(self.rect.centerx + (self.rect.size[0] * self.direction), self.rect.centery, self.direction,20)
            bullet_group.add(bullet)
            #reduce ammo
            self.ammo -= 1

class Machinegunner(Character):
    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 10
            bullet = Bullet(self.rect.centerx + (self.rect.size[0] * self.direction), self.rect.centery, self.direction,5)
            bullet_group.add(bullet)
            #reduce ammo
            self.ammo -= 1

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type] #from dict
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + BLOCK_SIZE // 2, y + (BLOCK_SIZE - self.image.get_height()))

    def update(self):
        for player in player_group:
            #check if the player has picked up the box
            if pygame.sprite.collide_rect(self, player):
                #check what kind of box it was
                if self.item_type == 'Health':
                    player.health += 25
                    if player.health > player.max_health:
                        player.health = player.max_health
                elif self.item_type == 'Ammo':
                    player.ammo += 3
                elif self.item_type == 'Grenade':
                    player.grenades += 1
                #delete the item box
                self.kill()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        #update with new health
        self.health = health
        #calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction,damage=10):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.damage = damage

    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed)
        #check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        #check collision with characters
        for player in player_group:
            if pygame.sprite.spritecollide(player, bullet_group, False):
                if player.alive:
                    player.health -= self.damage
                    self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= self.damage
                    self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        #check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.speed = 0

        #check collision with walls
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1
            dx = self.direction * self.speed

        #update grenade position
        self.rect.x += dx
        self.rect.y += dy

        #countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            #do damage to anyone that is nearby
            for player in player_group:
                if abs(self.rect.centerx - player.rect.centerx) < BLOCK_SIZE * 2 and \
                    abs(self.rect.centery - player.rect.centery) < BLOCK_SIZE * 2:
                    player.health -= 40
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < BLOCK_SIZE * 2 and \
                    abs(self.rect.centery - enemy.rect.centery) < BLOCK_SIZE * 2:
                    enemy.health -= 40

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(0, 3):
            img = pygame.image.load(f'weapon\ex{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        EXPLOSION_SPEED = 4
        #update explosion amimation
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            #if the animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

#create_button
startbutton = button.Button((SCREEN_WIDTH//2)-400,(SCREEN_HEIGHT//2)-100,start,2.7)
aibutton = button.Button((SCREEN_WIDTH//2)-130,(SCREEN_HEIGHT//2)-100,ai,2.7)
exitbutton = button.Button((SCREEN_WIDTH//2)+140,(SCREEN_HEIGHT//2)-100,exit,2.7)
titlecard = button.Button((SCREEN_WIDTH//2)-175,(SCREEN_HEIGHT//2)-350,title,3.5)

#create sprite groups
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()

#temp - create item boxes
item_box = ItemBox('Health', 100, 260)
item_box_group.add(item_box)
item_box = ItemBox('Ammo', 400, 260)
item_box_group.add(item_box)
item_box = ItemBox('Grenade', 500, 260)
item_box_group.add(item_box)

player = Hitman('player', 200, 200, 0.1, 5, 20, 5)
health_bar = HealthBar(10, 10, player.health, player.health)
player_group.add(player)
player2 = Machinegunner('player',700,200,0.1,5,20,5)
health_bar2 = HealthBar(470, 10, player2.health, player2.health)
player_group.add(player2)

enemy = Character('enemy', 500, 200, 0.1, 2, 20, 0)
enemy2 = Character('enemy', 300, 200, 0.1, 2, 20, 0)
enemy_group.add(enemy)
enemy_group.add(enemy2)

run = True

while run:
    clock.tick(FPS)

    if start_game == False:
        #draw menu
        screen.fill(BG)
        titlecard.draw(screen)
        if exitbutton.draw(screen):
            run = False
        if aibutton.draw(screen):
            start_game = True
            ai_activate = True
        if startbutton.draw(screen):
            start_game = True
            ai_activate = False
        
    else:
        draw_bg()
        #show player health
        health_bar.draw(player.health)
        health_bar2.draw(player2.health)
        #show ammo
        draw_text('AMMO: ', font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (90 + (x * 10), 33))
        draw_text('AMMO: ', font, WHITE, 470, 35)
        for x in range(player2.ammo):
            screen.blit(bullet_img, (550 + (x * 10), 33))
        #show grenades
        draw_text('GRENADES: ', font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img, (135 + (x * 15), 56))
        draw_text('GRENADES: ', font, WHITE, 470, 60)
        for x in range(player2.grenades):
            screen.blit(grenade_img, (595 + (x * 15), 56))

        player.update()
        player2.update()
        player.draw()
        player2.draw()
        if ai_activate:
            for enemy in enemy_group:
                enemy.ai()
                enemy.update()
                enemy.draw()
        if player.alive or player2.alive:
            item_spawn_likely = random.randint(1,5000)
            #spawn item crate
            if item_spawn_likely == 1:
                item_box = ItemBox('Health', random.randint(100,500), 260)
                item_box_group.add(item_box)
            if item_spawn_likely == 2500:
                item_box = ItemBox('Ammo', random.randint(100,500), 260)
                item_box_group.add(item_box)
            if item_spawn_likely == 5000:
                item_box = ItemBox('Grenade', random.randint(100,500), 260)
                item_box_group.add(item_box)

        #update and draw groups
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)

        #update player actions      
        if player.alive:
            #shoot bullets
            if shoot:
                player.shoot()
            #throw grenades
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
                            player.rect.top, player.direction)
                grenade_group.add(grenade)
                #reduce grenades
                player.grenades -= 1
                grenade_thrown = True
            if player.in_air:
                player.update_action(2)#2: jump
            elif moving_left or moving_right:
                player.update_action(1)#1: run
            else:
                player.update_action(0)#0: idle
            player.move(moving_left, moving_right)
        
        if player2.alive:
            #shoot bullets
            if shoot2:
                player2.shoot()
            #throw grenades
            elif grenade2 and grenade_thrown2== False and player2.grenades > 0:
                grenade2 = Grenade(player2.rect.centerx + (0.5 * player2.rect.size[0] * player2.direction),\
                            player2.rect.top, player2.direction)
                grenade_group.add(grenade2)
                #reduce grenades
                player2.grenades -= 1
                grenade_thrown2 = True
            if player2.in_air:
                player2.update_action(2)#2: jump
            elif moving_left2 or moving_right2:
                player2.update_action(1)#1: run
            else:
                player2.update_action(0)#0: idle
            player2.move(moving_left2, moving_right2)

    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
        #keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_c:
                shoot = True
            if event.key == pygame.K_v:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            
            if event.key == pygame.K_LEFT:
                moving_left2 = True
            if event.key == pygame.K_RIGHT:
                moving_right2 = True
            if event.key == pygame.K_l:
                shoot2 = True
            if event.key == pygame.K_k:
                grenade2 = True
            if event.key == pygame.K_UP and player2.alive:
                player2.jump = True
            
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_r:
                start_game = False
                player.kill()
                player2.kill()
                for enemy in enemy_group:
                    enemy.kill()
                for lootcrate in item_box_group:
                    lootcrate.kill()
                player = Hitman('player', 200, 200, 0.1, 5, 20, 5)
                health_bar = HealthBar(10, 10, player.health, player.health)
                player_group.add(player)
                player2 = Machinegunner('player',700,200,0.1,5,20,5)
                health_bar2 = HealthBar(470, 10, player2.health, player2.health)
                player_group.add(player2)
                enemy = Character('enemy', 500, 200, 0.1, 2, 20, 0)
                enemy2 = Character('enemy', 300, 200, 0.1, 2, 20, 0)
                enemy_group.add(enemy)
                enemy_group.add(enemy2)

        #keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_c:
                shoot = False
            if event.key == pygame.K_v:
                grenade = False
                grenade_thrown = False

            if event.key == pygame.K_LEFT:
                moving_left2 = False
            if event.key == pygame.K_RIGHT:
                moving_right2 = False
            if event.key == pygame.K_l:
                shoot2 = False
            if event.key == pygame.K_k:
                grenade2 = False
                grenade_thrown2 = False

    pygame.display.update()

pygame.quit()