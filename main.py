import threading
from abc import abstractmethod
from tkinter import *
from PIL import Image as PILImage
from PIL import ImageTk
import socket
import pickle

current_player = -1
scores = {"p1": 0, "p2": 0}
# This list will be used to check where the player is moving to, so it will contain a max of 2 elements
squares_clicked_on = []
piece_moves = []
duck_squares = []
IP = "192.168.4.63"
PORT = 5051
BUFFER_SIZE = 16384
piece_images = {}
game_is_over = False


# WORK ON LINE 328

def resize_image(image, size):
    image = image.resize(size)
    return image


class Game:
    def __init__(self, p1, p2):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((IP, PORT))

        self.player_assignment = pickle.loads(self.client.recv(BUFFER_SIZE))
        print(f"You are {self.player_assignment}")
        window.title(self.player_assignment)

        start_signal = pickle.loads(self.client.recv(BUFFER_SIZE))
        if start_signal != "Start":
            print("Error: Did not receive correct start signal")
            self.client.close()

        self.board = []
        self.squares = []
        self.p1 = Player(p1, -1)
        self.p2 = Player(p2, 1)
        self.create_board()
        global current_player
        self.duck_turn = False
        self.duck = Duck("duck", True, 2)
        self.networking_thread = threading.Thread(target=self.listen_to_server)
        self.networking_thread.daemon = True
        self.networking_thread.start()

    def initialise_game(self):
        global current_player, squares_clicked_on, piece_moves, duck_squares, game_is_over
        print("Game initialised")
        current_player = -1
        squares_clicked_on = []
        piece_moves = []
        duck_squares = []
        game_is_over = False

        self.board = []
        self.squares = []
        self.duck_turn = False

        self.p1.recreate_pieces()
        self.p2.recreate_pieces()
        self.create_board()

        if not self.networking_thread.is_alive():
            self.networking_thread = threading.Thread(target=self.listen_to_server)
            self.networking_thread.daemon = True
            self.networking_thread.start()
        self.redraw_board(None, False)

    def check_image(self, piece):
        global piece_images
        return piece_images[f"{piece.direction}{piece.name}"]

    def listen_to_server(self):
        while True:
            self.receive_board_and_turn_from_server()
            print("Board received ...")
            print(f"1. Current player: {current_player}")
            print(f"1. Player assignment: {self.player_assignment}")
            window.after(0, self.redraw_board(None, False))
            print("Updating board")

    def send_board_to_server(self):
        print(f"2. Current player: {current_player}")
        print(f"2. Player assignment: {self.player_assignment}")
        before = {"board": self.board, "duck_squares": duck_squares}
        # print(f"Before: {before}")
        to_send = pickle.dumps({"board": pickle.dumps(self.board), "duck_squares": duck_squares, "scores": scores})
        # print(f"To send: {to_send}")
        self.client.sendall(to_send)

    def receive_board_and_turn_from_server(self):
        try:
            data_received = pickle.loads(self.client.recv(BUFFER_SIZE))
        except (ConnectionResetError, BrokenPipeError, EOFError):
            print("Connection closed by server")
            window.quit()
            exit()

        if data_received["board"] is not None:
            self.board = pickle.loads(data_received["board"])
        if data_received["duck_squares"] is not None:
            global duck_squares
            duck_squares = data_received["duck_squares"]
        global current_player
        current_player = data_received["current_turn"]
        global scores
        if scores != data_received["scores"]:
            print("Scores unequal!")
            if data_received["scores"]["p1"] - scores["p1"] == 1:
                winner = "White"
            elif data_received["scores"]["p2"] - scores["p2"] == 1:
                winner = "Black"

            game_message_label.config(text=f"{winner} wins!")
            scores = data_received["scores"]
            white_score_label.config(text="White: " + str(scores["p1"]))
            black_score_label.config(text="Black: " + str(scores["p2"]))
            global game_is_over
            game_is_over = True
            self.initialise_game()
        # print(f"Current player: {current_player}")

    def create_board(self):
        self.board = []
        self.squares = []
        global transparent_image
        for i in range(8):
            self.board.append([])
            self.squares.append([])
            for j in range(8):
                self.board[i].append(Piece("None", False, 0, [i, j]))
                self.squares[i].append(
                    Button(
                        image=transparent_image,
                        height=60,
                        width=60,
                        command=lambda i=i, j=j: self.check_move(self.board[i][j].position)
                    ))
                self.squares[i][j].grid(row=i + 1, column=j, sticky="nsew")

        # Add pieces to the actual board
        self.board[0][0] = self.p2.pieces["rook1"]
        self.board[0][1] = self.p2.pieces["knight1"]
        self.board[0][2] = self.p2.pieces["bishop1"]
        self.board[0][3] = self.p2.pieces["queen1"]
        self.board[0][4] = self.p2.pieces["king1"]
        self.board[0][5] = self.p2.pieces["bishop2"]
        self.board[0][6] = self.p2.pieces["knight2"]
        self.board[0][7] = self.p2.pieces["rook2"]
        for i in range(8):
            self.board[1][i] = self.p2.pieces[f"pawn{i + 1}"]

        self.board[7][0] = self.p1.pieces["rook1"]
        self.board[7][1] = self.p1.pieces["knight1"]
        self.board[7][2] = self.p1.pieces["bishop1"]
        self.board[7][3] = self.p1.pieces["queen1"]
        self.board[7][4] = self.p1.pieces["king1"]
        self.board[7][5] = self.p1.pieces["bishop2"]
        self.board[7][6] = self.p1.pieces["knight2"]
        self.board[7][7] = self.p1.pieces["rook2"]
        for i in range(8):
            self.board[6][i] = self.p1.pieces[f"pawn{i + 1}"]

    def swap_board_squares(self, square1, square2):
        temp = self.board[square1[0]][square1[1]]
        self.board[square1[0]][square1[1]] = self.board[square2[0]][square2[1]]
        self.board[square2[0]][square2[1]] = temp

        self.board[square1[0]][square1[1]].position = square1
        self.board[square2[0]][square2[1]].position = square2

    def make_check_move_command(self, x, y):
        return lambda: self.check_move(self.board[x][y].position)

    def redraw_board(self, selected_square, highlight):
        global transparent_image
        for i in range(8):
            for j in range(8):
                if game.board[i][j].image:
                    self.squares[i][j].config(
                        image=self.check_image(self.board[i][j]),
                        height=60,
                        width=60,
                        command=lambda i=i, j=j: self.check_move(self.board[i][j].position)
                    )
                else:
                    self.squares[i][j].config(
                        image=transparent_image,
                        height=60,
                        width=60,
                        command=lambda i=i, j=j: self.check_move(self.board[i][j].position)
                    )

                # The following code is for hiding the possible moves, which are shown when creating possible moves
                if not highlight:
                    if (i + j) % 2 == 0:
                        self.squares[i][j].config(bg="SystemButtonFace")
                    else:
                        self.squares[i][j].config(bg="Grey")

        if selected_square is not None and highlight:
            # If the player has selected a piece to move and it is not the square to move the piece to
            self.squares[selected_square[0]][selected_square[1]].config(bg="orange")
        if selected_square is not None and not highlight:
            if (selected_square[0] + selected_square[1]) % 2 == 0:
                self.squares[selected_square[0]][selected_square[1]].config(bg="SystemButtonFace")
            else:
                self.squares[selected_square[0]][selected_square[1]].config(bg="Grey")

    def castle(self, pos1, pos2):
        piece1 = self.board[pos1[0]][pos1[1]]
        piece2 = self.board[pos2[0]][pos2[1]]

        if (("king" in piece1.name and "None" in piece2.name) or
            ("rook" in piece1.name and "None" in piece2.name)) \
                and not piece1.has_moved_yet:
            if current_player == -1:
                y = 7
            else:
                y = 0
            if pos2[1] == 2:
                if not self.board[y][0].has_moved_yet and "rook" in self.board[y][0].name and not self.board[y][
                    4].has_moved_yet and "king" in self.board[y][4].name:
                    # Check for clear path between king and rook
                    free_spaces = True
                    for i in range(1, 4):
                        if self.board[y][i].name != "None":
                            free_spaces = False
                    if free_spaces:
                        # Castle
                        self.swap_board_squares([y, 2], [y, 4])
                        self.swap_board_squares([y, 0], [y, 3])
                        return True
            elif pos2[1] == 6:
                if not self.board[y][7].has_moved_yet and "rook" in self.board[y][7].name and not self.board[y][
                    4].has_moved_yet and "king" in self.board[y][4].name:
                    # Check for clear path between king and rook
                    free_spaces = True
                    for i in range(5, 7):
                        if self.board[y][i].name != "None":
                            free_spaces = False
                    if free_spaces:
                        # Castle
                        self.swap_board_squares([y, 7], [y, 5])
                        self.swap_board_squares([y, 4], [y, 6])
                        return True
        return False

    def create_possible_moves_all_pieces(self):
        global current_player
        possible_moves = []
        print(f"create: {possible_moves}")
        if current_player == -1:
            for piece in self.p1.pieces.values():
                piece.create_possible_moves(self.board, False)
                possible_moves.extend(piece.possible_moves)
        else:
            for piece in self.p2.pieces.values():
                piece.create_possible_moves(self.board, False)
                possible_moves.extend(piece.possible_moves)

        return possible_moves

    # Check if a piece can move to a square on the board
    def check_move(self, position):
        global squares_clicked_on
        global transparent_image
        global current_player
        global piece_moves
        print(position)
        piece = self.board[position[0]][position[1]]
        print(piece.name)

        print(current_player, self.player_assignment)
        global game_is_over
        if int(current_player) == int(self.player_assignment) and not game_is_over:

            if piece.direction == current_player or piece.direction == 0 or (
                    piece.direction != current_player and len(squares_clicked_on) == 1):
                # If the player has clicked of their pieces to select, or has clicked the square to move one of their pieces to
                print("1")
                if not self.duck_turn:
                    piece.possible_moves = []
                    piece.create_possible_moves(self.board, True)

                    if len(squares_clicked_on) == 1 and self.castle(
                            [squares_clicked_on[0][0], squares_clicked_on[0][1]], [position[0], position[1]]):
                        # If the player is trying to castle, castle
                        self.redraw_board(None, False)
                        self.duck_turn = True
                    elif len(squares_clicked_on) == 1 and piece.direction == self.board[squares_clicked_on[0][0]][
                        squares_clicked_on[0][1]].direction:
                        # If the player has clicked on another piece of theirs after selecting a piece of theirs already
                        print("2")
                        self.redraw_board(squares_clicked_on[0], False)
                        squares_clicked_on = []
                        piece_moves = []
                    else:
                        if len(squares_clicked_on) == 0 and piece.name != "None":
                            # If the player has clicked on a valid piece of theirs to select
                            print("3")
                            squares_clicked_on.append(position)
                            self.redraw_board(squares_clicked_on[0], True)
                            piece_moves.append(piece.possible_moves)
                            print(f"1. {squares_clicked_on}")
                        elif len(squares_clicked_on) == 1:
                            # If the player has clicked on a square to move the already selected piece to
                            if position in piece_moves[0]:
                                # If the square to move to is a valid move option
                                print("5")
                                original_pos = squares_clicked_on[0]

                                # Change the piece's position attribute
                                self.board[original_pos[0]][original_pos[1]].position = position
                                self.board[original_pos[0]][original_pos[1]].has_moved_yet = True

                                # Change the location on the board
                                self.board[position[0]][position[1]] = self.board[original_pos[0]][original_pos[1]]
                                self.board[original_pos[0]][original_pos[1]] = Piece("None", False, 0,
                                                                                     [original_pos[0], original_pos[1]])

                                # Check if pawn promotion is valid
                                last_row = 0
                                if current_player == 1:
                                    last_row = 7
                                if "pawn" in self.board[position[0]][position[1]].name and position[0] == last_row:
                                    self.board[position[0]][position[1]] = Piece("queen1", True, current_player, [position[0], position[1]])
                                    print(f"PAWN STUFF: {self.board[position[0]][position[1]]}")

                                self.duck_turn = True

                                # Handle if the opposing king has been taken (win condition)
                                if "king" in piece.name:
                                    if piece.direction == 1:
                                        scores["p1"] += 1
                                        white_score_label.config(text="White: " + str(scores["p1"]))
                                        game_message_label.config(text="White wins!")
                                    else:
                                        scores["p2"] += 1
                                        black_score_label.config(text="Black: " + str(scores["p2"]))
                                        game_message_label.config(text="Black wins!")
                                    self.redraw_board(None, False)
                                    game_is_over = True
                                if game_is_over:
                                    self.initialise_game()
                                else:
                                    self.redraw_board(squares_clicked_on[0], False)
                                self.send_board_to_server()
                            else:
                                # If the player has clicked on an invalid square
                                self.redraw_board(squares_clicked_on[0], False)
                                squares_clicked_on = []
                                piece_moves = []
                else:
                    if piece.name == "None":
                        print("6")
                        self.duck.position = position
                        if len(duck_squares) == 1:
                            self.swap_board_squares(position, duck_squares[0])
                            duck_squares[0] = position
                        else:
                            self.board[position[0]][position[1]] = self.duck
                        duck_squares.clear()
                        duck_squares.append([position[0], position[1]])
                        self.duck_turn = False

                        # Handle if the king is in stalemate (win condition)
                        # stalemate can only be achieved by the duck being the last piece moved
                        possible_moves = self.create_possible_moves_all_pieces()
                        print(f"possible moves: {possible_moves}")
                        if len(possible_moves) == 0:
                            if current_player == -1:
                                scores["p1"] += 1
                                white_score_label.config(text="White: " + str(scores["p1"]))
                                game_message_label.config(text="White wins by stalemate!")
                            else:
                                scores["p2"] += 1
                                black_score_label.config(text="Black: " + str(scores["p2"]))
                                game_message_label.config(text="Black wins by stalemate!")

                        self.redraw_board(None, False)
                        self.send_board_to_server()
                        squares_clicked_on = []
                        piece_moves = []


# Note: colour is represented by -1 for white, and 1 for black
class Player:
    def __init__(self, name, colour):
        self.name = name
        self.colour = colour
        self.pieces = {}
        if colour == 1:
            first_row = 0
            second_row = 1
        else:
            first_row = 7
            second_row = 6
        self.piece_names = {"king1": [first_row, 4], "pawn1": [second_row, 0],
                            "pawn2": [second_row, 1], "pawn3": [second_row, 2],
                            "pawn4": [second_row, 3], "pawn5": [second_row, 4],
                            "pawn6": [second_row, 5], "pawn7": [second_row, 6],
                            "pawn8": [second_row, 7], "rook1": [first_row, 0],
                            "rook2": [first_row, 7], "knight1": [first_row, 1],
                            "knight2": [first_row, 6], "bishop1": [first_row, 2],
                            "bishop2": [first_row, 5], "queen1": [first_row, 3]}

        global piece_images
        piece_images["2duck"] = ImageTk.PhotoImage(PILImage.open("Images/2duck.png").resize((60, 60)))
        for piece_name in self.piece_names.keys():
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
            piece_images[f"{self.colour}{piece_name}"] = image

            if "pawn" in piece_name:
                self.pieces[piece_name] = (Pawn(piece_name, True, colour, self.piece_names[piece_name]))
            else:
                self.pieces[piece_name] = (Piece(piece_name, True, colour, self.piece_names[piece_name]))

    def recreate_pieces(self):
        for piece_name in self.piece_names.keys():
            if "pawn" in piece_name:
                self.pieces[piece_name] = (Pawn(piece_name, True, self.colour, self.piece_names[piece_name]))
            else:
                self.pieces[piece_name] = (Piece(piece_name, True, self.colour, self.piece_names[piece_name]))


class Piece:
    def __init__(self, name, image, direction, position):
        self.name = name
        self.moves = []
        self.possible_moves = []
        self.image = image
        self.direction = direction
        self.position = position
        self.has_moved_yet = False

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
                                                                                   column_check].direction != 0 or
                                                                               board[row_check][
                                                                                   column_check].direction == 2):
                        if board[row_check][column_check].direction != self.direction and board[row_check][
                            column_check].direction != 2:
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
                        continue

                    row_check = move[0] + self.position[0]
                    column_check = move[1] + self.position[1]
                    if (0 <= row_check <= 7) and (0 <= column_check <= 7) and board[row_check][
                        column_check].direction != 0:
                        continue

                    self.possible_moves.append([row_check, column_check])

            # Handle taking pieces with pawns
            elif move == self.moves[2] or move == self.moves[3]:
                row_check = move[0] + self.position[0]
                column_check = move[1] + self.position[1]
                if (0 <= row_check <= 7) and (0 <= column_check <= 7) and board[row_check][
                    column_check].direction != self.direction and (
                        board[row_check][column_check].direction != 0 and board[row_check][
                    column_check].direction != 2):
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

white_score_label = Label(window, text="White: 0")
black_score_label = Label(window, text="Black: 0")
white_score_label.grid(row=0, column=0, sticky='w', padx=10)
black_score_label.grid(row=0, column=7, sticky='e', padx=10)
game_message_label = Label(window, text="White, make a move!")
game_message_label.grid(row=0, column=1, columnspan=6, sticky='n')

game = Game("p1", "p2")
game.redraw_board(None, False)

# Make the window resizable
for i in range(8):
    window.columnconfigure(i, weight=1, minsize=50)
    window.rowconfigure(i, weight=1, minsize=50)

window.mainloop()
