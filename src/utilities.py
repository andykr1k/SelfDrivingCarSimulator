import pygame

def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)

def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(
        center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)

def blit_text_center(win, font, text):
    render = font.render(text, 1, (200, 200, 200))
    win.blit(render, (win.get_width()/2 - render.get_width() /
                      2, win.get_height()/2 - render.get_height()/2))


def record(pygame, window, frames, left, right, forward, backward, brake, player_car):
    file = open("outputs/training_metadata.csv", "a")

    if frames == 0:
        file.write("path,left,right,forward,backward,brake\n")
    else:
        player_rect = pygame.Rect(
            player_car.x - 50, player_car.y - 50, 100, 100)
        capture_surface = pygame.Surface(
            (player_rect.width, player_rect.height))
        capture_surface.blit(window, (0, 0), player_rect)
        name = "outputs/training_data/" + str(frames) + ".jpeg"
        pygame.image.save(capture_surface, name)
        file.write(name + "," + str(left) + "," + str(right) + "," + str(forward) + "," + str(backward) + "," + str(brake) + "\n")
        name = "outputs/training_data/vertically_flipped_" + str(frames) + ".jpeg"
        flipped_screen = pygame.transform.flip(capture_surface, False, True)
        pygame.image.save(flipped_screen, name)
        file.write(name + "," + str(left) + "," + str(right) + "," + str(forward) + "," + str(backward) + "," + str(brake) + "\n")
        name = "outputs/training_data/horizontally_flipped_" + str(frames) + ".jpeg"
        flipped_screen = pygame.transform.flip(capture_surface, True, False)
        pygame.image.save(flipped_screen, name)
        file.write(name + "," + str(left) + "," + str(right) + "," + str(forward) + "," + str(backward) + "," + str(brake) + "\n")
    file.close()
