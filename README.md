# Duck Chess
#### Video Demo:  <URL HERE>
#### Description:
Duck chess is a variant of chess where players make a normal chess move but then have to place down a duck piece immediately after.
The game is built in Python, using Tkinter for the graphical user interface, sockets for networking (with the help of pickles for data serialisation), and threading for managing many operations at the same time while ensuring that the GUI is updated as needed without interruption. 

## Basic rules (from [chess.com](https://www.chess.com/terms/duck-chess)):
- Players make a standard chess move, followed by moving the duck to an empty square on the board.
- The duck always moves.
- The duck blocks the square where it's placed, making it impossible for other pieces to move to or through it.
- Knights can jump over the duck.
- There are no checks or checkmates—players capture the enemy king to win.
- Kings can move to attacked squares. They can also castle through attacked squares.

## Project structure
### main.py
This file contains all of the client-side logic as well as the GUI for the game and how it is rendered for each client. I have tried to keep it as **object-oriented** as I can for a clean code design and easy future maintainability, but that has proved to be quite hard as I implemented more and more features.
It handles user input, displays the game board after each move, validates user moves, and communicates with the server for multiplayer to work.
The key features include:
- Setting up the game with the "Game" class, including connecting to the server and initialising the board and players. The init() method of the Game class also sets up a dedicated networking thread to continuously listen to the server waiting for input (the board state, current player, scores, etc..)
- Implementing the game logic itself: the check_move() method in the Game class is the most important part of what validates player moves and handles placing the duck correctly. It also allows for special moves such as castling and promoting pawns to queens when they reach the back rank of the opponent.
- Displaying the GUI: the game board is represented as an 8x8 grid of buttons, where each button has an image displaying either a chess piece or being empty (or having a background colour to show possible moves). A transparent image is used for empty squares, allowing me to change the background of these squares as needed. The create_board() method sets up the board graphically, and then the redraw_board() method refreshes the board to show the latest game state after each move or simply a click on a square.
- Error handling: manages errors such as receiving incorrect sttart signals from the server and ensuring that the connection between the 2 clients, and between each individual client and the server is maintained. If a single client disconnects, the other client and the server will also be terminated, and all connections will be closed.
- At a lower level, there are methods to create all of the possible moves for any piece based on the state of the board at any time.
- Handling if the game is over and re-initialising the game state and sending appropriate signals to the server to restart the game for the other client too, as well as updating the score for both clients and making sure that the clients are still in sync with the server.
- Also at a lower level, each piece is instantiated either from the Piece class, or from the Pawn or Duck classes, which both inherit from the Piece class.
- There are many helper functions to ensure that the game works as intended, for example the check_image() method in the Game class which ensures that each button is displayed with the appropriate image based on the piece that the square should represent. This was a necessary design choice in order to make sure that the pickles library can serialise the board without running into any errors when attempting to serialise Tkinter image objects. This should also greatly lower the amount of data transmitted when sending the board between the server and clients.

### server.py
This file manages the server-side logic of the game. It sets up a server, handles client connections, and syncs the game state between the two players, making sure that one player can not go out of sync with the other.
Here are the key parts:
- Server initialisation through a socket server set up on a specific IP and port. After both players connect, they are assigned their player number (representing if they will be playing white or black), and after both players have successfully connected, the server tells the players that the game can start using the start signal.
- The server receives a dictionary containing data about the game after each move. This dictionary includes information about the board state, current turn, duck positions, and scores.
- The current turn data from the dictionary is how the server keeps track of which player's turn it is to make a move. Once a player has sent 2 board states, one for their first normal move and one for the duck move, then the server will swap the player's roles and ensure that the current_player variable is updated and sent to both clients so that they can not continue to make moves when it is not their turn.
- Handles the game over logic by checking if there has been a change in the scores variable received from the dictionary about the state of the game, and then resets the game state using the initialise_server_game() function. This then makes sure that both players are updated with the new game state, and the new scores.
- The server handles errors and detects if a player disconnects or if an error occurs.

## Design choices
- I decided to use Tkinter over Pygame as I didn't need the full control that Pygame offers for this project, and the input is not too complex to manage with Tkinter due to the players simply having to click on different parts of the GUI. Tkinter felt like the more lightweight choice, and as I will be making a project at school using Tkinter soon, it seemed like the better option to get some practice in. I already had an idea in mind of how I would use the grid manager to represent the game board graphically, allowing for the user to resize their board if they wish to. **NOTE:** The board itself resizes with squares growing/shrinking as necessary, but the images do not. I have tried to make the images resize in many ways, but because there are so many different images to handle, each image for each square will have to be individually resized each time the window resize event is called from the client side. I was able to accomplish this, but the performance issues it came with were not worth the resizing of the images. I tried to further optimise this by only resizing images if the window had been resized by a certain amount, but there was still noticeable lag.
- Simple GUI with labels at the top to give the players information about the scores and who has recently won. Main.py is in charge of displaying light and dark squares correctly.
- The server.py file has been designed to be thread safe so that it can be modified to handle multiple geame sessions simultaneously in the future, but I decided not to implement this after the chess project took me much longer to code than anticipated.
- There is another rule for duck chess where the player who gets stalemated wins. This is however almost impossible to achieve as there are no checks in duck chess making stalemates incredibly rare in actual games. Implementing this feature means that after each player's turn to place the duck, the possible moves for each of their pieces will need to be checked to make sure that there are absolutely no moves that they can make including the square that the duck is on. As a result of this being so processor-heavy, I decided not to implement it in the end, especially because of how rare it is.
- Sending data as a serialised dictionary after each move was a risky choice I made at the beginning of the game in order to make syncing game data between clients easier, without the server needing to send messages to the clients requesting data at certain times. As time went on, I realised that it was a debatable choice, and I will try to approach networking in my projects differently in the future. Nevertheless, the game still runs as intended, and I have not come across any sync issues in any of the tests that I have ran after completing the project.

I had a lot of fun working on duck chess! CS50x was a great experience that gave me the skills I needed to create a game like this by myself.
  
