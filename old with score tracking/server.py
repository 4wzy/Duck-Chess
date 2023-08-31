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
        print(colored("1", "green"))
        while True:
            print(colored("2", "green"))
            # receive the board state from the current player
            board_data = current_player_conn.recv(BUFFER_SIZE)
            if not board_data:
                print("Player disconnected.")
                break
            print(colored("3", "green"))
            boards_sent += 1
            print(f"boards sent: {boards_sent}. Current player: {current_player}. Current conn: {current_player_conn}")
            # print(board_data)
            # print(pickle.loads(board_data))

            board_data = pickle.loads(board_data)
            # send the board state to the other player
            if board_data["game_over"]:
                current_player = -1
                print(colored("Game over", "red"))
            other_player_conn.sendall(pickle.dumps({"board": board_data["board"], "current_turn": current_player, "duck_squares": board_data["duck_squares"], "scores": board_data["scores"]}))

            # Swap the players
            if boards_sent == 2:
                print(colored("4", "green"))
                if scores == board_data["scores"]:
                    current_player_conn, other_player_conn = other_player_conn, current_player_conn
                    current_player = 1 if current_player == -1 else -1
                    print(f"Old scores: {scores}")
                    print(f"New scores: {scores}")
                    print("Players swapped")
                else:
                    print(colored("5", "green"))
                    print(f"O Scores: {scores}")
                    scores = board_data["scores"]
                    print(f"N Scores: {scores}")
                boards_sent = 0

            if board_data["game_over"]:
                boards_sent = 0
                board_data["game_over"] = False
                scores = board_data["scores"]
                current_player = -1
                print(colored("6 Game over.", "red"))

            player1_conn.sendall(pickle.dumps({"board": None, "current_turn": current_player, "duck_squares": board_data["duck_squares"], "scores": board_data["scores"]}))
            player2_conn.sendall(pickle.dumps({"board": None, "current_turn": current_player, "duck_squares": board_data["duck_squares"], "scores": board_data["scores"]}))
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