import pygame as pg
from sys import exit, path
from os.path import join as os_join
from random import randint, choice

### CONSTANTS ###
#Paths
ASSETS_PATH = "./assets"
#Colors
PINK = (247, 144, 178)  ##f790b2
GREEN = (144, 247, 213) ##90f7d5
GREEN2 = (230, 247, 144)##e6f790
GREEN3 = pg.Color('#7c98b4')
GOLD = pg.Color('#E6CF4E')
GRAY = (64, 64, 64)
#Font sizes
SCORE_FTS = 50

# Sprite Classes #
class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # images
        player_walk_1 = pg.image.load(os_join(ASSETS_PATH, 'graphics/Player/player_walk_1.png')).convert_alpha()
        player_walk_2 = pg.image.load(os_join(ASSETS_PATH, 'graphics/Player/player_walk_2.png')).convert_alpha()
        self.player_jump =  pg.image.load(os_join(ASSETS_PATH, 'graphics/Player/jump.png')).convert_alpha()
        # for animation
        self.player_walk_arr = [player_walk_1, player_walk_2]
        self.player_walk_idx = 0
        self.image = self.player_walk_arr[self.player_walk_idx] 
        # default position
        self.rect = self.image.get_rect(midbottom=(80, 300))
        # default gravity
        self.player_gravity = 0
        # sounds
        self.jump_sound = pg.mixer.Sound(os_join(ASSETS_PATH, 'audio/jump.mp3'))
        self.jump_sound.set_volume(0.09)

    def player_input(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE] or keys[pg.K_UP]:
            if self.rect.bottom == 300:
                self.player_gravity = -20
                self.jump_sound.play()

    def apply_gravity(self):
        self.player_gravity += 1
        self.rect.y += self.player_gravity
        if self.rect.bottom >= 300: self.rect.bottom = 300

    def animation_state(self):
        if self.rect.bottom < 300: self.image = self.player_jump
        else:
            self.player_walk_idx += 0.1
            if self.player_walk_idx >= len(self.player_walk_arr): self.player_walk_idx = 0
            self.image = self.player_walk_arr[int(self.player_walk_idx)]

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()


class Obstacle(pg.sprite.Sprite):
    def __init__(self, sprite_type):
        super().__init__()
        # Index to track/control frame change
        # Create different sprites
        if sprite_type == "fly":
            fly1 = pg.image.load(os_join(ASSETS_PATH, 'graphics/Fly/Fly1.png')).convert_alpha()
            fly2 = pg.image.load(os_join(ASSETS_PATH, 'graphics/Fly/Fly2.png')).convert_alpha()
            self.frames = [fly1, fly2]
            y_pos = 210
        else:
            snail1 = pg.image.load(os_join(ASSETS_PATH, 'graphics/snail/snail1.png')).convert_alpha()
            snail2 = pg.image.load(os_join(ASSETS_PATH, 'graphics/snail/snail2.png')).convert_alpha()
            self.frames = [snail1, snail2]
            y_pos = 300

        self.animation_idx = 0
        # Set default image, position
        self.image = self.frames[self.animation_idx] 
        self.rect = self.image.get_rect(midbottom = (randint(900, 1100), y_pos))

    def animation_state(self):
        self.animation_idx += 0.1
        if self.animation_idx >= 2: self.animation_idx = 0
        self.image = self.frames[int(self.animation_idx)] 

    def update(self):
        self.animation_state()
        self.rect.x -= 6
        self.destroy()

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()



### Additional Functions ###
def sprite_collision(player, obstacle_group): 
    """Arguments- player: single sprite group, obstacle_group: sprite group
       Checks collision
    """
    if pg.sprite.spritecollide(player.sprite, obstacle_group, False):
        #Delete obstacles
        obstacle_group.empty()
        return False
    return True

def display_score(center_x=400, center_y=50):
    # calculate time of the current round, modify and display it
    score = (pg.time.get_ticks() - score_time_offset) // 1000
    score_txt = score_font.render(f"Score: {score}", False, GRAY) 
    score_rect = score_txt.get_rect(center=(center_x, center_y))
    screen.blit(score_txt, score_rect)
    return score


## Basic Set Up ##
pg.init()
size = width, height = 800, 400
pg.display.set_caption("Pixel Jump!")
screen = pg.display.set_mode(size)
icon = pg.image.load(os_join(ASSETS_PATH, 'graphics/Player/player_stand.png')).convert_alpha()
pg.display.set_icon(icon)
clock = pg.time.Clock()
score_font = pg.font.Font(os_join(ASSETS_PATH, 'font/Pixeltype.ttf'), SCORE_FTS)
game_active = False 
score_time_offset = 0
score = 0
#Music
bg_music = pg.mixer.Sound(os_join(ASSETS_PATH, 'audio/music.wav'))
bg_music.set_volume(0.1)
bg_music.play(loops = -1)

#Surfaces
sky_sfs = pg.image.load(os_join(ASSETS_PATH, 'graphics/Sky.png')).convert()
ground_sfs = pg.image.load(os_join(ASSETS_PATH, 'graphics/ground.png')).convert()


#Groups
player = pg.sprite.GroupSingle()
player.add(Player())
obstacle_group = pg.sprite.Group()

#Game intro
player_stand = pg.image.load(os_join(ASSETS_PATH, 'graphics/Player/player_stand.png')).convert_alpha()
player_stand = pg.transform.rotozoom(player_stand, 0, 1.7)
player_stand_rect = player_stand.get_rect(center = (400, 200))

intro_txt = score_font.render("Press Space, or Up to start the game and jump!", False, GRAY)
intro_txt_rect = intro_txt.get_rect(center = (400, 350))

snail_sfs = pg.image.load(os_join(ASSETS_PATH, 'graphics/snail/snail1.png')).convert_alpha()
snail_intro = pg.transform.rotozoom(snail_sfs, 0, 1.3)
snail_intro_rect = snail_intro.get_rect(midbottom=player_stand_rect.midtop)

# Timers
obstacle_timer = pg.USEREVENT + 1
# integer changes spawn rate of the obstacles
pg.time.set_timer(obstacle_timer, 1300)


# Main Gameloop
while 1:
    #Event Check
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit() 
            exit() 

        if game_active:
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(['fly', 'snail', 'snail', 'snail'])))
        else:
            if event.type == pg.KEYDOWN and (event.key == pg.K_SPACE or event.key == pg.K_UP):
                game_active = True
                # get time from the start of the app
                score_time_offset = pg.time.get_ticks()

    if(game_active):
        #Place fone surfaces
        screen.blit(sky_sfs, (0,0))
        screen.blit(ground_sfs, (0,300))

        #Place moving sprites 
        player.draw(screen)
        player.update()

        obstacle_group.draw(screen)
        obstacle_group.update()


        #Collision
        game_active = sprite_collision(player, obstacle_group)
        
        #Display Score
        score = display_score()

    else:
        #Show Intro 'Screen'
        screen.fill(GREEN3)
        screen.blit(player_stand, player_stand_rect)
        screen.blit(snail_intro, snail_intro_rect)
        screen.blit(intro_txt, intro_txt_rect)

        final_score = score_font.render(f"Score: {score}", False, GRAY)
        final_score_rect = final_score.get_rect(center = (400, 50))
        screen.blit(final_score, final_score_rect)

    #Update display, not faster than 60 tps
    pg.display.update()
    clock.tick(60)
