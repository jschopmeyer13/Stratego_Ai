from player import *
from board import *


# TODO: Selects random pieces and setups random board
# The pieces appears to be referenced improperly
# Pieces like Flag(11), Bomb(12) are moving despite being instructed not to
# -> Need to change reference to Board in game and player class
# ->> Currently self.player1.board.board references the 2D matrix
class Game:
    def __init__(self, trace, player1, player2, hide):
        self.trace = trace 
        self.player1 = player1
        self.player2 = player2 
        self.hide = hide

        
        # self.board = startBoard
        # self.board = Board(self, trace)
        # self.player1 = player1_type
        # self.player2 = player2_type
        
    def runGame(self):
        #! board = Board(self.trace) 
        # TODO : Add back in trace
        if isinstance(self.player1, PlayerAB):
            algorithmPlayer = 0
        elif isinstance(self.player2, PlayerAB):
            algorithmPlayer = 1
        else:
            algorithmPlayer = 0 
        

        board = Board(self.trace, algorithmPlayer=algorithmPlayer)
        # board.printTrace()
        while not board.game_over:
            if board.turn == 0:
                if not isinstance(self.player1, ManualPlayer):
                    print("Player 1 is thinking")
   
                else:
                    pass
                board.print(self.hide)

                self.player1.getMyPieces(board)
                if isinstance(self.player1, PlayerAB):
                    move = self.player1.findMove(board, algorithmPlayer)
                else:
                    move = self.player1.findMove(board)
                
            else:
                if not isinstance(self.player2, ManualPlayer):
                    print("Player 2 is thinking")
        
                else:
                    pass
                board.print(self.hide)
                
                self.player2.getMyPieces(board)
                if isinstance(self.player2, PlayerAB):
                    move = self.player2.findMove(board, algorithmPlayer)
                else:
                    move = self.player2.findMove(board)

            # Make moves setup (x1, y1, x2, y2) (x1, y1) ==moves to=> (x2, y2)
            if len(move) == 0:
                print("No Moves Remaining: GAME OVER") # ! Check who has no moves left             
                return "done"

            else:
                pass

            # Print statements to show moves
            if self.hide == 1 and board.board[move[0]][move[1]].team == 1:
                print("Player",board.board[move[0]][move[1]].team+1, "moves:",board.board[move[0]][move[1]].rank, " to ", str(move[2]) +", "+str(move[3]))
            
            elif self.hide == 0 and board.board[move[0]][move[1]].team == 0:
                print("Player",board.board[move[0]][move[1]].team+1, "moves:",board.board[move[0]][move[1]].rank, " to ", str(move[2]) +", "+str(move[3]))

            elif self.hide == -1:
                print("Player",board.board[move[0]][move[1]].team+1, "moves:",board.board[move[0]][move[1]].rank, " to ", str(move[2]) +", "+str(move[3]))
            else:
                pass

            board.makeMove(move[0], move[1], move[2], move[3])

            # board.printTrace()

            # board.print()
            # board.printTrace() # uncomment to print out the trace of each board state

        print("--Final Game Board--")
        board.print()


# Starts Game with user input
# ! Alpha-beta works better as Player 1 than it does as Player 2
def userInput():
    hide = -1

    print("Player options: RandomPlayer(r), PlayerAb(ab), or ManualPlayer(m)\n\n")
    
    
    p1 = None
    while p1 == None:
        player1 = input("Choose Player 1 [RandomPLayer(r), PlayerAB(ab), or ManualPlayer(m)]: ")
        player1 = player1.lower()

        if player1 == "r":
            p1 = RandomPlayer(RED_TEAM)
            break
        elif player1 == "ab":
            p1 = PlayerAB(RED_TEAM, hide = -1)
            break
        elif player1 == "m":
            p1 = ManualPlayer(RED_TEAM)
    
        else:
            print("p1 should be either: r, ab, or m")

    p2 = None
    while p2 == None:

        if isinstance(p1, PlayerAB):
            player2 = input("Choose Player 2 [RandomPlayer(r), ManualPlayer(m)]: ")
        else:
            player2 = input("Choose Player 2 [RandomPLayer(r), PlayerAB(ab), or ManualPlayer(m)]: ")

        player2 = player2.lower()

        if player2 == "r":
            p2 = RandomPlayer(BLUE_TEAM)
            break

        elif player2 == "m":
            p2 = ManualPlayer(BLUE_TEAM)        

        elif (not isinstance(p1, PlayerAB)) and player2 == "ab":
            p2 = PlayerAB(BLUE_TEAM, hide = -1)
            # only 1 ab works at a time
            break
        
        elif (isinstance(p1, PlayerAB)) and player2 == "ab":
            print("only 1 Player AB can be selected")

        else:
            print("p2 should be either: r or m")


    if isinstance(p1, ManualPlayer) and (not isinstance(p2, ManualPlayer)):
        hideInput = input("P1: Do you want to hide the opponents pieces? (y/n): ")
        if hideInput.lower() == "y":
            hide = 0
            if isinstance(p2, PlayerAB):
                p2 = PlayerAB(BLUE_TEAM, hide = hide) # reassigns to hide the probability trace
        else:
            hide = -1
    
    elif isinstance(p2, ManualPlayer) and (not isinstance(p1, ManualPlayer)):
        hideInput = input("P2: Do you want to hide the opponents pieces? (y/n): ")
        if hideInput.lower() == "y":
            hide = 1
            if isinstance(p1, PlayerAB):
                p1 = PlayerAB(RED_TEAM, hide = hide) # reassigns to hide the probability trace
        else:
            hide = -1

        

    return p1, p2, hide

def testInput():
    hide = -1 # set to -1 to show everything, 0 to show only top pieces, and 1 to show only bottom pieces
    p1 = PlayerAB(RED_TEAM)
    p2 = ManualPlayer(BLUE_TEAM) # uncomment to use with assigned players
    return p1, p2, hide


# RED_TEAM is p1
# BLUE_TEAM is p2

p1, p2, hide = userInput() # uncomment to use with userInput (use this or noUser)

# p1, p2, hide = testInput()



# ! PlayerAb only works as Player1 



# ? if a trace value is set, comment out the randomplacements
# Note: board.printTrace() will print out a copyable list, that trace can be set to
trace = []
#attempt = [(-1, -1, 0, 0, Piece(0,0, 5, 0, 4)), (-1, -1, 0, 1, Piece(0,1, 2, 0, 1)), (-1, -1, 0, 2, Piece(0,2, 3, 0, 1)), (-1, -1, 0, 3, Piece(0,3, 7, 0, 3)), (-1, -1, 0, 4, Piece(0,4, 9, 0, 2)), (-1, -1, 0, 5, Piece(0,5, 6, 0, 1)), (-1, -1, 0, 6, Piece(0,6, 9, 0, 3)), (-1, -1, 0, 7, Piece(0,7, 5, 0, 2)), (-1, -1, 0, 8, Piece(0,8, 8, 0, 3)), (-1, -1, 0, 9, Piece(0,9, 7, 0, 4)), (-1, -1, 1, 0, Piece(1,0, 9, 0, 4)), (-1, -1, 1, 1, Piece(1,1, 8, 0, 2)), (-1, -1, 1, 2, Piece(1,2, 11, 0, 1)), (-1, -1, 1, 3, Piece(1,3, 8, 0, 5)), (-1, -1, 1, 4, Piece(2,4, 4, 0, 2)), (-1, -1, 1, 5, Piece(1,5, 8, 0, 4)), (-1, -1, 1, 6, Piece(1,6, 4, 0, 1)), (-1, -1, 1, 7, Piece(1,7, 9, 0, 7)), (-1, -1, 1, 8, Piece(1,8, 7, 0, 1)), (-1, -1, 1, 9, Piece(1,9, 5, 0, 3)), (-1, -1, 2, 0, Piece(2,0, 6, 0, 4)), (-1, -1, 2, 1, Piece(2,1, 12, 0, 1)), (-1, -1, 2, 2, Piece(2,2, 8, 0, 1)), (-1, -1, 2, 3, Piece(2,3, 12, 0, 3)), (-1, -1, 2, 4, Piece(3,4, 1, 0, 1)), (-1, -1, 2, 5, Piece(2,5, 9, 0, 6)), (-1, -1, 2, 6, Piece(2,6, 9, 0, 5)), (-1, -1, 2, 7, Piece(2,7, 5, 0, 1)), (-1, -1, 2, 8, Piece(2,8, 10, 0, 1)), (-1, -1, 2, 9, Piece(2,9, 9, 0, 1)), (-1, -1, 3, 0, Piece(3,0, 9, 0, 8)), (-1, -1, 3, 1, Piece(3,1, 12, 0, 2)), (-1, -1, 3, 2, Piece(3,2, 4, 0, 3)), (-1, -1, 3, 3, Piece(3,3, 3, 0, 2)), (-1, -1, 3, 4, Piece(4,4, 6, 0, 3)), (-1, -1, 3, 5, Piece(3,5, 7, 0, 2)), (-1, -1, 3, 6, Piece(3,6, 12, 0, 5)), (-1, -1, 3, 7, Piece(3,7, 12, 0, 4)), (-1, -1, 3, 8, Piece(3,8, 6, 0, 2)), (-1, -1, 3, 9, Piece(3,9, 12, 0, 6)), (-1, -1, 6, 0, Piece(4,0, 5, 1, 3)), (-1, -1, 6, 1, Piece(6,1, 9, 1, 5)), (-1, -1, 6, 2, Piece(6,2, 10, 1, 1)), (-1, -1, 6, 3, Piece(6,3, 9, 1, 4)), (-1, -1, 6, 4, Piece(6,4, 9, 1, 6)), (-1, -1, 6, 5, Piece(6,5, 12, 1, 3)), (-1, -1, 6, 6, Piece(6,6, 9, 1, 1)), (-1, -1, 6, 7, Piece(6,7, 8, 1, 5)), (-1, -1, 6, 8, Piece(6,8, 3, 1, 2)), (-1, -1, 6, 9, Piece(6,9, 4, 1, 2)), (-1, -1, 7, 0, Piece(7,0, 12, 1, 4)), (-1, -1, 7, 1, Piece(7,1, 4, 1, 1)), (-1, -1, 7, 2, Piece(7,2, 2, 1, 1)), (-1, -1, 7, 3, Piece(7,3, 6, 1, 3)), (-1, -1, 7, 4, Piece(7,4, 9, 1, 3)), (-1, -1, 7, 5, Piece(7,5, 12, 1, 1)), (-1, -1, 7, 6, Piece(7,6, 12, 1, 6)), (-1, -1, 7, 7, Piece(7,7, 7, 1, 1)), (-1, -1, 7, 8, Piece(7,8, 12, 1, 5)), (-1, -1, 7, 9, Piece(7,9, 7, 1, 3)), (-1, -1, 8, 0, Piece(8,0, 6, 1, 4)), (-1, -1, 8, 1, Piece(8,1, 9, 1, 8)), (-1, -1, 8, 2, Piece(8,2, 6, 1, 2)), (-1, -1, 8, 3, Piece(8,3, 9, 1, 2)), (-1, -1, 8, 4, Piece(8,4, 8, 1, 2)), (-1, -1, 8, 5, Piece(8,5, 1, 1, 1)), (-1, -1, 8, 6, Piece(8,6, 11, 1, 1)), (-1, -1, 8, 7, Piece(8,7, 3, 1, 1)), (-1, -1, 8, 8, Piece(8,8, 5, 1, 1)), (-1, -1, 8, 9, Piece(8,9, 8, 1, 1)), (-1, -1, 9, 0, Piece(9,0, 8, 1, 4)), (-1, -1, 9, 1, Piece(9,1, 5, 1, 4)), (-1, -1, 9, 2, Piece(9,2, 12, 1, 2)), (-1, -1, 9, 3, Piece(9,3, 6, 1, 1)), (-1, -1, 9, 4, Piece(9,4, 8, 1, 3)), (-1, -1, 9, 5, Piece(9,5, 5, 1, 2)), (-1, -1, 9, 6, Piece(9,6, 7, 1, 4)), (-1, -1, 9, 7, Piece(9,7, 7, 1, 2)), (-1, -1, 9, 8, Piece(9,8, 9, 1, 7)), (-1, -1, 9, 9, Piece(9,9, 4, 1, 3)), (3, 4, 4, 4, Piece(4,4, 6, 0, 3)), (6, 0, 5, 0, Piece(4,0, 5, 1, 3)), (2, 4, 3, 4, Piece(3,4, 1, 0, 1)), (5, 0, 4, 0, Piece(4,0, 5, 1, 3)), (1, 4, 2, 4, Piece(2,4, 4, 0, 2))]
p1.randomPlacements(trace) # if trace is given comment the randomplacements out
p2.randomPlacements(trace)


print("**Info**")
print("--Piece Setup:--")
print("Rank,Count_Team ; (ex: 8,3_1 -> Rank 8(miner), the 3rd miner, on team P1)\n")
print("--Piece Move Setup--")
print("row col direction(up(u), right(r), left(l), down(d)) ; (ex: 6 0 u -> moves piece at row 6, col 0 Up)")

print("\n")
g = Game(trace, p1, p2, hide)

g.runGame()
