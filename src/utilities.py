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

def record(pygame, window, frames, movement_vector):
    file = open("outputs/training_metadata.csv", "a")

    if frames == 0:
        file.write("path,steering\n")
    else:
        name = "outputs/training_data/" + str(frames) + ".jpeg"
        pygame.image.save(window, name)
        file.write(name + "," + str(movement_vector) + "\n")
        name = "outputs/training_data/flipped_" + str(frames) + ".jpeg"
        flipped_screen = pygame.transform.flip(window, False, True)
        pygame.image.save(flipped_screen, name)
        file.write(name + "," + str(movement_vector) + "\n")

    file.close()
