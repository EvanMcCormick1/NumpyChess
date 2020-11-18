import numpy as np
import copy
import turtle


class Chess:
    turn = 1
    movelist = []
    playing = True
    chessboard = np.zeros((8, 8), dtype='int32')
    saveboard = copy.deepcopy(chessboard)
    fileDict = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    pieceDict = {10: 'R', 11: 'N', 12: 'B', 13: 'Q', 14: 'K', 15: 'P', 20: 'R', 21: 'N', 22: 'B', 23: 'Q', 24: 'K',
                 25: 'P', 0: 0}
    imageDict = {10: 'BRook.gif', 11: 'BKnight.gif', 12: 'BBishop.gif', 13: "BQueen.gif", 14: 'BKing.gif',
                 15: 'BPawn.gif', 20: 'WRook.gif', 21: 'WKnight.gif', 22: 'WBishop.gif', 23: 'WQueen.gif',
                 24: 'WKing.gif', 25: 'WPawn.gif'}

    def __init__(self):
        self.chessboard[1, :] = 25
        self.chessboard[-2, :] = 15
        for x in range(5):
            self.chessboard[0, x] = 20 + x
            self.chessboard[-1, x] = 10 + x
        for x in range(3):
            self.chessboard[0, -(x + 1)] = 20 + x
            self.chessboard[-1, -(x + 1)] = 10 + x
        self.saveboard = copy.deepcopy(self.chessboard)
        self.mainloop()

    def move_converter(self, start, target):
        move = [start, target]

        if self.is_opponent_piece(target):
            move += [True]
        else:
            move += [False]

        move += [self.pieceDict[self.chessboard[start[0], start[1]]]]
        return move

    def square_converter(self, prompt="Type the coordinates of the piece you would like to move!"):
        while True:
            string = input(prompt)
            if len(string) == 2 and (string[0] in self.fileDict.keys()) and int(string[1]) > 0 and int(string[1]) <= 8:
                coord = []
                coord += [int(string[1]) - 1]
                coord += [self.fileDict[string[0]]]
                return coord
            else:
                print("That's not a valid coordinate!")

    def is_legal_move(self, move):
        if move[3] == 'N':
            return self.legal_knight(move)
        elif move[3] == 'B':
            return self.legal_bishop(move)
        elif move[3] == 'R':
            return self.legal_rook(move)
        elif move[3] == 'Q':
            return self.legal_queen(move)
        elif move[3] == 'K':
            return self.legal_king(move)
        elif move[3] == 'P':
            return self.legal_pawn(move)
        else:
            return False

    def legal_knight(self, move):
        start, target = move[0], move[1]
        if abs(start[0] - target[0]) in [1, 2] and abs(start[1] - target[1]) in [1, 2] and (
                abs(start[1] - target[1]) != abs(start[0] - target[0])) and (
                self.are_enemies(start, target) or self.is_empty(target)):
            return True
        else:
            return False

    def legal_bishop(self, move):
        start, target = move[0], move[1]
        if self.is_diagonal(start, target) and self.no_pieces_between(start, target) and (
                self.are_enemies(start, target) or self.is_empty(target)):
            return True
        else:
            return False

    def legal_rook(self, move):
        start, target = move[0], move[1]
        if (target[1] == start[1] or target[0] == start[0]) and self.no_pieces_between(start, target) and (
                self.are_enemies(start, target) or self.is_empty(target)):
            return True
        else:
            return False

    def legal_queen(self, move):
        start, target = move[0], move[1]
        if (self.is_diagonal(start, target) or target[1] == start[1] or target[0] == start[0]) and (
                self.are_enemies(start, target) or self.is_empty(target)) and self.no_pieces_between(start, target):
            return True
        else:
            return False

    def legal_king(self, move):
        start, target = move[0], move[1]
        if self.is_in_one(start, target) and (self.are_enemies(start, target) or self.is_empty(target)):
            return True
        else:
            return False

    def legal_pawn(self, move):
        start, target = move[0], move[1]

        if self.is_forward(start, target):
            if move[2] and self.is_pawn_capture(start, target):
                return True
            elif self.is_empty(target) and start[1] == target[1]:
                if self.is_in_one(start, target) or (
                        (start[0] == 1 or start[0] == 6) and abs(start[0] - target[0]) <= 2):
                    return True
            return False
        return False

    def king_dies(self, move):
        result = False
        self.change_board(move)
        king = list(self.array_index(10 * (self.turn % 2) + 14)[0])
        self.turn += 1
        for x in range(8):
            for y in range(8):
                start = [x, y]
                if self.is_my_own_piece(start):
                    move = self.move_converter(start, king)
                    if self.is_legal_move(move):
                        result = True
        self.chessboard = copy.deepcopy(self.saveboard)
        self.turn -= 1
        return result

    def is_check(self):
        result = False
        king = list(self.array_index(10 * ((self.turn) % 2) + 14)[0])
        for x in range(8):
            for y in range(8):
                start = [x, y]
                if self.is_opponent_piece(start):
                    if self.is_legal_move(self.move_converter(start, king)):
                        result = True
        return result

    def whats_checking(self):
        checks = []
        king = list(self.array_index(10 * ((self.turn) % 2) + 14)[0])
        for x in range(8):
            for y in range(8):
                start = [x, y]
                if self.is_opponent_piece(start):
                    move = self.move_converter(start, king)
                    if self.is_legal_move(move):
                        checks += [move]
        return checks

    def is_checkmate(self):
        checks = self.whats_checking()
        king = list(self.array_index(10 * ((self.turn) % 2) + 14)[0])
        friendlySquares = []
        for x in range(8):
            for y in range(8):
                square = [x, y]
                if self.is_in_one(king, square):
                    self.escape_route = self.move_converter(king, square)
                    if self.is_legal_move(self.escape_route) and (not self.king_dies(self.escape_route)):
                        return False
                if self.is_my_own_piece(square):
                    friendlySquares += [square]
        if len(checks) == 2:
            print('Double Check.', end=' ')
            return True
        for square in friendlySquares:
            move = self.move_converter(square, checks[0][0])
            if self.is_legal_move(move) and not self.king_dies(move):
                return False
        if checks[0][3] == 'N':
            return True
        blocks = self.squares_between(checks[0][0], king)
        if not blocks:
            return True
        if isinstance(blocks[0], int):
            for start in friendlySquares:
                block = self.move_converter(start, blocks)
                if self.is_legal_move(block) and not self.king_dies(block):
                    return False
        else:
            for target in blocks:
                for start in friendlySquares:
                    block = self.move_converter(start, target)
                    if self.is_legal_move(block) and not self.king_dies(block):
                        return False
        return True

    def array_index(self, val):
        return np.vstack(np.where(self.chessboard == val)).T

    def change_board(self, move):
        start, target = move[0], move[1]
        val = self.chessboard[start[0], start[1]]
        self.chessboard[target[0], target[1]] = val
        self.chessboard[start[0], start[1]] = 0

    def move_logger(self, move):
        val = self.chessboard[move[0][0], move[0][1]]
        piece = self.pieceDict[val]
        takes = ""
        if move[2]:
            takes = "x"
        file = chr(ord('a') + move[1][1])
        rank = str(move[1][0] + 1)
        x = str(self.turn) + ". " + piece + takes + file + rank
        return x

    def squares_between(self, start, target):
        a = start[0]
        b = start[1]
        c = target[0]
        d = target[1]
        squares = []
        if d == b:
            for x in range(min([c, a]), max([c, a]) + 1):
                squares += [[x, b]]
        elif a == c:
            for x in range(min([d, b]), max([d, b]) + 1):
                squares += [[a, x]]
        elif abs(c - a) == abs(d - b):
            x, y = a, b
            square = [[x, y]]
            squares += square
            while x != c and y != d:
                if x > c:
                    x -= 1
                else:
                    x += 1
                if y > d:
                    y -= 1
                else:
                    y += 1
                square = [[x, y]]
                squares += square
        squaresBetween = squares[1:-1]
        return squaresBetween

    def no_pieces_between(self, start, target):
        squaresBetween = self.squares_between(start, target)
        vals = []
        if squaresBetween == []:
            return True
        if isinstance(squaresBetween[0], int):
            vals += [self.chessboard[squaresBetween[0], squaresBetween[1]]]
        else:
            for i in squaresBetween:
                vals += [self.chessboard[i[0], i[1]]]
        if max(vals) == 0:
            return True
        else:
            return False

    def not_my_own_piece(self, target):
        return not self.is_my_own_piece(target)

    def is_my_own_piece(self, square):
        base = 10 * (self.turn % 2) + 10
        piece = self.chessboard[square[0], square[1]]
        if piece >= base and piece < (base + 10):
            return True
        else:
            return False

    def is_opponent_piece(self, target):
        if self.is_my_own_piece(target) or self.is_empty(target):
            return False
        else:
            return True

    def is_empty(self, targetSquare):
        if self.chessboard[targetSquare[0], targetSquare[1]] == 0:
            return True
        else:
            return False

    def are_enemies(self, start, target):
        targpiece = self.chessboard[target[0], target[1]]
        mypiece = self.chessboard[start[0], start[1]]
        if targpiece // 10 != mypiece // 10 and targpiece != 0:
            return True
        else:
            return False

    def is_forward(self, pawn_start, pawn_target):
        if ((2 * (self.turn % 2) - 1) * (pawn_target[0] - pawn_start[0])) > 0:
            return True
        else:
            return False

    def is_diagonal(self, start, target):
        if abs(target[0] - start[0]) == abs(target[1] - start[1]):
            return True
        else:
            return False

    def is_pawn_capture(self, start, target):
        if self.is_diagonal(start, target) and self.is_in_one(start, target) and self.are_enemies(start, target):
            return True
        else:
            return False

    def is_in_one(self, start, target):
        if abs(start[0] - target[0]) <= 1 and abs(start[1] - target[1]) <= 1:
            return True
        else:
            return False

    def get_piece_at(self, x, y):
        return self.chessboard[x, y]

    def mainloop(self):
        self.plot_board()
        while self.playing:
            startingSquare = self.square_converter()
            while self.not_my_own_piece(startingSquare):
                print("Your piece isn't there!")
                startingSquare = self.square_converter()
            targetingSquare = self.square_converter(prompt="Type the coordinates of the square to move it to.")
            movement = self.move_converter(startingSquare, targetingSquare)
            if self.is_legal_move(movement):
                if self.king_dies(movement):
                    print("That's' not a valid move, you can't hang your king!")
                else:
                    x = [self.move_logger(movement)]
                    self.movelist += x
                    self.change_board(movement)
                    self.saveboard = copy.deepcopy(self.chessboard)
                    self.turn += 1
                    self.plot_board()
                    if self.is_check():
                        print('Check!')
                        if self.is_checkmate():
                            print('Checkmate!')
                            self.playing = False
            else:
                print("That's not a valid move!")

    def draw(self,pen):
        for i in range(4):
            pen.forward(60)
            pen.left(90)

    def stamp_piece(self, piece,pen,sc):
        if piece:
            image = 'ChessImages/' + self.imageDict[piece]
            if image not in sc.getshapes():
                sc.addshape(image)
            pen.shape(image)
            return pen.stamp()

    def plot_board(self):
        turtle.TurtleScreen._RUNNING=True
        sc = turtle.Screen()
        sc.tracer(0, 0)
        pen = turtle.Turtle()
        sc.setup(600, 600)
        pen.speed(100)
        for i in range(8):
            pen.up()
            pen.setpos(-240, -240 + 60 * i)
            pen.down()
            for j in range(8):
                if (i + j) % 2 == 0:
                    col = '#006600'

                else:
                    col = 'white'
                pen.fillcolor(col)
                pen.begin_fill()
                self.draw(pen)
                pen.forward(60)
                pen.up()
                pen.end_fill()
        self.fill_board(pen, sc)
        sc.update()
        pen.hideturtle()
        sc.exitonclick()

    def fill_board(self,pen,sc):
        i=(self.turn+1)%2
        for x in range(8):
            for y in range(8):
                pen.setpos(-210 + 60 * x, -210 + 60 * y)
                self.stamp_piece(self.chessboard[(-2*i+1)*y-i, (-2*i+1)*x-i],pen,sc)


Chessgame = Chess()
