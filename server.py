import socket
import pickle
import threading

IP = "127.0.0.1"
PORT = 5051
BUFFER_SIZE = 12000

def initialise_server_game(player1_conn, player2_conn):
    current_player_conn = player1_conn
    other_player_conn = player2_conn
    boards_sent = 0
    current_player = -1
    return current_player_conn, other_player_conn, boards_sent, current_player

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
            boards_sent += 1
            print(f"boards sent: {boards_sent}. Current player: {current_player}. Current conn: {current_player_conn}")
            print(f"Current conn: {current_player_conn}, other conn: {other_player_conn}")
            # print(board_data)
            print(pickle.loads(board_data))

            board_data = pickle.loads(board_data)

            if scores != board_data["scores"]:  # Game over detected
                current_player_conn, other_player_conn, boards_sent, current_player = initialise_server_game(player1_conn, player2_conn)
                print("reset")
                scores = board_data["scores"]
                current_player_conn.sendall(pickle.dumps({"board": board_data["board"], "current_turn": current_player,
                                                    "duck_squares": board_data["duck_squares"],
                                                    "scores": board_data["scores"]}))
            # send the board state to the other player
            other_player_conn.sendall(pickle.dumps({"board": board_data["board"], "current_turn": current_player,
                                                    "duck_squares": board_data["duck_squares"],
                                                    "scores": board_data["scores"]}))

            # Swap the players
            if boards_sent == 2:
                current_player_conn, other_player_conn = other_player_conn, current_player_conn
                current_player = 1 if current_player == -1 else -1
                print("Players swapped")
                boards_sent = 0
                player1_conn.sendall(pickle.dumps(
                    {"board": None, "current_turn": current_player, "duck_squares": board_data["duck_squares"],
                     "scores": board_data["scores"]}))
                player2_conn.sendall(pickle.dumps(
                    {"board": None, "current_turn": current_player, "duck_squares": board_data["duck_squares"],
                     "scores": board_data["scores"]}))

    except Exception as e:
        print(e)
        print("An error has occurred or a player has disconnected")

    player1_conn.close()
    player2_conn.close()
    server.close()
    print("Closed")


if __name__ == "__main__":
    start_server()
