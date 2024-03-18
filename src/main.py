import pygame
import sys
from square import Square
from const import *
from game import Game
from move import Move

class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Cowboy Chess')
        self.game = Game()
        
    def mainloop(self):
        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger
        winner = 'white'
        game_new = True
        game_active = False
        game_over = False
        tutorial = False
        myfont = pygame.font.Font('/Users/ronanchan/Downloads/playful-time-star-font/PlayfulTime-BLBB8.ttf', 110)
        myfont2 = pygame.font.Font('/Users/ronanchan/Downloads/playful-time-star-font/PlayfulTime-BLBB8.ttf', 80)
        
        intro = pygame.image.load('/Users/ronanchan/Desktop/chess/pixil-frame-0.png')
        stalemate = pygame.image.load('/Users/ronanchan/Desktop/chess/src/GAMEOVER/pixil-frame-0-3.png')
        white_wins = pygame.image.load('/Users/ronanchan/Desktop/chess/src/GAMEOVER/pixil-frame-0-4.png')
        black_wins = pygame.image.load('/Users/ronanchan/Desktop/chess/src/GAMEOVER/pixil-frame-0-5.png')
        intro_rect = intro.get_rect()
        stalemate_rect = stalemate.get_rect()
        white_rect = white_wins.get_rect()
        black_rect = black_wins.get_rect()
        game_name = myfont.render('Cowboy Chess', False, (1,1,1))
        game_name_rect = game_name.get_rect(center = (400, 400))
        game_message = myfont2.render('Press SPACE to begin', False, (1,1,1))
        game_message_rect = game_message.get_rect(center = (400, 600))
        while True:
                # show methods
            if game_active:
                game.show_bg(screen)
                game.show_last_move(screen)
                game.show_moves(screen)
                game.show_pieces(screen)

                game.show_hover(screen)
                
                if dragger.dragging:
                    dragger.update_blit(screen)
            elif game_new:
                screen.blit(intro, intro_rect)
                
            else:
                # game over screen
                if winner == 'white':
                    screen.blit(white_wins, white_rect)
                elif winner == 'black':
                    screen.blit(black_wins, black_rect)
                else: 
                    screen.blit(stalemate, stalemate_rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()                    
                if game_active:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # click
                        dragger.update_mouse(event.pos)

                        clicked_row = dragger.mousey // sqsize
                        clicked_col = dragger.mousex // sqsize

                        if board.squares[clicked_row][clicked_col].has_piece():
                            # does clicked square have a piece?
                            piece = board.squares[clicked_row][clicked_col].piece
                            # valid piece colour?
                            if piece.color == game.next_player:
                                # Clear before valid move
                                piece.clear_moves()
                                # Calculate valid move
                                board.calc_moves(piece, clicked_row, clicked_col)
                                dragger.save_initial(event.pos)
                                dragger.drag_piece(piece)
                                # show methods
                                game.show_bg(screen)
                                game.show_moves(screen)
                                game.show_pieces(screen)

                            

                    elif event.type == pygame.MOUSEMOTION:
                        motion_row = event.pos[1] // sqsize
                        motion_col = event.pos[0] // sqsize
                        # motion
                        game.set_hover(motion_row, motion_col)

                        if dragger.dragging:
                            dragger.update_mouse(event.pos)
                            # show methods
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)
                            game.show_hover(screen)
                            dragger.update_blit(screen)

                    elif event.type == pygame.MOUSEBUTTONUP:
                        # release
                        if dragger.dragging:
                            dragger.update_mouse(event.pos)

                            released_row = dragger.mousey // sqsize
                            released_col = dragger.mousex // sqsize

                            initial = Square(dragger.initial_row, dragger.initial_col)
                            final = Square(released_row, released_col)
                            move = Move(initial, final)

                            # valid move?
                            if board.valid_move(dragger.piece, move):
                                # normal capture
                                captured = board.squares[released_row][released_col].has_piece()

                                board.move(dragger.piece, move)

                                board.set_true_en_passant(dragger.piece)

                                # sounds
                                game.play_sound(captured)
                                # show methods
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_pieces(screen)
                                # next turn
                                game.next_turn()
                                
                                    

                                if game.game_over():
                                    if game.checked():
                                        if game.next_player == 'white':
                                            winner = "black"
                                        else: winner = 'white'
                                    else:
                                        winner = "stalemate"
                                    game_active = False
                        dragger.undrag_piece()


                    # key press
                    elif event.type == pygame.KEYDOWN:

                        if event.key == pygame.K_t:
                            # changing themes
                            game.change_theme()

                        if event.key == pygame.K_r:
                            # reset
                            game.reset()
                            game = self.game
                            board = self.game.board
                            dragger = self.game.dragger
                elif game_new:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            game_new = False
                            game_active = True
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            game_over = False
                            game_new = True
                            game.reset()
                            game = self.game
                            board = self.game.board
                            dragger = self.game.dragger
                ##elif tutorial:
                    #game.show_bg(screen)

            
            pygame.display.update()
main = Main()
main.mainloop()

