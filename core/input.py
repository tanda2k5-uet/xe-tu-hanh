import pygame

class Input(object):

    def __init__(self):
        # has the user quit the application?
        self.quit = False
        self.mouse_clicked = False
        self.mouse_pos = (0, 0)

    def update(self):
        self.mouse_clicked = False
        # iterate over all user input events (such as keyboard or mouse) that occured since the last time events were checked
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.mouse_clicked = True
                self.mouse_pos = event.pos