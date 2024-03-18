import pygame
from const import *
from board import Board 
from square import Square
from dragger import Dragger
from config import Config
from piece import *

class Game:

    def __init__(self):
        self.next_player = 'white'
        self.hovered_sqr = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()

    # blit methods

    def show_bg(self, surface):
        theme = self.config.theme

        for row in range(rows):
            for col in range(cols):
                # color
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark
                # rect
                rect = (col * sqsize, row * sqsize, sqsize, sqsize)
                # blit
                pygame.draw.rect(surface, color, rect)

                # row coordinates
                if col == 0:
                    # color
                    color = theme.bg.dark if row % 2 == 0 else theme.bg.light
                    # label 
                    lbl = self.config.font.render(str(rows-row), 1, color)
                    lbl_pos = (5, 5 + row * sqsize)
                    # blit
                    surface.blit(lbl, lbl_pos)
                
                # col coordinates
                if row == 7:
                    # color
                    color = theme.bg.dark if (row + col)% 2 == 0 else theme.bg.light
                    # label 
                    lbl = self.config.font.render(Square.get_alphacol(col), 1, color)
                    lbl_pos = (col * sqsize + sqsize - 20, height - 20)
                    # blit
                    surface.blit(lbl, lbl_pos)


    def show_pieces(self, surface):
        for row in range(rows):
            for col in range(cols):
                # piece on square?
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece
                    
                    # all pieces not dragging
                    if piece is not self.dragger.piece:
                        piece.set_texture(size = 80)
                        img = pygame.image.load(piece.texture)
                        img_center = col * sqsize + sqsize // 2, row * sqsize + sqsize // 2
                        piece.texture_rect = img.get_rect(center = img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface):
        theme = self.config.theme

        if self.dragger.dragging:
            piece = self.dragger.piece

            # loop all valid moves
            for move in piece.moves:
                # color
                color = theme.moves.light if (move.final.row + move.final.col) % 2 == 0 else theme.moves.dark
                # rect
                rect = (move.final.col * sqsize, move.final.row * sqsize, sqsize, sqsize)
                # blit
                pygame.draw.rect(surface, color, rect)
    
    def show_last_move(self, surface):
        theme = self.config.theme

        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:
                # color 
                color = theme.trace.light if (pos.row + pos.col) % 2 == 0 else theme.trace.dark
                # rect
                rect = (pos.col * sqsize, pos.row * sqsize, sqsize, sqsize)
                # blit
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_sqr:
            # color
            color = (180, 180, 180)
            #rect
            rect = (self.hovered_sqr.col * sqsize, self.hovered_sqr.row * sqsize, sqsize, sqsize)
            # blit
            pygame.draw.rect(surface, color, rect, width=3)

    # other methods

    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def set_hover(self, row, col):
        self.hovered_sqr = self.board.squares[row][col]

    def change_theme(self):
        self.config.change_theme()

    def play_sound(self, captured = False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        self.__init__()
        
    def checked(self):
        colour = self.next_player
        for row in range(rows):
            for col in range(cols):
                if self.board.squares[row][col].has_piece():
                    p = self.board.squares[row][col].piece
                    if isinstance(p, King):
                        if p.color == colour:
                            # is the king currently in check?

                            #knights
                            evil_knight = [(row - 2, col  + 1), (row - 1, col + 2), (row + 1, col + 2), (row + 2, col + 1), (row + 2, col - 1), (row + 1, col - 2), (row - 1, col -2), (row - 2, col - 1)]
                            for x in evil_knight:
                                i, j = x
                                if Square.in_range(i, j):
                                    if self.board.squares[i][j].has_rival_piece(colour):
                                        if isinstance(self.board.squares[i][j].piece, Knight):
                                            return True
                                        
                             #cowboys
                            evil_cowboy = [(row - 2, col  + 1), (row - 1, col + 2), (row + 1, col + 2), (row + 2, col + 1), (row + 2, col - 1), (row + 1, col - 2), (row - 1, col -2), (row - 2, col - 1), (row - 3, col  + 1), (row - 1, col + 3), (row + 1, col + 3), (row + 3, col + 1), (row + 3, col - 1), (row + 1, col - 3), (row - 1, col -3), (row - 3, col - 1)]
                            for x in evil_cowboy:
                                i, j = x
                                if Square.in_range(i, j):
                                    if self.board.squares[i][j].has_rival_piece(colour):
                                        if isinstance(self.board.squares[i][j].piece, Cowboy):
                                            return True
                            
                            #pawns
                            if colour == 'white':
                                evil_pawn = [(row-1, col-1), (row+1, col-1)]
                            else:
                                evil_pawn = [(row-1, col+1), (row+1, col+1)]
                            for x in evil_pawn:
                                i, j = x
                                if Square.in_range(i, j):
                                    if self.board.squares[i][j].has_rival_piece(colour):
                                        if isinstance(self.board.squares[i][j].piece, Pawn):
                                            return True
                                        
                            #bishops
                            increments = [(1,1), (-1, -1), (1, -1), (-1, 1)]
                            for incr in increments:
                                i, j = incr
                                nextrow = row+i
                                nextcol = col+j
                                while True:
                                    if Square.in_range(nextrow, nextcol):
                                        if self.board.squares[nextrow][nextcol].has_piece():
                                            pc = self.board.squares[nextrow][nextcol].piece
                                            if pc.color != colour:
                                                if isinstance(pc, Bishop):
                                                    return True
                                                elif isinstance(pc, Queen):
                                                    return True
                                                else: break
                                            else: break
                                        else:
                                            nextrow += i
                                            nextcol += j
                                    else: break
                            #rooks
                            increments2 = [(0,1), (0, -1), (1, 0), (-1, 0)]
                            for incr in increments2:
                                i, j = incr
                                nextrow = row+i
                                nextcol = col+j
                                while True:
                                    if Square.in_range(nextrow, nextcol):
                                        if self.board.squares[nextrow][nextcol].has_piece():
                                            pc = self.board.squares[nextrow][nextcol].piece
                                            if pc.color != colour:
                                                if isinstance(pc, Rook):
                                                    return True
                                                elif isinstance(pc, Queen):
                                                    return True
                                                else: break
                                            else: break
                                        else:
                                            nextrow += i
                                            nextcol += j
                                    else: break

        return False

    def game_over(self):
        colour = self.next_player
        for row in range(rows):
            for col in range(cols):
                if self.board.squares[row][col].has_piece():
                    pc = self.board.squares[row][col].piece
                    if pc.color == colour:
                        pc.clear_moves()
                        self.board.calc_moves(pc, row, col)
                        for amove in pc.moves:
                            if self.board.valid_move(pc, amove):
                                return False
        return True