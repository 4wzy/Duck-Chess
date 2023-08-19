from abc import abstractmethod
from tkinter import *
from PIL import Image as PILImage
from PIL import ImageTk

current_player = -1
score = {"p1": 0, "p2": 0}
# This list will be used to check where the player is moving to, so it will contain a max of 2 elements
squares_clicked_on = []
piece_moves = []
duck_squares = []


class Game:
    def __init__(self, p1, p2):
        self.board = []
        self.squares = []
        self.p1 = Player(p1, -1)
        self.p2 = Player(p2, 1)
        self.winner = 0
        self.create_board()
        self.current_player = self.p1.colour
        global duck_image
        global current_player
        self.duck_placed = False
        self.duck = Duck("duck", duck_image, 2)
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
                self.squares[i][j].grid(row=i + 1, column=j)

        # Add pieces to the actual board
        self.board[0][0] = self.p2.pieces["rook1"]
        self.board[0][1] = self.p2.pieces["knight1"]
        self.board[0][2] = self.p2.pieces["bishop1"]
        self.board[0][3] = self.p2.pieces["queen"]
        self.board[0][4] = self.p2.pieces["king"]
        self.board[0][5] = self.p2.pieces["bishop2"]
        self.board[0][6] = self.p2.pieces["knight2"]
        self.board[0][7] = self.p2.pieces["rook2"]
        for i in range(8):
            self.board[1][i] = self.p2.pieces[f"pawn{i + 1}"]

        self.board[7][0] = self.p1.pieces["rook1"]
        self.board[7][1] = self.p1.pieces["knight1"]
        self.board[7][2] = self.p1.pieces["bishop1"]
        self.board[7][3] = self.p1.pieces["queen"]
        self.board[7][4] = self.p1.pieces["king"]
        self.board[7][5] = self.p1.pieces["bishop2"]
        self.board[7][6] = self.p1.pieces["knight2"]
        self.board[7][7] = self.p1.pieces["rook2"]
        for i in range(8):
            self.board[6][i] = self.p1.pieces[f"pawn{i + 1}"]

    def swap_board_squares(self, square1, square2):
        temp = self.board[square1[0]][square1[1]]
        self.board[square1[0]][square1[1]] = self.board[square2[0]][square2[1]]
        temp.position = [square2[0], square2[1]]
        self.board[square2[0]][square2[1]] = temp

    def make_check_move_command(self, x, y):
        return lambda: self.check_move(game.board[x][y].position)

    def redraw_board(self, selected_square, highlight):
        global transparent_image
        for i in range(8):
            for j in range(8):
                if game.board[i][j].image is not None:
                    self.squares[i][j].config(
                        image=game.board[i][j].image,
                        height=60,
                        width=60,
                        command=self.make_check_move_command(i, j)
                    )
                else:
                    self.squares[i][j].config(
                        image=transparent_image,
                        height=60,
                        width=60,
                        command=self.make_check_move_command(i, j)
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

        if not self.duck_placed:
            if piece.name == "None":
                self.duck.position = position
                if len(duck_squares) == 1:
                    self.swap_board_squares(position, duck_squares[0])
                    duck_squares[0] = position
                else:
                    self.board[position[0]][position[1]] = self.duck
                self.duck_placed = True
                duck_squares.clear()
                duck_squares.append([position[0], position[1]])
                self.redraw_board(None, False)
        else:
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

                            self.duck_placed = False

                        self.redraw_board(squares_clicked_on[0], False)
                        squares_clicked_on = []
                        piece_moves = []


# Note: colour is represented by -1 for white, and 1 for black
class Player:
    def __init__(self, name, colour):
        self.name = name
        self.colour = colour
        self.pieces = {}
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
                self.pieces[piece_name] = (Pawn(piece_name, image, colour, piece_names[piece_name]))
            else:
                self.pieces[piece_name] = (Piece(piece_name, image, colour, piece_names[piece_name]))


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
                    column_check].direction != self.direction and board[row_check][column_check].direction != 2:
                    self.possible_moves.append([row_check, column_check])
        elif "king" in self.name:
            for move in self.moves:
                row_check = move[0] + self.position[0]
                column_check = move[1] + self.position[1]
                if (0 <= row_check <= 7) and (0 <= column_check <= 7) and board[row_check][
                    column_check].direction != self.direction and board[row_check][column_check].direction != 2:
                    self.possible_moves.append([row_check, column_check])

        elif "bishop" in self.name or "rook" in self.name or "queen" in self.name:
            for move_list in self.moves:
                for move in move_list[1:]:
                    row_check = move[0] + self.position[0]
                    column_check = move[1] + self.position[1]
                    # If the square is on the board and is not empty, the path is blocked by a piece
                    if (0 <= row_check <= 7) and (0 <= column_check <= 7) and (board[row_check][
                        column_check].direction != 0 or board[row_check][column_check].direction == 2):
                        if board[row_check][column_check].direction != self.direction and board[row_check][column_check].direction != 2:
                            self.possible_moves.append([row_check, column_check])
                        break
                    elif (0 <= row_check <= 7) and (0 <= column_check <= 7) and board[row_check][
                        column_check].direction != self.direction:
                        self.possible_moves.append([row_check, column_check])

        elif "duck" in self.name:
            for square in self.moves:
                if board[square[0]][square[1]].direction == 0:
                    self.possible_moves.append(square)

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

    def create_duck_moves(self):
        for i in range(8):
            for j in range(8):
                self.moves.append([i, j])


class Duck(Piece):
    def __init__(self, name, image, direction):
        super().__init__(name, image, direction, [-1, -1])
        self.position = []


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
                # Handle pawn moving 2 squares forward
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

            # Handle taking pieces with pawns
            elif move == self.moves[2] or move == self.moves[3]:
                row_check = move[0] + self.position[0]
                column_check = move[1] + self.position[1]
                if (0 <= row_check <= 7) and (0 <= column_check <= 7) and board[row_check][
                    column_check].direction != self.direction and (board[row_check][column_check].direction != 0 and board[row_check][column_check].direction != 2):
                    self.possible_moves.append([row_check, column_check])
            # Normal pawn movement
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
duck_image = ImageTk.PhotoImage(PILImage.open("Images/duck.png").resize((60, 60)))

white_score_label = Label(window, text="White: 0")
black_score_label = Label(window, text="Black: 0")
game_message_label = Label(window, text="White, place the duck!")
white_score_label.grid(row=0, column=0, sticky='w', padx=10)
game_message_label.grid(row=0, column=1, columnspan=6, sticky='n')
black_score_label.grid(row=0, column=7, sticky='e', padx=10)


game = Game("p1", "p2")
game.redraw_board(None, False)

# Make the window resizable
for i in range(8):
    window.columnconfigure(i, weight=1, minsize=50)
    window.rowconfigure(i, weight=1, minsize=50)

window.mainloop()