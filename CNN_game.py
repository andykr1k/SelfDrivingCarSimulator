import pygame
import time
import math
from PIL import Image
from CNN.CNN import CNN_Predict
from funcs.utils import scale_image, blit_rotate_center, blit_text_center

pygame.font.init()

GRASS = scale_image(pygame.image.load("./images/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("./images/track.png"), 0.9)

TRACK_BORDER = scale_image(pygame.image.load(
    "./images/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = pygame.image.load("./images/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130, 250)

RED_CAR = scale_image(pygame.image.load("./images/red-car.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("./images/green-car.png"), 0.55)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

MAIN_FONT = pygame.font.SysFont("comicsans", 18)

FPS = 60


class GameInfo:
    LEVELS = 10

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time)


class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.images = self.images
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.images, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.images)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0


class PlayerCar(AbstractCar):
    images = RED_CAR
    START_POS = (165, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()


def draw(win, images, player_car, game_info):
    for images, pos in images:
        win.blit(images, pos)

    # level_text = MAIN_FONT.render(
    #     f"Level {game_info.level}", 1, (255, 255, 255))
    # win.blit(level_text, (10, HEIGHT - level_text.get_height() - 70))

    # time_text = MAIN_FONT.render(
    #     f"Time: {game_info.get_level_time()}s", 1, (255, 255, 255))
    # win.blit(time_text, (10, HEIGHT - time_text.get_height() - 40))

    # vel_text = MAIN_FONT.render(
    #     f"Vel: {round(player_car.vel, 1)}px/s", 1, (255, 255, 255))
    # win.blit(vel_text, (10, HEIGHT - vel_text.get_height() - 10))

    player_car.draw(win)
    pygame.display.update()


def AI_move_player(player_car, window):
    player_rect = pygame.Rect(
        player_car.x - 50, player_car.y - 50, 100, 100)
    capture_surface = pygame.Surface(
        (player_rect.width, player_rect.height))
    capture_surface.blit(window, (0, 0), player_rect)
    scaled_surface = pygame.transform.scale(capture_surface, (64, 64))
    pixel_data = pygame.image.tostring(scaled_surface, 'RGBA', False)
    pil_image = Image.frombytes('RGBA', scaled_surface.get_size(), pixel_data)
    grayscale_image = pil_image.convert('L')
    steering_vector = CNN_Predict(grayscale_image)

    threshold = 0.5
    if float(steering_vector[0]) > threshold:
        player_car.rotate(left=True)
    if float(steering_vector[1]) > threshold:
        player_car.rotate(right=True)
    if float(steering_vector[2]) > threshold:
        player_car.move_forward()
    if float(steering_vector[3]) > threshold:
        player_car.reduce_speed()


def handle_collision(player_car, game_info):
    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()

    player_finish_poi_collide = player_car.collide(
        FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            game_info.next_level()
            player_car.reset()


run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)),
          (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]

player_car = PlayerCar(4, 4)
game_info = GameInfo()
frames = 0

while run:
    clock.tick(FPS)

    draw(WIN, images, player_car, game_info)

    while not game_info.started:
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.KEYDOWN:
                game_info.start_level()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
    # if frames % 10:
    AI_move_player(player_car, WIN)

    # handle_collision(player_car, game_info)

    frames += 1

    if game_info.game_finished():
        blit_text_center(WIN, MAIN_FONT, "You won the game!")
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()


pygame.quit()
