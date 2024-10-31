import pygame, asyncio
from os.path import join #file paths
from random import randint, uniform


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join("images", "player.png")).convert_alpha() #load image
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)) #create surface
        self.direction = pygame.Vector2()
        self.speed = 500

        # cooldown for shooting laser
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

        # mask -> see collisions
        self.mask = pygame.mask.from_surface(self.image)

    def laser_timer(self): #check 
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        
        #normalize diagonal movement
        self.direction = ( 
            self.direction.normalize() if self.direction else self.direction
        ) 

        #player cannot leave window
        if self.rect.bottom + self.direction.y > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
        elif self.rect.top + self.direction.y < 0:
            self.rect.top = 0
        elif self.rect.right + self.direction.x > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
        elif self.rect.left + self.direction.x < 0 : 
            self.rect.left = 0
        else:
            self.rect.center += self.direction * self.speed * dt
        
        #shoot laser
        recent_keys = pygame.key.get_just_pressed()
        if (recent_keys[pygame.K_SPACE] or recent_keys[pygame.K_z] or keys[pygame.K_x] or keys[pygame.K_PERIOD] or keys[pygame.K_COMMA]) and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            laser_sound.play()
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()

        self.laser_timer() #start cooldown


class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(
            center=(randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT))
        )


class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom=pos)

    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups, speed):
        super().__init__(groups)
        self.original_surf = surf #helps with rotation animation
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1) #vary angles
        self.speed = randint(100, 300) + speed #vary speeds + speed up as time gets higher
        self.rotation_speed = randint(40, 80) #rotation animation
        self.rotation = 0

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if self.rect.top > WINDOW_HEIGHT: #kill if out of window
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center=self.rect.center)


class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center=pos) 

    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()


def collisions():
    global reset

    #collision is true when masks collide
    collision_sprites = pygame.sprite.spritecollide(
        player, meteor_sprites, True, pygame.sprite.collide_mask
    ) 

    #reset game if hit by meteor
    if collision_sprites:
        reset = pygame.time.get_ticks()//100
    #destroy meteor if hit by laser
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()


def display_score(reset):
    current_time = pygame.time.get_ticks() // 100 - reset
    text_surf = font.render(str(current_time), True, (240, 240, 240))     #text positioning
    text_rect = text_surf.get_frect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50)) 
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(
        display_surface, (240, 240, 240), text_rect.inflate(20, 10).move(0, -8), 5, 10
    ) #text box


# general setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space shooter")

#global variables
running = True
reset = 0

#clock
clock = pygame.time.Clock()

# image imports
star_surf = pygame.image.load(join("images", "star.png")).convert_alpha()
meteor_surf = pygame.image.load(join("images", "meteor.png")).convert_alpha()
laser_surf = pygame.image.load(join("images", "laser.png")).convert_alpha()
font = pygame.font.Font(join("images", "Oxanium-Bold.ttf"), 40)
explosion_frames = [
    pygame.image.load(join("images", "explosion", f"{i}.png")).convert_alpha()
    for i in range(21)
]

#sound imports
laser_sound = pygame.mixer.Sound(join("audio", "laser.wav"))
laser_sound.set_volume(0.1)
explosion_sound = pygame.mixer.Sound(join("audio", "explosion.wav"))
explosion_sound.set_volume(0.1)
damage_sound = pygame.mixer.Sound(join("audio", "damage.ogg"))
game_music = pygame.mixer.Sound(join("audio", "game_music.wav"))
game_music.set_volume(0.1)
game_music.play(loops=-1)

# sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
for i in range(20):
    Star(all_sprites, star_surf)
player = Player(all_sprites)

# custom events -> meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

async def main():
    global running
    while running:
        #delta time
        dt = clock.tick() / 1000 
        
        # event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            if event.type == meteor_event:
                x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
                Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites),pygame.time.get_ticks()//100 - reset)
        # update
        all_sprites.update(dt)
        collisions()

        # draw the game
        display_surface.fill("#3a2e3f")
        all_sprites.draw(display_surface)
        display_score(reset)

        # update display
        pygame.display.update()
        await asyncio.sleep(0)
        if not running:
            pygame.quit()
            return
    #running = false
    pygame.quit()
    

asyncio.run(main())
