import pygame
import time
import math
import numpy as np
import random
from PIL import Image
from funcs.utils import scale_image, blit_rotate_center, blit_text_center
from DQN.DQN import DQN

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

clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)),
          (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]


class GameInfo():
    def __init__(self, level=1, car=None):
        self.level = level
        self.started = False
        self.level_start_time = 0
        self.action_space = 4
        self.car = car
        self.num_actions = 4

    def step(self, action):
        return

    def next_level(self):
        self.level += 1
        self.started = False

    def draw(win, images, player_car):
        for images, pos in images:
            win.blit(images, pos)
        player_car.draw(win)
        pygame.display.update()

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def game_finished(self):
        return self.level > 10

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time)

    def preprocess_state(self):
        image = self.state
        resized_image = image.resize((84, 84))
        grayscale_image = resized_image.convert('L')
        grayscale_array = np.array(grayscale_image)
        normalized_array = grayscale_array / 255.0
        return normalized_array


class Car:
    def __init__(self):
        self.images = RED_CAR
        self.max_vel = 5
        self.vel = 0
        self.rotation_vel = 0.5
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

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
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


def select_action(state, epsilon, model):
    if np.random.rand() < epsilon:
        return np.random.randint(4)
    else:
        q_values = model.predict(state)
        return np.argmax(q_values)


def execute_action(action, player_car):
    if action == 0:
        player_car.rotate(left=True)
    elif action == 1:
        player_car.rotate(right=True)
    elif action == 2:
        player_car.move_forward()
    elif action == 3:
        player_car.reduce_speed()


def handle_collision(player_car, game_info):
    reward = 0
    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()
        reward = -3
    player_finish_poi_collide = player_car.collide(
        FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
            reward = -3
        else:
            game_info.next_level()
            player_car.reset()
            reward = 3

    reward = 1 if reward >= 0 else reward

    return reward


car = Car()
game_info = GameInfo(1, car)
model = DQN(game_info.preprocess_state().shape, game_info.num_actions)

for episode in range(50):
    while not game_info.game_finished():
        reward = 0
        clock.tick(FPS)

        while not game_info.started:
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    break

                if event.type == pygame.KEYDOWN:
                    game_info.start_level()

        if game_info.game_finished():
            reward += 10

        state = game_info.preprocess_state()
        action = select_action(state, 0.1, model)
        execute_action(action, car)
        reward += handle_collision(car, game_info)
        next_state = game_info.preprocess_state()
        done = game_info.game_finished()

        model.store_transition(state, action, reward, next_state, done)
        model.train()

    game_info.reset()
    car.reset()
    reward = 0

pygame.quit()
