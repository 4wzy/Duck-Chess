from abc import abstractmethod
from tkinter import *
from PIL import Image as PILImage
from PIL import ImageTk

# To do:

# Add is_check() method using create_all_possible_moves
# Do this by adding an is_attacking attribute to each piece with a list of the names of pieces from possible_positions
# If king is found in any of those is_attacking pieces (add all of them to a single list or something)
# There is check.
# To find out if the move the player tries to make is also in check, change the position of the king (not visually displayed)
# (so don't call redraw_board) and then use the same function.

# Add is_checkmate() method by checking if all of the positions around the king lead to check
# AND no move can be made to block the checkmate (may be harder)


current_player = -1
score = {"p1": 0, "p2": 0}
# This list will be used to check where the player is moving to, so it will contain a max of 2 elements
squares_clicked_on = []
piece_moves = []


class Game:
    def __init__(self, p1, p2):
        self.board = []
        self.squares = []
        self.p1 = Player(p1, -1)
        self.p2 = Player(p2, 1)
        self.winner = 0
        self.create_board()
        self.current_player = self.p1.colour
        global current_player
        # self.create_possible_moves_all_pieces()

    def create_board(self):
        global transparent_image
        for i in range(8):
            self.board.append([])
            self.squares.append([])
            for j in range(8):
                self.board[i].append(Piece("None", None, 0, [i, j]))
                self.squares[i].append(
                    Button(
                        image=transparent_image,
                        height=60,
                        width=60,
                        command=lambda i=i, j=j: self.check_move(game.board[i][j].position)
                    ))
                self.squares[i][j].grid(row=i, column=j)

        # Add pieces to the actual board
        self.board[0][0] = self.p2.pieces[8]
        self.board[0][1] = self.p2.pieces[10]
        self.board[0][2] = self.p2.pieces[12]
        self.board[0][3] = self.p2.pieces[14]
        self.board[0][4] = self.p2.pieces[15]
        self.board[0][5] = self.p2.pieces[13]
        self.board[0][6] = self.p2.pieces[11]
        self.board[0][7] = self.p2.pieces[9]
        for i in range(8):
            self.board[1][i] = self.p2.pieces[i]

        self.board[7][0] = self.p1.pieces[8]
        self.board[7][1] = self.p1.pieces[10]
        self.board[7][2] = self.p1.pieces[12]
        self.board[7][3] = self.p1.pieces[14]
        self.board[7][4] = self.p1.pieces[15]
        self.board[7][5] = self.p1.pieces[13]
        self.board[7][6] = self.p1.pieces[11]
        self.board[7][7] = self.p1.pieces[9]
        for i in range(8):
            self.board[6][i] = self.p1.pieces[i]

    def redraw_board(self, selected_square, highlight):
        global transparent_image
        for i in range(8):
            for j in range(8):
                if game.board[i][j].image is not None:
                    self.squares[i][j].config(
                        image=game.board[i][j].image,
                        height=60,
                        width=60,
                        command=lambda i=i, j=j: self.check_move(game.board[i][j].position)
                    )
                else:
                    self.squares[i][j].config(
                        image=transparent_image,
                        height=60,
                        width=60,
                        command=lambda i=i, j=j: self.check_move(game.board[i][j].position)
                    )

                # The following code is for hiding the possible moves, which are shown when creating possible moves
                if not highlight:
                    self.squares[i][j].config(bg="SystemButtonFace")

        if selected_square is not None and highlight:
            # If the player has selected a piece to move and it is not the square to move the piece to
            self.squares[selected_square[0]][selected_square[1]].config(bg="orange")
        if selected_square is not None and not highlight:
            self.squares[selected_square[0]][selected_square[1]].config(bg="SystemButtonFace")

    # Check if a piece can move to a square on the board
    def check_move(self, position):
        global squares_clicked_on
        global transparent_image
        global current_player
        global piece_moves
        print(position)
        piece = self.board[position[0]][position[1]]
        print(piece.name)
        # print(piece.possible_moves)

        if piece.direction == current_player or piece.direction == 0 or (
                piece.direction != current_player and len(squares_clicked_on) == 1):
            # If the player has clicked of their pieces to select, or has clicked the square to move one of their pieces to

            piece.possible_moves = []
            piece.create_possible_moves(self.board, True)

            if len(squares_clicked_on) == 1 and piece.position == squares_clicked_on[0]:
                # If the player has clicked on the same square as the square selected to move to, allow them to rechoose
                self.redraw_board(squares_clicked_on[0], False)
                squares_clicked_on = []
                piece_moves = []
            else:
                if len(squares_clicked_on) == 0 and piece.name != "None":
                    # If the player has clicked on a valid piece of theirs to select
                    squares_clicked_on.append(position)
                    self.redraw_board(squares_clicked_on[0], True)
                    piece_moves.append(piece.possible_moves)
                    print(f"1. {squares_clicked_on}")
                elif len(squares_clicked_on) == 1:
                    # If the player has clicked on a square to move the already selected piece to

                    if position in piece_moves[0]:
                        # If the square to move to is a valid move option
                        original_pos = squares_clicked_on[0]

                        # Change the piece's position attribute
                        self.board[original_pos[0]][original_pos[1]].position = position
                        # Change the location on the board
                        self.board[position[0]][position[1]] = self.board[original_pos[0]][original_pos[1]]
                        self.board[original_pos[0]][original_pos[1]] = Piece("None", transparent_image, 0,
                                                                             [original_pos[0], original_pos[1]])
                        if current_player == -1:
                            current_player = 1
                        else:
                            current_player = -1

                    self.redraw_board(squares_clicked_on[0], False)
                    squares_clicked_on = []
                    piece_moves = []

    # This method can be used to get all the squares that are being attacked by every piece on the board
    # EXCEPT THE KING AS THIS WILL CAUSE A RECURSION LOOP
    # This method will need to be adapted to check where the opposite king can move to
    def create_possible_moves_all_pieces(self):
        p1_positions_attacking = []
        p2_positions_attacking = []
        for piece in self.p1.pieces:
            if piece.name != "king":
                piece.create_possible_moves(self.board, False)
                p1_positions_attacking.extend(piece.possible_moves)
        for piece in self.p2.pieces:
            if piece.name != "king":
                piece.create_possible_moves(self.board, False)
                p2_positions_attacking.extend(piece.possible_moves)

        return [p1_positions_attacking, p2_positions_attacking]

    def is_check(self, king_position):
        attacked_positions = self.create_possible_moves_all_pieces()
        if current_player == -1:
            if king_position in attacked_positions[1]:
                return True
            else:
                return False
        else:
            if king_position in attacked_positions[0]:
                return True
            else:
                return False


# Note: colour is represented by -1 for white, and 1 for black
class Player:
    def __init__(self, name, colour):
        self.name = name
        self.colour = colour
        self.pieces = []
        # This may be the LEAST efficient and unnecessarily complicated way to set up the pieces, but oh well
        if colour == 1:
            first_row = 0
            second_row = 1
        else:
            first_row = 7
            second_row = 6
        piece_names = {"king": [first_row, 4], "pawn1": [second_row, 0],
                       "pawn2": [second_row, 1], "pawn3": [second_row, 2],
                       "pawn4": [second_row, 3], "pawn5": [second_row, 4],
                       "pawn6": [second_row, 5], "pawn7": [second_row, 6],
                       "pawn8": [second_row, 7], "rook1": [first_row, 0],
                       "rook2": [first_row, 7], "knight1": [first_row, 1],
                       "knight2": [first_row, 6], "bishop1": [first_row, 2],
                       "bishop2": [first_row, 5], "queen": [first_row, 3]}

        for piece_name in piece_names.keys():
            imagepath = f"Images/{colour}"
            position = []

            if "pawn" in piece_name:
                imagepath += "pawn"
            elif "king" in piece_name:
                imagepath += "king"
            elif "rook" in piece_name:
                imagepath += "rook"
            elif "bishop" in piece_name:
                imagepath += "bishop"
            elif "knight" in piece_name:
                imagepath += "knight"
            elif "queen" in piece_name:
                imagepath += "queen"
            imagepath += ".png"

            image = ImageTk.PhotoImage(PILImage.open(imagepath))

            if "pawn" in piece_name:
                self.pieces.append(Pawn(piece_name, image, colour, piece_names[piece_name]))
            else:
                self.pieces.append(Piece(piece_name, image, colour, piece_names[piece_name]))


class Piece:
    def __init__(self, name, image, direction, position):
        self.name = name
        self.moves = []
        self.possible_moves = []
        self.image = image
        self.direction = direction
        self.position = position

        if "pawn" in self.name:
            self.create_pawn_moves()
        elif "king" in self.name:
            self.create_king_moves()
        elif "knight" in self.name:
            self.create_knight_moves()
        elif "bishop" in self.name:
            self.create_bishop_moves()
        elif "rook" in self.name:
            self.create_rook_moves(False)
        elif "queen" in self.name:
            self.create_queen_moves()

    @abstractmethod
    def create_pawn_moves(self):
        pass

    def create_possible_moves(self, board, highlight):
        if "knight" in self.name:
            for move in self.moves:
                row_check = move[0] + self.position[0]
                column_check = move[1] + self.position[1]
                # The code below checks if a move is possible under the following conditions:
                # The move lands the piece on a square which is on the board
                # The move lands the piece on a square which is not occupied by a piece owned by the same player
                # There are other pieces in the way of the move, and the current piece is not a knight
                if (0 <= row_check <= 7) and (0 <= column_check <= 7) and board[row_check][
                    column_check].direction != self.direction:
                    self.possible_moves.append([row_check, column_check])
        elif "king" in self.name:
            # CHECK IF NOT IN CHECK/CHECKMATE first AND IF NEXT MOVE WILL LEAD TO CHECK AGAIN
            for move in self.moves:
                row_check = move[0] + self.position[0]
                column_check = move[1] + self.position[1]
                if (0 <= row_check <= 7) and (0 <= column_check <= 7) and board[row_check][
                    column_check].direction != self.direction:
                    if not game.is_check([row_check, column_check]):
                        self.possible_moves.append([row_check, column_check])

        # Check for a free path between the 2 positions DONE
        elif "bishop" in self.name or "rook" in self.name or "queen" in self.name:
            for move_list in self.moves:
                for move in move_list[1:]:
                    row_check = move[0] + self.position[0]
                    column_check = move[1] + self.position[1]
                    # If the square is on the board and is not empty, the path is blocked by a piece
                    if (0 <= row_check <= 7) and (0 <= column_check <= 7) and board[row_check][
                        column_check].direction != 0:
                        if board[row_check][column_check].direction != self.direction:
                            self.possible_moves.append([row_check, column_check])
                        break
                    elif (0 <= row_check <= 7) and (0 <= column_check <= 7) and board[row_check][
                        column_check].direction != self.direction:
                        self.possible_moves.append([row_check, column_check])

        if highlight:
            for move in self.possible_moves:
                game.squares[move[0]][move[1]].config(bg="#c2cfd1")

    # All moves are created in the form [y, x]
    def create_king_moves(self):
        self.moves.append([1, 1])
        self.moves.append([1, 0])
        self.moves.append([1, -1])
        self.moves.append([0, 1])
        self.moves.append([0, -1])
        self.moves.append([-1, 1])
        self.moves.append([-1, 0])
        self.moves.append([-1, -1])

    def create_knight_moves(self):
        self.moves.append([1, 2])
        self.moves.append([1, -2])
        self.moves.append([2, 1])
        self.moves.append([2, -1])
        self.moves.append([-1, 2])
        self.moves.append([-1, -2])
        self.moves.append([-2, 1])
        self.moves.append([-2, -1])

    def create_bishop_moves(self):
        for i in range(5):
            self.moves.append([])

        for i in range(8):
            for j in range(8):
                if i == j:
                    self.moves[1].append([i, j])  # Down Right
                    self.moves[2].append([-i, j])  # Up Right
                    self.moves[3].append([i, -j])  # Down Left
                    self.moves[4].append([-i, -j])  # Up Left

    def create_rook_moves(self, is_queen):
        for i in range(5):
            self.moves.append([])

        start = 1
        if is_queen:
            start = 5
        for i in range(8):
            self.moves[start].append([i, 0])  # Down
            self.moves[start + 1].append([-i, 0])  # Up
            self.moves[start + 2].append([0, i])  # Right
            self.moves[start + 3].append([0, -i])  # Left

    def create_queen_moves(self):
        self.create_bishop_moves()
        self.create_rook_moves(True)


class Pawn(Piece):
    def __init__(self, name, image, direction, position):
        super().__init__(name, image, direction, position)

    def create_pawn_moves(self):
        self.moves.append([2 * self.direction, 0])
        self.moves.append([1 * self.direction, 0])
        # Allow for taking pieces with pawns
        self.moves.append([1 * self.direction, 1])
        self.moves.append([1 * self.direction, -1])

    def create_possible_moves(self, board, highlight):
        for move in self.moves:
            if move == self.moves[0]:
                if (self.direction == -1 and self.position[0] == 6) or (self.direction == 1 and self.position[0] == 1):
                    # If the piece hasn't been moved yet
                    row_check = move[0] // 2 + self.position[0]
                    column_check = move[1] // 2 + self.position[1]
                    if (0 <= row_check <= 7) and (0 <= column_check <= 7) and board[row_check][
                        column_check].direction != 0:
                        break

                    row_check = move[0] + self.position[0]
                    column_check = move[1] + self.position[1]
                    if (0 <= row_check <= 7) and (0 <= column_check <= 7) and board[row_check][
                        column_check].direction != 0:
                        break

                    self.possible_moves.append([row_check, column_check])

            elif move == self.moves[2] or move == self.moves[3]:
                row_check = move[0] + self.position[0]
                column_check = move[1] + self.position[1]
                if (0 <= row_check <= 7) and (0 <= column_check <= 7) and board[row_check][
                    column_check].direction != self.direction and board[row_check][column_check].direction != 0:
                    self.possible_moves.append([row_check, column_check])
            else:
                row_check = move[0] + self.position[0]
                column_check = move[1] + self.position[1]
                if (0 <= row_check <= 7) and (0 <= column_check <= 7) and board[row_check][
                    column_check].direction == 0:
                    self.possible_moves.append([row_check, column_check])

        if highlight:
            for move in self.possible_moves:
                game.squares[move[0]][move[1]].config(bg="#c2cfd1")


window = Tk()
transparent_image = ImageTk.PhotoImage(PILImage.open("Images/transparent_60x60.png"))

game = Game("p1", "p2")
game.redraw_board(None, False)

# Make the window resizable
for i in range(8):
    window.columnconfigure(i, weight=1, minsize=50)
    window.rowconfigure(i, weight=1, minsize=50)

window.mainloop()
