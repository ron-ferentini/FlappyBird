# Flappy
# Ron Ferentini
# 08/06/2023
#

import math
import os
import random

import pygame


class TextBox:
    def __init__(self, x, y, size,
                 color=pygame.Color("white"),
                 bg_color=pygame.Color("black")):
        self.x = x
        self.y = y
        self.font = pygame.font.Font(None, size)
        self.color = color
        self.bg_color = bg_color

    def draw(self, s, text):
        text_bitmap = self.font.render(text, True, self.color, self.bg_color)
        s.blit(text_bitmap, (self.x, self.y))


class Image(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_file)
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


class Foreground(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_file)
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location
        self.rect1 = self.rect.copy()
        self.rect2 = self.rect.copy()
        self.i = self.rect.w
        self.w = self.rect.w
        self.rect2.left = self.w
        self.stopped = False

    def update(self):
        if not self.stopped:
            self.rect1.left = self.i - self.w
            self.rect2.left = self.i
            self.i -= 1
            if self.i == 0:
                self.i = self.w


class Pipe(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_file)
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location
        self.up_rect = self.rect.copy()
        self.up_rect.height = 1000000
        self.up_rect.bottom = self.rect.top
        self.sibling = None
        self.stopped = True
        self.score_counted = False

    def update(self):
        if not self.stopped:
            vertical_space_between_pipes = 150
            pipe_height = 320
            self.rect.left -= 1
            self.up_rect.left -= 1
            if self.rect.right == 0 and self.sibling is not None:
                self.rect.left = self.rect.w * 10
                self.sibling.rect.left = self.rect.width * 10
                rnd = random.randint(150, 350)
                # set the bottom pipe
                self.sibling.rect.top = rnd
                self.rect.top = rnd - vertical_space_between_pipes - pipe_height
                self.score_counted = False
                self.up_rect = self.rect.copy()
                self.up_rect.height = 1000000
                self.up_rect.bottom = self.rect.top


class Bird(pygame.sprite.Sprite):
    def __init__(self, image_file_list, location):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        # state of flap during the game
        self.images_index = 1
        self.images.append(pygame.image.load(image_file_list[0]).convert_alpha())   # up flap
        self.images.append(pygame.image.load(image_file_list[1]).convert_alpha())   # mid flap
        self.images.append(pygame.image.load(image_file_list[2]).convert_alpha())   # down flap
        self.images.append(pygame.image.load(image_file_list[1]).convert_alpha())  # mid flap
        self.image = self.images[self.images_index]
        # used to slow the bird flapping
        self.frame_counter = 0
        self.image_copy = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location
        self.location = location
        self.waiting = True
        self.stopped = False
        self.angle = 0.0
        # gravity variables
        self.grav = 0.0
        self.accel = 0.10  # .2
        self.jump = -5.0   # -7.0

    def update(self):
        self.frame_counter += 1
        if self.frame_counter == 7:
            self.images_index += 1
            if self.images_index == len(self.images):
                self.images_index = 0
            self.frame_counter = 0

        if self.waiting:
            self.rect.top = self.location[1] + math.sin(self.angle) * 10
            self.angle += 0.1
            # check if the angle is 2 times Pi (2 * 3.14 = 6.28)
            if self.angle >= 6.28:
                self.angle = 0.0
            self.image = self.image_copy
            self.image = self.images[self.images_index]
        elif not self.stopped:
            self.grav += self.accel
            self.rect.y += self.grav
            if self.grav >= 7:
                self.image = pygame.transform.rotate(self.images[self.images_index], -90)
            elif self.grav >= 5:
                self.image = pygame.transform.rotate(self.images[self.images_index], -45)
            elif self.grav >= -2:
                self.image = self.images[self.images_index]
            else:
                self.image = pygame.transform.rotate(self.images[self.images_index], 45)
        else:
            pass

    def flap(self):
        self.grav += self.jump


def make_pipes(pipes):
    global ImagesFolder
    global ScreenWidth
    vertical_space_between_pipes = 150
    horizontal_space_between_pipes = ScreenWidth // 1.5
    pipe_height = 320
    start_delay = ScreenWidth * 1.5
    pipes.empty()
    for c in range(3):
        # top of bottom pipe
        rnd = random.randint(150, 350)
        down_pipe = Pipe(os.path.join(ImagesFolder, "pipe-green-lower.png"),
                         (start_delay + horizontal_space_between_pipes * c, rnd))
        up_pipe = Pipe(os.path.join(ImagesFolder, "pipe-green-upper.png"),
                       (start_delay + horizontal_space_between_pipes * c,
                        rnd - vertical_space_between_pipes - pipe_height))
        pipes.add(up_pipe)
        pipes.add(down_pipe)
        up_pipe.sibling = down_pipe


pygame.init()
clock = pygame.time.Clock()
fps = 60

# sound stuff
pygame.mixer.init()
audio_folder = "audio"
volume = 0.3
swoosh = pygame.mixer.Sound(os.path.join(audio_folder, "swoosh.ogg"))
swoosh.set_volume(volume)
wing = pygame.mixer.Sound(os.path.join(audio_folder, "wing.ogg"))
wing.set_volume(volume)
point = pygame.mixer.Sound(os.path.join(audio_folder, "point.ogg"))
point.set_volume(volume)
hit = pygame.mixer.Sound(os.path.join(audio_folder, "hit.ogg"))
hit.set_volume(volume)
die = pygame.mixer.Sound(os.path.join(audio_folder, "die.ogg"))
die.set_volume(volume)

ScreenHeight = 512
ScreenWidth = 288

pygame.display.set_caption("Flappy Birds")
screen = pygame.display.set_mode((ScreenWidth, ScreenHeight))

ImagesFolder = "images"
Background = Image(os.path.join(ImagesFolder, "background-day.png"), (0, 0))
Base = Foreground(os.path.join(ImagesFolder, "base.png"), (0, 400))

Pipes = pygame.sprite.Group()
make_pipes(Pipes)

faby_images = [os.path.join(ImagesFolder, "yellowbird-upflap.png"),
               os.path.join(ImagesFolder, "yellowbird-midflap.png"),
               os.path.join(ImagesFolder, "yellowbird-downflap.png")]

Faby = Bird(faby_images, (100, ScreenHeight / 3))

Restart = Image(os.path.join(ImagesFolder, "restart.png"), (80, ScreenHeight / 3))
Message = Image(os.path.join(ImagesFolder, "message.png"), (50, 10))

Score = 0
HighScore = 0
txtScore = TextBox(80, 430, 40, pygame.Color("black"),  pygame.Color(222, 216, 149))
txtHighScore = TextBox(50, 470, 40, pygame.Color("black"), pygame.Color(222, 216, 149))

GameRunning = True
while GameRunning:
    for event in pygame.event.get():
        # == means is equal to
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            GameRunning = False       # = means Gets... GameRunning variable gets the value false
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) \
                or event.type == pygame.MOUSEBUTTONDOWN:
            if Faby.waiting:
                pygame.mixer.Sound.play(swoosh)
                Faby.waiting = False
                Faby.flap()
                # start the pipes moving
                for p in Pipes:
                    p.stopped = False
            # restart code
            elif Faby.stopped:
                if Score > HighScore:
                    HighScore = Score
                Score = 0
                Faby.stopped = False
                Faby.waiting = True
                Faby.grav = 0.0
                make_pipes(Pipes)
                Base.stopped = False
            else:
                if not Base.stopped:
                    pygame.mixer.Sound.play(wing)
                    Faby.flap()

    screen.blit(Background.image, Background.rect)

    # draw the pipes and move them from right to left
    for p in Pipes:
        screen.blit(p.image, p.rect)
        p.update()

    # draw the bird
    screen.blit(Faby.image, Faby.rect)
    Faby.update()

    for p in Pipes:
        if Faby.rect.left >= p.rect.right and \
                not p.score_counted and \
                p.sibling is not None:
            pygame.mixer.Sound.play(point)
            Score += 1
            p.score_counted = True
            break

    # collision detection
    if pygame.sprite.spritecollideany(Faby, Pipes) or Faby.rect.bottom >= Base.rect1.top:
        # stop the base and pipes from moving
        if not Base.stopped:
            pygame.mixer.Sound.play(hit)
            pygame.mixer.Sound.play(die)
        # stop the base and pipes from moving
        Base.stopped = True
        for p in Pipes:
            p.stopped = True
    # collision with invisible rectangle above the upper pipe
    for p in Pipes:
        if pygame.Rect.colliderect(Faby.rect, p.up_rect) and p.sibling is not None:
            Faby.grav = 10.0
            Faby.accel = 0.20
            Faby.rect.bottom = 0
            if not Base.stopped:
                pygame.mixer.Sound.play(hit)
                pygame.mixer.Sound.play(die)
                # stop the base and pipes from moving
            Base.stopped = True
            for p2 in Pipes:
                p2.stopped = True
    if Faby.rect.bottom + 10 >= Base.rect1.top:
        Faby.stopped = True
        # stop the base and pipes from moving
        Base.stopped = True
        for p in Pipes:
            p.stopped = True

    # so welcome message when waiting
    if Faby.waiting:
        screen.blit(Message.image, Message.rect)

    if Faby.stopped:
        screen.blit(Restart.image, Restart.rect)

    # draw the base image
    screen.blit(Base.image, Base.rect1)
    screen.blit(Base.image, Base.rect2)
    # update the base image to show it moving from right to left
    Base.update()

    txtScore.draw(screen, f"Score: {Score}")
    txtHighScore.draw(screen, f" High Score: {HighScore}")

    pygame.display.update()
    clock.tick(fps)

# out of the while loop
print("Game over")
pygame.quit()
