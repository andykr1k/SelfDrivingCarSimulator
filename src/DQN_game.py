from CNN import CNN_Predict
import pygame
import time
import math
import numpy as np
from utilities import scale_image, blit_rotate_center, blit_text_center
from DQN import DQN
from PIL import Image

pygame.font.init()
GRASS = scale_image(pygame.image.load("images/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("images/track.png"), 0.9)
TRACK_BORDER = scale_image(pygame.image.load("images/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = pygame.image.load("images/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130, 250)
RED_CAR = scale_image(pygame.image.load("images/red-car.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("images/green-car.png"), 0.55)
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
        self.max_vel = 2.25
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
    START_POS = (180, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()


def draw(win, images, player_car, game_info):
    for images, pos in images:
        win.blit(images, pos)
    player_car.draw(win)
    pygame.display.update()
    pixels = pygame.image.tostring(WIN, 'RGB')
    image_array = np.frombuffer(pixels, dtype=np.uint8)
    image_array = image_array.reshape((HEIGHT, WIDTH, 3))
    return image_array

def draw_next_state(win, images, player_car, game_info):
    for images, pos in images:
        win.blit(images, pos)
    player_car.draw(win)
    pixels = pygame.image.tostring(WIN, 'RGB')
    image_array = np.frombuffer(pixels, dtype=np.uint8)
    image_array = image_array.reshape((HEIGHT, WIDTH, 3))
    return image_array

def preprocess_state(state):
    image = Image.fromarray(state)
    resized_image = image.resize((84, 84))
    grayscale_image = resized_image.convert('L')
    grayscale_array = np.array(grayscale_image)
    normalized_array = grayscale_array / 255.0
    return normalized_array

def select_action(state, epsilon):
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

clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)),
          (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
images = [(TRACK, (0, 0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]

pixels = pygame.image.tostring(WIN, 'RGB')
image_array = np.frombuffer(pixels, dtype=np.uint8)
image_array = image_array.reshape((HEIGHT, WIDTH, 3))

input_shape = image_array.shape
num_actions = 4
model = DQN(input_shape, num_actions)

player_car = PlayerCar(4, 4)
game_info = GameInfo()
frames = 0
episodes = 50

for episode in range(episodes):
    while not game_info.game_finished():
        reward = 0
        clock.tick(FPS)

        current_game_state = draw(WIN, images, player_car, game_info)

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

        state = preprocess_state(current_game_state)

        action = select_action(state, epsilon=0.1)

        execute_action(action, player_car)

        reward += handle_collision(player_car, game_info)

        frames += 1

        next_state = preprocess_state(draw_next_state(WIN, images, player_car, game_info))
        done = game_info.game_finished()

        model.store_transition(state, action, reward, next_state, done)
        model.train()

    game_info.reset()
    player_car.reset()
    frames = 0
    reward = 0

pygame.quit()