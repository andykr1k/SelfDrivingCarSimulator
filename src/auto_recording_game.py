import pygame
import time
import math
from utilities import scale_image, blit_rotate_center, blit_text_center, record
pygame.font.init()

# GRASS = scale_image(pygame.image.load("images/grass.jpg"), 2.5)
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

PATH = [(175, 119), (150, 80), (110, 70), (70, 90), (60, 133), (55, 300), (75, 491), (170, 600), (274, 710), (400, 698), (418, 521), (507, 475), (600, 551), (613, 715), (726, 703), (734, 399), (611, 357), (409, 343), (433, 257), (697, 258), (738, 123), (581, 71), (303, 78), (275, 377), (182, 378), (178, 260)]

FPS = 60


class GameInfo:
    def __init__(self):
        self.level = 1
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
        return self.level > 10

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

def draw(win, images, computer_car, game_info):
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
    computer_car.draw(win)

    pygame.display.update()


class ComputerCar(AbstractCar):
    images = RED_CAR
    START_POS = (170, 200)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = 2.25

    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255, 0, 0), point, 5)

    def draw(self, win):
        super().draw(win)
        self.draw_points(win)

    def calculate_angle(self):
        left = 0
        right = 0
        forward = 0
        brake = 0

        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi / 2
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
            left = 1
            forward = 1
        elif difference_in_angle < 0:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))
            right = 1
            forward = 1
        else:
            forward = 1
            if abs(difference_in_angle) < 0.1:
                brake = 1
        return left, right, forward, brake

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(
            self.x, self.y, self.images.get_width(), self.images.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            self.current_point = 0

        left, right, forward, brake = self.calculate_angle()
        self.update_path_point()
        super().move()

        return left, right, forward, brake


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
# images = [(GRASS, (0, 0)), (TRACK, (0, 0)),
#           (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
images = [(TRACK, (0, 0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
computer_car = ComputerCar(4, 4, PATH)
game_info = GameInfo()
frames = 0

while run:
    clock.tick(FPS)

    draw(WIN, images, computer_car, game_info)

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

    left, right, forward, brake = computer_car.move()

    # record(pygame, WIN, frames, left, right,
    #        forward, 0, brake, computer_car)

    frames += 1

    if game_info.game_finished():
        blit_text_center(WIN, MAIN_FONT, "You won the game!")
        pygame.time.wait(5000)
        game_info.reset()
        # player_car.reset()


pygame.quit()
