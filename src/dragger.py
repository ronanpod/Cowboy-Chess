import pygame
from const import *


class Dragger:

    def __init__(self):
        self.piece = None
        self.dragging =  False
        self.mousex = 0
        self.mousey = 0
        self.initial_row = 0
        self.initial_col = 0

    def update_mouse(self, pos):
        self.mousex, self.mousey = pos

    # blit methods

    def update_blit(self, surface):
        # texture
        self.piece.set_texture(size = 128)
        texture = self.piece.texture
        # image
        img = pygame.image.load(texture)
        # rectangle
        img_center = (self.mousex, self.mousey)
        self.piece.texture_rect = img.get_rect(center = img_center)
        # blit
        surface.blit(img, self.piece.texture_rect)

    # other methods

    def save_initial(self, pos):
        self.initial_row = pos[1] // sqsize
        self.initial_col = pos[0] // sqsize

    def drag_piece(self, piece):
        self.piece = piece
        self.dragging = True

    def undrag_piece(self):
        self.piece = None
        self.dragging = False
