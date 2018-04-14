from abc import ABC, abstractmethod
from copy import deepcopy

class Board():
    def __init__(self):
        self.grid = [ [0 for x in range(8)] for x in range(8) ] #grid[r][c] = (row, column)
        self.white_king = King(7, 4, True)
        self.black_king = King(0, 4, False)
        self.white_pieces = [self.white_king]
        self.black_pieces = [self.black_king]
        self.grid[7][4] = self.white_king
        self.grid[0][4] = self.black_king
        self.turn = 0 #0 for white, 1 for black
    
    def initialize_board(self):
        for i in range(0, 8):
            self.grid[1][i] = Pawn(1, i, False)
            self.grid[6][i] = Pawn(6, i, True)
            self.black_pieces.append(self.grid[1][i])
            self.white_pieces.append(self.grid[6][i])
        for i in range(0, 14, 7):
            self.grid[0][i] = Rook(0, i, False)
            self.grid[7][i] = Rook(7, i, True)
            self.black_pieces.append(self.grid[0][i])
            self.white_pieces.append(self.grid[7][i])
        for i in range(1, 11, 5):
            self.grid[0][i] = Knight(0, i, False)
            self.grid[7][i] = Knight(7, i, True)
            self.black_pieces.append(self.grid[0][i])
            self.white_pieces.append(self.grid[7][i])
        for i in range(2, 8, 3):
            self.grid[0][i] = Bishop(0, i, False)
            self.grid[7][i] = Bishop(7, i, True)
            self.black_pieces.append(self.grid[0][i])
            self.white_pieces.append(self.grid[7][i])
        self.grid[0][3] = Queen(0, 3, False)
        self.grid[7][3] = Queen(7, 3, True)
        self.black_pieces.append(self.grid[0][3])
        self.white_pieces.append(self.grid[7][3])
        
    def in_check(self):
        if self.turn == 0:
            king = self.white_king
            opponent_pieces = self.black_pieces
        else:
            king = self.black_king
            opponent_pieces = self.white_pieces
        for piece in opponent_pieces:
            if piece.can_attack( (king.row, king.column), self ):
                return True
        return False

    def game_ended(self):
        if self.turn == 0:
            my_pieces = self.white_pieces
        else:
            my_pieces = self.black_pieces
        for piece in my_pieces:
            if len(piece.get_moves(self)) > 0:
                return False
        if self.in_check():
            return "Checkmate"
        return "Stalemate"

    def evaluate_position(self):
        return self.player_score(self.white_pieces) - self.player_score(self.black_pieces)

    def player_score(self, pieces):
        score = 0
        for piece in pieces:
            if piece.piece_type == "Queen":
                score += 9
            elif piece.piece_type == "Rook":
                score += 5
            elif piece.piece_type == "Bishop":
                score += 3.25
            elif piece.piece_type == "Knight":
                score += 3.25
            elif piece.piece_type == "Pawn":
                score += 1
        return score
        
        
class Chess_piece(ABC):
    def __init__(self, row, column, is_white):
        self.row = row
        self.column = column
        self.is_white = is_white
        self.possible_moves = []
        self.has_moved = False
        self.can_be_taken_en_passant = False

    @abstractmethod
    def get_moves(self, board):
        pass

    @abstractmethod
    def can_attack(self, position, board):
        pass

    def move(self, position, board):
        b = deepcopy(board)
        b.grid[self.row][self.column].row = position[0]
        b.grid[self.row][self.column].column = position[1]
        b.grid[self.row][self.column].has_moved = True
        if b.grid[position[0]][position[1]] != 0:
            if self.is_white:
                b.black_pieces.remove(b.grid[position[0]][position[1]])
            else:
                b.white_pieces.remove(b.grid[position[0]][position[1]])
        b.grid[position[0]][position[1]] = b.grid[self.row][self.column]
        b.grid[self.row][self.column] = 0
        if self.is_white:
            opponent_pieces = b.black_pieces
        else:
            opponent_pieces = b.white_pieces
        for piece in opponent_pieces:
            piece.can_be_taken_en_passant = False
        b.turn = (b.turn + 1) % 2
        return b

    def is_legal(self, position, board):
        temp = board.grid[position[0]][position[1]]
        if temp != 0:
            if self.is_white:
                opponent_pieces = board.black_pieces
            else:
                opponent_pieces = board.white_pieces
            opponent_pieces.remove(temp)
        board.grid[position[0]][position[1]] = self
        board.grid[self.row][self.column] = 0
        is_legal = not board.in_check()
        board.grid[position[0]][position[1]] = temp
        if temp != 0:
            opponent_pieces.append(temp)
        board.grid[self.row][self.column] = self
        return is_legal

    def get_diagonals(self, board):
        coordinates = []
        for i in range(-1, 3, 2):
            col = self.column + i
            row = self.row + i
            while col <= 7 and col >= 0 and row <= 7 and row >= 0:
                if board.grid[row][col] != 0:
                    if board.grid[row][col].is_white ^ self.is_white:
                        coordinates.append( (row, col) )
                    break
                else:
                    coordinates.append( (row, col) )
                col += i
                row += i
            col = self.column - i
            row = self.row + i
            while col <= 7 and col >= 0 and row <= 7 and row >= 0:
                if board.grid[row][col] != 0:
                    if board.grid[row][col].is_white ^ self.is_white:
                        coordinates.append( (row, col) )
                    break
                else:
                    coordinates.append( (row, col) )
                col -= i
                row += i
        return coordinates

    def get_orthogonals(self, board):
        coordinates = []
        for i in range(-1, 3, 2):
            col = self.column + i
            row = self.row + i
            #horizontal coordinates
            while col <= 7 and col >= 0:
                if board.grid[self.row][col] != 0:
                    if board.grid[self.row][col].is_white ^ self.is_white:
                        coordinates.append( (self.row, col))
                    break
                else:
                    coordinates.append( (self.row, col) )
                col += i
            #vertical coordinates
            while row <= 7 and row >= 0:
                if board.grid[row][self.column] != 0:
                    if board.grid[row][self.column].is_white ^ self.is_white:
                        coordinates.append( (row, self.column) )
                    break
                else:
                    coordinates.append( (row, self.column) )
                row += i
        return coordinates
        
    
class King(Chess_piece):
    piece_type = "King"
    def get_moves(self, board):
        coordinates = []
        for i in range(self.row - 1, self.row + 2):
            for j in range(self.column - 1, self.column + 2):
                if ( (i != self.row or j != self.column) and i >= 0 and i <= 7 and j >= 0 and j <= 7):
                    coordinates.append( (i, j) )
        if self.is_white:
            opponent_pieces = board.black_pieces
        else:
            opponent_pieces = board.white_pieces
        valid_coordinates = []
        for c in coordinates:
            if board.grid[c[0]][c[1]] != 0 and not (board.grid[c[0]][c[1]].is_white ^ self.is_white):
                continue
            for piece in opponent_pieces:
                if piece.can_attack(c, board):
                    break
            else:
                valid_coordinates.append(c)
        if self.can_castle_kingside(board):
            valid_coordinates.append((self.row, 6, "Kingside"))
        if self.can_castle_queenside(board):
            valid_coordinates.append((self.row, 2, "Queenside"))
        return valid_coordinates
    
    def can_attack(self, position, board):
        return abs(self.row - position[0]) <= 1 and abs(self.column - position[1]) <= 1

    def can_castle_kingside(self, board):
        if not self.has_moved and board.grid[self.row][7] != 0 and not board.grid[self.row][7].has_moved and not board.in_check() and \
            board.grid[self.row][6] == 0 and board.grid[self.row][5] == 0:
            if self.is_white:
                opponent_pieces = board.black_pieces
            else:
                opponent_pieces = board.white_pieces
            for piece in opponent_pieces:
                if piece.can_attack((self.row, 5), board) or piece.can_attack((self.row, 6), board):
                    return False
            return True
        return False

    def can_castle_queenside(self, board):
        if not self.has_moved and board.grid[self.row][0] != 0 and not board.grid[self.row][0].has_moved and not board.in_check() and \
            board.grid[self.row][1] == 0 and board.grid[self.row][2] == 0:
            if self.is_white:
                opponent_pieces = board.black_pieces
            else:
                opponent_pieces = board.white_pieces
            for piece in opponent_pieces:
                if piece.can_attack((self.row, 1), board) or piece.can_attack((self.row, 2), board):
                    return False
            return True
        return False

    def move(self, position, board):
        if len(position) == 2:
            return super().move(position, board)
        b = deepcopy(board)
        b.grid[self.row][self.column].has_moved = True
        if position[2] == "Kingside":
            b.grid[self.row][7].column -= 2
            b.grid[self.row][7].has_moved = True
            b.grid[self.row][self.column + 1] = b.grid[self.row][7]
            b.grid[self.row][7] = 0
        else:
            b.grid[self.row][0].column += 3
            b.grid[self.row][0].has_moved = True
            b.grid[self.row][self.column - 1] = b.grid[self.row][0]
            b.grid[self.row][0] = 0
        b.grid[self.row][self.column].column = position[1]
        b.grid[position[0]][position[1]] = b.grid[self.row][self.column]
        b.grid[self.row][self.column] = 0
        if self.is_white:
            opponent_pieces = b.black_pieces
        else:
            opponent_pieces = b.white_pieces
        for piece in opponent_pieces:
            piece.can_be_taken_en_passant = False
        b.turn = (b.turn + 1) % 2
        return b
            
class Queen(Chess_piece):
    piece_type = "Queen"
    def get_moves(self, board):
        coordinates = self.get_diagonals(board)
        coordinates += self.get_orthogonals(board)
        valid_coordinates = []
        for c in coordinates:
            if self.is_legal(c, board):
                valid_coordinates.append(c)
        return valid_coordinates

    def can_attack(self, position, board):
        if position in self.get_diagonals(board):
            return True
        return position in self.get_orthogonals(board)

class Bishop(Chess_piece):
    piece_type = "Bishop"
    def get_moves(self, board):
        coordinates = self.get_diagonals(board)
        valid_coordinates = []
        for c in coordinates:
            if self.is_legal(c, board):
                valid_coordinates.append(c)
        return valid_coordinates

    def can_attack(self, position, board):
        return position in self.get_diagonals(board)

class Rook(Chess_piece):
    piece_type = "Rook"
    def get_moves(self, board):
        coordinates = self.get_orthogonals(board)
        valid_coordinates = []
        for c in coordinates:
            if self.is_legal(c, board):
                valid_coordinates.append(c)
        return valid_coordinates

    def can_attack(self, position, board):
        return position in self.get_orthogonals(board)

class Pawn(Chess_piece):
    piece_type = "Pawn"
    def get_moves(self, board):
        if self.is_white:
            i = -1
        else:
            i = 1
        coordinates = []
        if board.grid[self.row + i][self.column] == 0:
            if (self.row + i == 0 and self.is_white) or (self.row + i == 7 and not self.is_white):
                coordinates += [(self.row + i, self.column, "Queen"), (self.row + i, self.column, "Rook"),
                                (self.row + i, self.column, "Bishop"), (self.row + i, self.column, "Knight")]
            else:
                coordinates.append((self.row + i, self.column))
            if not self.has_moved and board.grid[self.row + 2 * i][self.column] == 0:
                coordinates.append((self.row + 2 * i, self.column, "Double Move"))
        if self.column > 0 and board.grid[self.row + i][self.column - 1] != 0 and (board.grid[self.row + i][self.column - 1].is_white ^ self.is_white):
            coordinates.append((self.row + i, self.column - 1))
        if self.column < 7 and board.grid[self.row + i][self.column + 1] != 0 and (board.grid[self.row + i][self.column + 1].is_white ^ self.is_white):
            coordinates.append((self.row + i, self.column + 1))
        if self.column > 0 and board.grid[self.row][self.column - 1] != 0 and board.grid[self.row][self.column - 1].can_be_taken_en_passant and (board.grid[self.row][self.column - 1].is_white ^ self.is_white):
            coordinates.append((self.row + i, self.column - 1, "En Passant"))
        if self.column < 7 and board.grid[self.row][self.column + 1] != 0 and board.grid[self.row][self.column + 1].can_be_taken_en_passant and (board.grid[self.row][self.column + 1].is_white ^ self.is_white):
            coordinates.append((self.row + i, self.column - 1, "En Passant"))
        valid_coordinates = []
        for c in coordinates:
            if self.is_legal(c, board):
                valid_coordinates.append(c)
        return valid_coordinates

    def can_attack(self, position, board):
        if self.is_white:
            i = -1
        else:
            i = 1
        return position[0] == self.row + i and (position[1] == self.column + 1 or position[1] == self.column - 1)

    def move(self, position, board):
        if len(position) == 2:
            return super().move(position, board)
        b = deepcopy(board)
        if position[2] == "Double Move":
            self.can_be_taken_en_passant = True
            return super().move(position, board)
        elif position[2] == "En Passant":
            b.grid[self.row][self.column].row = position[0]
            b.grid[self.row][self.column].column = position[1]
            b.grid[self.row][self.column].has_moved = True
            b.grid[self.row][self.column] = 0
            if self.is_white:
                b.black_pieces.remove(b.grid[self.row][position[1]])
            else:
                b.white_pieces.remove(b.grid[self.row][position[1]])
            b.grid[self.row][position[1]] = 0
            b.grid[position[0]][position[1]] = self
        else:
            b.grid[self.row][self.column] = 0
            if self.is_white:
                my_pieces = b.white_pieces
            else:
                my_pieces = b.black_pieces
            if position[2] == "Queen":
                b.grid[position[0]][position[1]] = Queen(position[0], position[1], self.is_white)
            elif position[2] == "Rook":
                b.grid[position[0]][position[1]] = Rook(position[0], position[1], self.is_white)
            elif position[2] == "Bishop":
                b.grid[position[0]][position[1]] = Bishop(position[0], position[1], self.is_white)
            else:
                b.grid[position[0]][position[1]] = Knight(position[0], position[1], self.is_white)
            my_pieces.append(b.grid[position[0]][position[1]])
        if self.is_white:
            opponent_pieces = b.black_pieces
        else:
            opponent_pieces = b.white_pieces
        for piece in opponent_pieces:
            piece.can_be_taken_en_passant = False
        b.turn = (b.turn + 1) % 2
        return b

class Knight(Chess_piece):
    piece_type = "Knight"
    def get_moves(self, board):
        r = self.row
        c = self.column
        coordinates = [(r+1, c+2), (r-1, c+2), (r+1, c-2), (r-1, c-2), (r+2, c+1), (r+2, c-1), (r-2, c+1), (r-2, c-1)]
        valid_coordinates = []
        for c in coordinates:
            if c[0] >= 0 and c[0] < 8 and c[1] >= 0 and c[1] < 8 and (board.grid[c[0]][c[1]] == 0 or \
            (board.grid[c[0]][c[1]].is_white ^ self.is_white))and self.is_legal(c, board):
                valid_coordinates.append(c)
        return valid_coordinates

    def can_attack(self, position, board):
        r = self.row
        c = self.column
        coordinates = [(r+1, c+2), (r-1, c+2), (r+1, c-2), (r-1, c-2), (r+2, c+1), (r+2, c-1), (r-2, c+1), (r-2, c-1)]
        return position in coordinates

def mini_max(board_position, depth, maximizing_player):
    #depth must be even number to get a whole number of plies
    game_ended = board_position.game_ended()
    if game_ended:
        if game_ended == "Stalemate":
            return 0
        elif board_position.turn == 0:
            return -10000
        else:
            return 10000
    if depth == 0:
        return board_position.evaluate_position()
    if board_position.turn == 0:
        my_pieces = board_position.white_pieces
    else:
        my_pieces = board_position.black_pieces
    move_values = []
    if maximizing_player:
        for piece in my_pieces:
            possible_moves = piece.get_moves(board_position)
            for position in possible_moves:
                move_values.append(mini_max(piece.move(position, board_position), depth - 1, False))
        return max(move_values)
    else:
        for piece in my_pieces:
            possible_moves = piece.get_moves(board_position)
            for position in possible_moves:
                move_values.append(mini_max(piece.move(position, board_position), depth - 1, True))
        return min(move_values)
        
        

board = Board()
board.initialize_board()

            
    


                  
