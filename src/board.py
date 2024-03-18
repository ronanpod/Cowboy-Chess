# generates a new board 

from const import *
from square import Square
from piece import *
from move import Move
from sound import Sound
import copy
import os

class Board:

    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(cols)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def move(self, piece, move, testing = False):
        initial = move.initial
        final = move.final

        en_passant_empty = self.squares[final.row][final.col].isempty()
        cowboy_time = self.squares[final.row][final.col].has_team_piece(piece.color)
        #console board move update
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        
        # en passant capture
        if isinstance(piece, Pawn):
            diff = final.col - initial.col
            if diff!=0 and cowboy_time:
                self.squares[final.row][final.col].piece = Cowboy(piece.color)
                if not testing:
                    sound = Sound(os.path.join('assets/sounds/439191__javapimp__kara-yeehaw-2 (1).ogg'))
                    sound.play()
            elif diff != 0 and en_passant_empty:
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece
                if not testing:
                    sound = Sound(os.path.join('assets/sounds/capture.wav'))
                    sound.play()
        
        
            # pawn promotion 
            else:
                self.check_promotion(piece, final)
        

        # king castling
        if isinstance(piece, King):
            if self.castling(initial, final) and not testing:
                diff = final.col - initial.col 
                rook = piece.left_rook if (diff<0) else piece.right_rook
                self.move(rook, rook.moves[-1])

        piece.moved = True
        # clear valid moves
        piece.clear_moves()
        #set last move
        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves
    
    def check_promotion(self, piece, final):
        if final.row == 0 or final.row == 7: 
            self.squares[final.row][final.col].piece = Queen(piece.color)

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2
    

    def set_true_en_passant(self, piece):

        if not isinstance(piece, Pawn):
            return
        for row in range(rows):
            for col in range(cols):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False

        piece.en_passant = True

        
    

    def in_check(self, piece, move):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move(temp_piece, move, testing = True)

        for row in range(rows):
            for col in range(cols):
                if temp_board.squares[row][col].has_rival_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    if isinstance(p, King):
                    # king kissing
                        adjs = [(row -1, col + 0), (row +0, col + 1), (row +1, col + 0), (row +0, col + -1), (row -1, col + 1), (row +1, col -1), (row +1, col + 1), (row -1, col -1)]
                        for x in adjs:
                            i,j = x
                            if Square.in_range(i, j):
                                if isinstance(temp_board.squares[i][j].piece, King):
                                    return True
                    temp_board.calc_moves(p, row, col, bool = False)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True
        
                        
        return False
    
    def calc_moves(self, piece, row, col, bool=True):
        '''
        # calculate all possible valid moves of a specific piece on a specific square
        '''

        def pawn_moves():
            steps = 1 if piece.moved else 2
            
            # vertical moves
            # move row is possible move row
            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))
            for move_row in range(start, end, piece.dir):
                if Square.in_range(move_row):
                    if self.squares[move_row][col].isempty():
                        # create intial and final move squares
                        # create new move
                        initial = Square(row, col)
                        final = Square(move_row, col)
                        move = Move(initial, final)

                        # potential checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else: 
                            piece.add_move(move)

                    # blocked
                    else: break
                # not in range
                else: break
            # diagonal moves
            possible_move_row = row + piece.dir
            possible_move_cols = [col-1, col+1]
            for possible_move_col in possible_move_cols:
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_rival_piece(piece.color):
                        # create intial and final move squares
                        # create new move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        move = Move(initial, final)
                        
                        # potential checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else: 
                            piece.add_move(move)
                    # cowboy time
                    elif self.squares[possible_move_row][possible_move_col].has_piece():
                        if isinstance(self.squares[possible_move_row][possible_move_col].piece, Knight):
                            initial = Square(row, col)
                            final_piece = self.squares[possible_move_row][possible_move_col].piece
                            final = Square(possible_move_row, possible_move_col, final_piece)
                            move = Move(initial, final)
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else: 
                                piece.add_move(move)
            # left en passant moves
            r = 3 if piece.color == 'white' else 4
            fr = 2 if piece.color == 'white' else 5
            if Square.in_range(col - 1) and row == r:
                if self.squares[row][col-1].has_rival_piece(piece.color):
                    p = self.squares[row][col-1].piece
                    if isinstance(p, Pawn):
                        if p.en_passant:
                            # initial and final move squares
                            initial = Square(row, col)
                            final = Square(fr, col-1, p)
                            # create new move
                            move = Move(initial, final)

                            # potential checks
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else: 
                                piece.add_move(move)

            # right en passant moves
            if Square.in_range(col + 1) and row == r:
                if self.squares[row][col+1].has_rival_piece(piece.color):
                    p = self.squares[row][col+1].piece
                    if isinstance(p, Pawn):
                        if p.en_passant:
                            # initial and final move squares
                            initial = Square(row, col)
                            final = Square(fr, col+1, p)
                            # create new move
                            move = Move(initial, final)

                            # potential checks
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else: 
                                piece.add_move(move)



        def knight_moves():
            # 8 possible moves
            possible_moves = [(row - 2, col  + 1), (row - 1, col + 2), (row + 1, col + 2), (row + 2, col + 1), (row + 2, col - 1), (row + 1, col - 2), (row - 1, col -2), (row - 2, col - 1)]
            
            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move

            
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_rival(piece.color):
                        # create squares of new move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        
                        # create new move
                        move = Move(initial, final)
                        # potential checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else: 
                                piece.add_move(move)

        def cowboy_moves():
            possible_moves = [(row - 3, col  + 1), (row - 1, col + 3), (row + 1, col + 3), (row + 3, col + 1), (row + 3, col - 1), (row + 1, col - 3), (row - 1, col -3), (row - 3, col - 1), (row - 2, col  + 1), (row - 1, col + 2), (row + 1, col + 2), (row + 2, col + 1), (row + 2, col - 1), (row + 1, col - 2), (row - 1, col -2), (row - 2, col - 1)]                
            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move

            
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_rival(piece.color):
                        # create squares of new move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        
                        # create new move
                        move = Move(initial, final)
                        # potential checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else: 
                                piece.add_move(move)

        def straight_line_moves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                possible_move_row = row + row_incr
                possible_move_col = col + col_incr

                while True:
                    if Square.in_range(possible_move_row, possible_move_col):
                        # create squares of possible new move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        move = Move(initial, final)
                        # empty = continue looping
                        if self.squares[possible_move_row][possible_move_col].isempty():
                            # potential checks
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else: 
                                piece.add_move(move)

                        # has rival piece
                        elif self.squares[possible_move_row][possible_move_col].has_rival_piece(piece.color):
                            # potential checks
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else: 
                                piece.add_move(move)
                            break
                        elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
                            break
                    else: break
                    possible_move_row = possible_move_row + row_incr 
                    possible_move_col = possible_move_col + col_incr
                    
        def king_moves():
            # normal moves
            adjs = [(row -1, col + 0), (row +0, col + 1), (row +1, col + 0), (row +0, col + -1), (row -1, col + 1), (row +1, col -1), (row +1, col + 1), (row -1, col -1)]
            for possible_move in adjs:
                possible_move_row, possible_move_col = possible_move
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_rival(piece.color):
                        # create squares of new move
                        initial = Square(row, col)
                        
                        final = Square(possible_move_row, possible_move_col)
                        # create new move
                        move = Move(initial, final)

                        # potential checks
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else: 
                            piece.add_move(move)

            # castling moves

            if not piece.moved:
                # queen castling
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook, Rook):
                    if not left_rook.moved:
                        for c in range(1, 4):
                            if self.squares[row][c].has_piece():
                                break

                            if c == 3: 
                                # adds left rook to king
                                piece.left_rook = left_rook

                                # rook move
                                initial = Square(row, 0)
                                final = Square(row, 3)
                                moveR = Move(initial, final)
                                left_rook.add_move(moveR)
            
                                # king move
                                initial = Square(row, col)
                                final = Square(row, 2)
                                moveK = Move(initial, final)

                                # castling checks 

                                hop = Square(row, 3)

                                check = Move(initial, hop)

                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(left_rook, moveR):
                                        if not self.in_check(piece, check):
                                            # append new move ro rook
                                            left_rook.add_move(moveR)
                                            # append new move to king
                                            piece.add_move(moveK)                                
                                else: 
                                    # append new move ro rook
                                    left_rook.add_move(moveR)
                                    # append new move to king
                                    piece.add_move(moveK)

                            
                # king castling 
                right_rook = self.squares[row][7].piece
                if isinstance(right_rook, Rook):
                    if not right_rook.moved:
                        for c in range(5, 7):
                            if self.squares[row][c].has_piece():
                                break

                            if c == 6: 
                                # adds right rook to king
                                piece.right_rook = right_rook

                                # rook move
                                initial = Square(row, 7)
                                final = Square(row, 5)
                                moveR = Move(initial, final)
                                
            
                                # king move
                                initial = Square(row, col)
                                final = Square(row, 6)
                                moveK = Move(initial, final)

                                # castling checks 

                                hop = Square(row, 5)

                                check = Move(initial, hop)
                                
                                 # potential checks
                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(right_rook, moveR):
                                        if not self.in_check(piece, check):
                                            # append new move ro rook
                                            right_rook.add_move(moveR)
                                            # append new move to king
                                            piece.add_move(moveK)
                                else: 
                                    # append new move ro rook
                                    right_rook.add_move(moveR)
                                    # append new move to king
                                    piece.add_move(moveK)

        if isinstance(piece, Pawn):
            pawn_moves()

        elif isinstance(piece, Knight):
            knight_moves()

        elif isinstance(piece, Cowboy):
            cowboy_moves()

        elif isinstance(piece, Bishop):
            straight_line_moves([(-1, 1), (1, -1), (1, 1), (-1, -1)])
        
        elif isinstance(piece, Rook):
            straight_line_moves([(-1, 0), (0, 1), (1, 0), (0, -1)])

        elif isinstance(piece, Queen):
            straight_line_moves([(-1, 0), (0, 1), (1, 0), (0, -1), (-1, 1), (1, -1), (1, 1), (-1, -1)])

        elif isinstance(piece, King):
            king_moves()

    def _create(self):
        for row in range(rows):
            for col in range(cols):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)
        # add all pawns
        for col in range(cols):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        # knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))

        # bishops 
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

        # rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))
        
        # queens
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))

        # kings
        self.squares[row_other][4] = Square(row_other, 4, King(color))
        