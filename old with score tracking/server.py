import socket
import pickle
import threading
from colorama import init
from termcolor import colored

init()

IP = "192.168.4.63"
PORT = 5051
BUFFER_SIZE = 16384


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((IP, PORT))
    except socket.error as e:
        str(e)
    server.listen(2)
    print("Server started and waiting for players to connect...")

    player1_conn, player1_addr = server.accept()
    print(f"Player 1 connected from {player1_addr}")
    player1_conn.sendall(pickle.dumps("-1"))

    player2_conn, player2_addr = server.accept()
    print(f"Player 2 connected from {player2_addr}")
    player2_conn.sendall(pickle.dumps("1"))

    # Inform players that the game can start
    player1_conn.sendall(pickle.dumps("Start"))
    player2_conn.sendall(pickle.dumps("Start"))

    current_player_conn = player1_conn
    other_player_conn = player2_conn

    boards_sent = 0
    current_player = -1
    scores = {"p1": 0, "p2": 0}

    try:
        while True:
            # receive the board state from the current player
            board_data = current_player_conn.recv(BUFFER_SIZE)
            if not board_data:
                print("Player disconnected.")
                break
            print(f"Current player: {current_player}. Current conn: {current_player_conn}")
            # print(board_data)
            # print(pickle.loads(board_data))

            board_data = pickle.loads(board_data)
            print(board_data)
            # send the board state to the other player
            if board_data[0] == "game_over":
                current_player = -1

            # Receive the board from the current player
            current_player_conn.sendall(pickle.dumps(["get_board"]))
            received_board = pickle.loads(current_player_conn.recv(BUFFER_SIZE))

            # Receive the duck_squares from the current player
            current_player_conn.sendall(pickle.dumps(["get_duck_squares"]))
            received_duck_squares = pickle.loads(current_player_conn.recv(BUFFER_SIZE))

            # Now send them to the other player
            other_player_conn.sendall(pickle.dumps(["board", received_board]))
            other_player_conn.sendall(pickle.dumps(["duck_squares", received_duck_squares]))

            other_player_conn.sendall(pickle.dumps(["current_player", current_player]))

            scores = current_player_conn.sendall(pickle.dumps(["get_scores"]))
            other_player_conn.sendall(pickle.dumps(["scores", scores]))

            # Swap the players
            if board_data[0] == "swap_players":
                current_player_conn, other_player_conn = other_player_conn, current_player_conn
                current_player = 1 if current_player == -1 else -1
                print(f"Scores: {scores}")
                print("Players swapped")

            if board_data[0] == "game_over":
                other_player_conn.sendall(pickle.dumps(["game_over", True]))
                current_player = -1
                other_player_conn.sendall(pickle.dumps(["current_player", -1]))
            print("Boards sent...")

    except Exception as e:
        print("An error has occurred or a player has disconnected")
        print(f"Exception: {e}")

    player1_conn.close()
    player2_conn.close()
    server.close()
    print(colored("7 Connections closed", "Blue"))


if __name__ == "__main__":
    start_server()
