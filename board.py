import numpy as np
import random
from piece import *


LAKE = -1
RED_TEAM = 0
BLUE_TEAM = 1
SPY = 1
FLAG = 11
BOMB = 12

GAME_OVER = False

# (RANK, COUNT)
# First, rank of piece (rank), second as ID (of which piece of rank it is)
# Generates a standard team's representations for the game
FULL_TEAM = [(1, 1), (2, 1), (3, 1), (3, 2), (4, 1), (4, 2), (4, 3), 
             (5, 1), (5, 2), (5, 3), (5, 4), 
             (6, 1), (6, 2), (6, 3), (6, 4), 
             (7, 1), (7, 2), (7, 3), (7, 4), 
             (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), 
             (9, 1), (9, 2), (9, 3), (9, 4), 
             (9, 5), (9, 6), (9, 7), (9, 8), (10, 1), 
             (11, 1), (12, 1), (12, 2), (12, 3), (12, 4),
             (12, 5), (12, 6)]


FULL_TEAM_LIST = [1, 2, 3, 3, 4, 4, 4, 5, 5, 5,
                  5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 
                  8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 
                  9, 9, 10, 11, 12, 12, 12, 12, 12, 12]


class Board:
    def __init__(self, trace = None, board = None, mainBoard = True, algorithmPlayer = 0):
        self._trace = [] # holds the trace of the moves
        self.mainBoard = mainBoard # used in alpha-beta for determing if it's the gameboard
        self.board = [[0 for j in range(10)] for i in range(10)] # contains 2d array of pieces
        self.game_over = False
        self.winner = -1
        self.turn = 0 
        self.discovered = {} # stores pieces that have been discovered
        self.redPlaceables = FULL_TEAM_LIST.copy() # stores all available red pieces
        self.bluePlaceables = FULL_TEAM_LIST.copy() # stores all available blue pieces
        
        self.allPieces = [] # stores all pieces on the board
        self.p1Pieces = [] # stores only player1 pieces
        self.p2Pieces = [] # stores only player 2 pieces

        self.lastMoves = [] # [(xOld, yOld, Piece), ...], stores last made move

        self.p1Board = [[0 for j in range(10)] for i in range(10)] # shows correct p1 pieces, and probability p2 pieces

        self.p2Board = [[0 for j in range(10)] for i in range(10)] # shows correct p2 pieces, and prob p1 pieces

        # Place lakes
        self.board[4][2] = LAKE
        self.board[5][2] = LAKE 
        self.board[4][3] = LAKE 
        self.board[5][3] = LAKE 
        self.board[4][6] = LAKE 
        self.board[5][6] = LAKE 
        self.board[4][7] = LAKE 
        self.board[5][7] = LAKE 

       

        # Matrix is setup like self.board, but each chanceBoard[x][y] contains
        # a list of length 12 where each indices represents each possible piece
        # and each indices value is the probability that they occur at this x, y location
        self.chanceBoard = [[0 for j in range(10)] for i in range(10)] 
        

        
        # sets each initial probability to be the same for each indice
        for i in range(4):
            for j in range(10):
                self.chanceBoard[i][j] = [1/12 for k in range(0, 12)] # pieces values are from 1 to 12

        for i in range(6,10):
            for j in range(10):
                self.chanceBoard[i][j] = [1/12 for k in range(0, 12)]

         # Places chanceboard lakes
        self.chanceBoard[4][2] = LAKE
        self.chanceBoard[5][2] = LAKE 
        self.chanceBoard[4][3] = LAKE 
        self.chanceBoard[5][3] = LAKE 
        self.chanceBoard[4][6] = LAKE 
        self.chanceBoard[5][6] = LAKE 
        self.chanceBoard[4][7] = LAKE 
        self.chanceBoard[5][7] = LAKE 


        # used to minimize issues with placing randomPiece placement on the board with placeables
        # this also limits only 1 abplayer per time though
        self.algorithmPlayer = algorithmPlayer # if 0 means only need to generate p2 pieces/blue  


        # Uses trace to generate board and setu pieces
        if trace is not None and len(trace) != 0:
            for m in trace:
                # m -> (x1, y1, x2, y2, piece)
                if self.isValidMove(m[0],m[1],m[2],m[3], m[4].team):

                    if m[0] == -1 and m[1] == -1 and m[2] != -1 and m[3] != -1:
                        #  moving pieces from off the board onto the board
                        self.setupBoard(m[2], m[3], m[4])
                        
                    elif m[0] != 0 and m[1] != 0 and m[2] == -1 and m[3] == -1:
                        #  moves piece off board
                        self.deletePiece(m[0], m[1])
                    else:
                        # actually makes a move
                        self.makeMove(m[0], m[1], m[2], m[3])
                else:
                    print("invalid move attempted")


        # only used for the main gameBoard (not used for depth searching part in game trees)
        if mainBoard:
            self.probabilites = {}

            # a check to see if board was sent in rather than trace
            if board is not None:
                self.board = board

            self.probBoard, self.redTrace, self.blueTrace = self.createProbBoard() # Creates a probability board and assigns vals


            # Matrix :  Board    probBoard  p1Board   p2Board
            # Top(P1):  Actual   Prob       Actual    Prob
            # Bot(P2):  Actual   Prob       Prob      Actual

            # Initializes p1Board and p2Board with their known and probability values
            for r in range(0,10):
                for c in range(0,10):
                    if not isinstance(self.board[r][c], int):

                        if self.board[r][c].team ==0:
                            # player 1 piece
                            self.p1Board[r][c] = self.board[r][c]
                            self.p2Board[r][c] = self.probBoard[r][c] # what p1 sees for this part of the board
                        else:
                            # player 2 piece
                            self.p1Board[r][c] = self.probBoard[r][c]
                            self.p2Board[r][c] = self.board[r][c]
                    else:
                        # space and lakes
                        self.p1Board[r][c] = self.board[r][c]
                        self.p2Board[r][c] = self.board[r][c]

    
    # Sets up the initial Board, used by the trace function
    def setupBoard(self, x, y, piece):

        self.board[x][y] = piece
        piece.X = x 
        piece.Y = y
        # ! check to see if the above matters
        self._trace.append((-1, -1, x, y, piece))

        self.allPieces.append(piece)

        if not isinstance(piece, int):
            if piece.team == 0:
                self.p1Pieces.append(piece)
            else:
                self.p2Pieces.append(piece)


    # gets the most likely piece at location x,y given the piece is available to be placed
    # Returns probability of piece occuring, index of piece (add 1 to be the piece rank)
    def getLikelyPiece(self, x, y, available = []):
        # Example of start probability
        # Piece                         1      2        3       4       5       6      7        8       9      10      11     12
        # self.chanceBoard[x][y] -> [0.0833, 0.0833, 0.0833, 0.0833, 0.0833, 0.0833, 0.0833, 0.0833, 0.0833, 0.0833, 0.0833, 0.0833]

        # Example of known probability (the piece is known to be a 5!)
        # Piece                       1  2  3  4   5   6  7  8  9  10  11  12
        # self.chanceBoard[x][y] -> [ 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 0,  0,  0]

        probLst = self.chanceBoard[x][y] 

        if isinstance(probLst, int):
            return None, probLst
        
        highest = max(probLst)
        
        updatedOdds = []

        def getNumStationary(lst):
            count = sum([1 if i in [11, 12] else 0 for i in lst])
            return count

        if len(available) != 0:
            notAvailable = [i for i in range(1,13) if i not in available]
            for i in notAvailable:
                self.adjustProb(x, y, i, 0)
            
            probLst = self.chanceBoard[x][y]

        # if move:
        #     # contains list of positions of highest value(s) in probLst
        #     # randHigh = [i for i in range(len(probLst)-2) if probLst[i]==highest]  
        # else:
            # contains list of positions of highest value(s) in probLst
        randHigh = [i for i in range(len(probLst)) if probLst[i]==highest] 

        if len(randHigh) == 1:
            valPos = randHigh[0]
            valProb = probLst[randHigh[0]]
        else:
            probLst = probLst[::-1] # likes to choose 12's at end before
            valPos = np.random.choice(np.arange(11, -1,-1), 1, p=probLst)
            valPos = valPos[0]
            valProb = probLst[valPos]

        return valProb, valPos



    # Creates a Probability board, chooses most likely piece for each location on the board 
    # boards/traces created from this functionused by alpha-beta to generate the opponents board
    def createProbBoard(self):
        chanceBoard = self.chanceBoard
        chancePlacements = []
        
        probTrace = []
        redPlaceables = self.redPlaceables.copy() # just a copy of the possible placeable red pieces
        bluePlaceables = self.bluePlaceables.copy() 
        
        redTrace = [] # used to store a trace for creation of p1Board (actual / prob)
        blueTrace = [] # used to store a trace for creation of p2board (prob / actual)
        redOnBoard = [] # stores # of red pieces on the board (used to store piece count)
        blueOnBoard = [] # stores # of blue pieces on the board (used to store piece count)


        for i in range(len(self.board)):
            tempRow = []
            for j in range(len(self.board[i])):
                pos = self.board[i][j]
                if isinstance(pos, int):
                    # if it's a lake or space
                    tempRow.append(pos)
                else:
                    if self.algorithmPlayer ==1 and pos.team == 0:
                        if (not isinstance(self.chanceBoard[i][j], int)) and self.chanceBoard[i][j].count(1) == 1:
                            # if one of the values in the probability list is 1, then it is known and assigns the respective value
                            pieceRank = self.chanceBoard[i][j].index(1)+1 # adds 1 to be the actual piece Rank
                            tempPiece = Piece(i, j, pieceRank,pos.team, redOnBoard.count(pieceRank)+1) 

                        else:
                            prob, piece = self.getLikelyPiece(i, j, available = redPlaceables) # finds a possible piece
                            pieceRank = piece +1
                            redPlaceables.remove(pieceRank) 

                            # Creats the piece with it's rank, team, and count
                            tempPiece = Piece(i, j, pieceRank, pos.team, redOnBoard.count(pieceRank)+1)

                        tempRow.append(tempPiece) 
                        redOnBoard.append(piece) 

                        blueTrace.append((-1, -1, i, j, tempPiece)) # Adds Prob value because not their team
                        redTrace.append((-1, -1, i, j, pos)) # adds Actual value because this is their team
                            
                    elif self.algorithmPlayer ==0 and pos.team ==0:
                        tempRow.append(pos) 
                        blueTrace.append((-1, -1, i, j, pos)) # Adds Prob value because not their team
                        redTrace.append((-1, -1, i, j, pos)) # adds Actual value because this is their team


                    elif self.algorithmPlayer== 0 and pos.team ==1:
                        if (not isinstance(self.chanceBoard[i][j], int))  and self.chanceBoard[i][j].count(1) == 1:
                            pieceRank = self.chanceBoard[i][j].index(1)+1
                            tempPiece = Piece(i, j, pieceRank, pos.team, blueOnBoard.count(pieceRank)+1)
                        else:
                            prob, piece = self.getLikelyPiece(i, j, available = bluePlaceables)
                            pieceRank = piece +1
                            bluePlaceables.remove(pieceRank)
                            tempPiece = Piece(i, j, pieceRank, pos.team, blueOnBoard.count(pieceRank)+1)

                        tempRow.append(tempPiece)
                        blueOnBoard.append(pieceRank)
                        redTrace.append((-1,-1, i, j, tempPiece)) # gives redTrace calculated prob piece
                        blueTrace.append((-1, -1, i, j, pos)) # gives blueTrace actual value
                    

                    elif self.algorithmPlayer ==1 and pos.team ==1:
                        tempRow.append(pos) 
                        blueTrace.append((-1, -1, i, j, pos))
                        redTrace.append((-1, -1, i, j, pos))


            chancePlacements.append(tempRow) # add to the board creation
        
        return chancePlacements, redTrace, blueTrace



    # Creates a Probability board, chooses most likely piece for each location on the board 
    # boards/traces created from this functionused by alpha-beta to generate the opponents board
    # this is without checking which team the probability placements need to be made for 
    # will make errant placements more than the other version
    '''
    def createProbBoard(self):
        chanceBoard = self.chanceBoard
        chancePlacements = []
        
        probTrace = []
        redPlaceables = self.redPlaceables.copy() # just a copy of the possible placeable red pieces
        bluePlaceables = self.bluePlaceables.copy() 
        
        redTrace = [] # used to store a trace for creation of p1Board (actual / prob)
        blueTrace = [] # used to store a trace for creation of p2board (prob / actual)
        redOnBoard = [] # stores # of red pieces on the board (used to store piece count)
        blueOnBoard = [] # stores # of blue pieces on the board (used to store piece count)


        for i in range(len(self.board)):
            tempRow = []
            for j in range(len(self.board[i])):
                pos = self.board[i][j]
                if isinstance(pos, int):
                    # if it's a lake or space
                    tempRow.append(pos)
                else:
                    if pos.team == 0:
                            if (not isinstance(self.chanceBoard[i][j], int)) and self.chanceBoard[i][j].count(1) == 1:
                                # if one of the values in the probability list is 1, then it is known and assigns the respective value
                                pieceRank = self.chanceBoard[i][j].index(1)+1 # adds 1 to be the actual piece Rank
                                tempPiece = Piece(i, j, pieceRank,pos.team, redOnBoard.count(pieceRank)+1) 
    
                            else:
                                prob, piece = self.getLikelyPiece(i, j, available = redPlaceables) # finds a possible piece
                                pieceRank = piece +1
                                redPlaceables.remove(pieceRank) 

                                # Creats the piece with it's rank, team, and count
                                tempPiece = Piece(i, j, pieceRank, pos.team, redOnBoard.count(pieceRank)+1)

                            tempRow.append(tempPiece) 
                            redOnBoard.append(piece) 

                            blueTrace.append((-1, -1, i, j, tempPiece)) # Adds Prob value because not their team
                            redTrace.append((-1, -1, i, j, pos)) # adds Actual value because this is their team


                    elif pos.team ==1:
                        if (not isinstance(self.chanceBoard[i][j], int))  and self.chanceBoard[i][j].count(1) == 1:
                            pieceRank = self.chanceBoard[i][j].index(1)+1
                            tempPiece = Piece(i, j, pieceRank, pos.team, blueOnBoard.count(pieceRank)+1)
                        else:
                            prob, piece = self.getLikelyPiece(i, j, available = bluePlaceables)
                            pieceRank = piece +1
                            bluePlaceables.remove(pieceRank)
                                       
                    
                            tempPiece = Piece(i, j, pieceRank, pos.team, blueOnBoard.count(pieceRank)+1)
                        tempRow.append(tempPiece)
                        blueOnBoard.append(pieceRank)
                        redTrace.append((-1,-1, i, j, tempPiece)) # gives redTrace calculated prob piece
                        blueTrace.append((-1, -1, i, j, pos)) # gives blueTrace actual value
            chancePlacements.append(tempRow) # add to the board creation
        
        return chancePlacements, redTrace, blueTrace
    '''

    # undos the last move from the trace
    def undoMove(self):
        self._trace.pop() # removes the last added move

    
    # given x, y piece moved therefore it cannot be a flag or bomb, probs adjusted as such
    def isMoveable(self, x, y):
        # used to remove probability of flag and bomb for pieces that have moved  
        if (not isinstance(self.chanceBoard[x][y],int)) and self.chanceBoard[x][y][:-2] != [0,0]:
            # only does it the first time
            self.adjustProb(x, y, 11, 0)
            self.adjustProb(x, y, 12, 0)
    

    # used to adjustProbabilties of pieces in the chanceBoard
    def adjustProb(self, x, y, pieceNum, prob):
        # Actual PieceNum is converted to format used here. Piece are 1-12(incl). 
        # chanceBoard[x][y] is 0 to 11(incl)

        pieceNum = pieceNum -1 

        # Piece found/revealed 100%
        if prob == 1:
            team = self.board[x][y] # ! time

            self.chanceBoard[x][y][pieceNum] = 1 # Update the probability of the known piece
            self.chanceBoard[x][y][:pieceNum] = [0 for i in range(pieceNum)]
            self.chanceBoard[x][y][pieceNum+1:] = [0 for i in range(12-pieceNum-1)]

            # Guarantees this piece won't be placed anywhere else on the board when a probBoard is created
            # needs to take into consideration the count of this kind of piece
            for i in range(len(self.chanceBoard)):
                for j in range(len(self.chanceBoard[i])):
                    if (not isinstance(self.board[i][j], int)) and self.board[i][j].team == team and (x!=i or y!=j):
                        self.adjustProb(i, j, pieceNum+1, 0) # no other piece can be this one
            
        
        # remove probability of this piece
        elif prob == 0:
            if self.chanceBoard[x][y][pieceNum] != 0:
                difference = 12 - (self.chanceBoard[x][y].count(0) +1) # finds the number of pieces left (aren't 0)
                    
                if difference >=1:
                    newProb = 1 / difference

                    self.chanceBoard[x][y][pieceNum] = 0 # Update the probability of the known piece
                    
                    # updates other pieces in the chanceBoard with new Probability
                    for i in range(0,12):
                        if i!= pieceNum and self.chanceBoard[x][y][i] != 0:
                            self.chanceBoard[x][y][i] = newProb
        else:
            pass
            
       
    
    # Removes the piece at x, y from the board
    def deletePiece(self, x, y):
        self.board[x][y] = 0
        self.chanceBoard[x][y] = 0 
        
        
    
    # moves the given piece to board[x][y], also adjusts chanceboard
    def setPiece(self, x, y, piece = None, xOld= 0, yOld=0, chance = False):
        
        if piece == None:

            piece = self.board[xOld][yOld] # piece hasn't been moved yet so still in old spot

            # if this is the gameBoard, make moves on the chance board
            if self.mainBoard:
                probPiece = self.chanceBoard[xOld][yOld]
       

        if chance and self.mainBoard: 
            # Used for updating probabilistic matrix
            self.chanceBoard[x][y] = probPiece # mirrors the actual board
            self.isMoveable(x, y)
            
        # updates the piece's own x, y
        piece.X = x 
        piece.Y = y 

        self.board[x][y] = piece # piece is set to new location
        self.allPieces.append(piece) 

        if not isinstance(piece, int):
            if piece.team == 0:
                self.p1Pieces.append(piece)
            else:
                self.p2Pieces.append(piece)
             
    # used for testing to print out a copyable trace
    # the printed trace can be used in game.py as the given trace        
    def printTrace(self):
        output = "["
        for i in self._trace:
            output += "("+str(i[0]) + ", " + str(i[1]) + ", " + str(i[2]) + ", " + str(i[3]) + ", " + str(i[4].print(False)) + "), "
        output = output[:-2] # removes last ", " including blank
        output += "]"
        print(output)

    
    # Print formatting for the gameBoard. Team used to hide pieces 
    def print(self, team = -1): 
        spaces = 0 
        
        for i in range(-1, 10,1): 
            #Escapetext for script and background colors 
            rowString = "\033[1:32:40m " 
            
            if i == -1:
                rowString += "   "
                for k in range(10):
                    rowString += " " + (str(k) + "      ") 
                print(rowString + "\n")

            else:
                rowString += str(i) + " |"

                for j in range(10): 
                    activePiece = self.board[i][j] 
                    if isinstance(activePiece, int): 
                        # rowString += '{0:5}'.format(str(activePiece)) 
                        rowString += " " + (str(activePiece) + "     ") 
                        if activePiece == 0: 
                            rowString += " " 
                    elif team == -1 or activePiece.team == team:
                            rowString += " " + (str(activePiece.rank) +","+ str(activePiece.count) + "_"+ str(activePiece.team+1)+ " ") 
                            if activePiece.rank != 12 and activePiece.rank != 11 and activePiece.rank != 10: 
                                rowString += " " 
                    else:
                        rowString += " [_]    "
                   
                        # ? Used for blocking out pieces
                        
                           

                rowString += "\n" 
                print(rowString)
        
        # Board function for handling attack encounters between different pieces.
        # Processed by the board instead of the AI, since true board identities are
        # known by the board and rules, rather than the players themselves.


    # return true if x and y are valid location
    def inBounds(self, x, y):
        if x>=0 and x<= 9 and y>=0 and y<=9:
            return True
        return False


    # Returns if a move from (x1,y1) -> (x2, y2) is valid (True, False)
    def isValidMove(self, x1, y1, x2, y2, team):
        
        if x1 == -1 and y1 == -1 and self.inBounds(x2, y2):
            # Used for start board moving piece from empty position to on the board
            return True
            
        elif x2 == -1 and y2 == -1 and self.inBounds(x1, y1):
            # used by trace to move a piece off the board
            return True
        
        elif not(self.inBounds(x1, y1) and self.inBounds(x2, y2)):
            # out of bounds
            return False
   
        # Check if move is a neighbor
        if not ((x1, y1, x2, y2) in self.board[x1][y1].getValidMoves(self)):
            return False

        # Check if player is trying to move their bomb or flag
        if self.board[x1][y1].rank == FLAG or self.board[x1][y1].rank == BOMB:
            return False

        # Check for if a 0 or -1 is attempting to be moved
        if self.board[x1][y1] == 0 or self.board[x1][y1] == LAKE:
            return False 
        
        # Checking if moving into lake
        if self.board[x2][y2] == LAKE:
            return False
        
        # Check if attempting to move into own team
        if self.board[x1][y1].team != team:
            return False

        # checks if moving into blank space
        if self.board[x2][y2] == 0:
            return True

        else:
            # an attack 
            if self.board[x1][y1].team != self.board[x2][y2]:
                # Moving into opposing player to attack
                return True
            else:
                # Trying to move into own player
                # print("You can't attack your own team!")
                return False
    
    


    # Rank, team has been deleted from the board, and updates respective placeable list
    def removePlaceable(self, rank, team):
        if team == 0:
            self.redPlaceables.remove(rank) # player1
        elif team ==1:
            self.bluePlaceables.remove(rank) # player2
        else:
            pass

        
    def makeMove(self, x1, y1, x2, y2, piece = None, trace = None):

        # Switches the turn
        if self.turn ==0:
            self.turn =1
        else:
            self.turn =0
        
        piece = self.board[x1][y1]
        self._trace.append((x1, y1, x2, y2, piece)) # adds this move to the trace


        attackPiece = self.board[x1][y1]
        defendPiece = self.board[x2][y2]

        # Grab ranks of the defender and attacker
        attkVal = attackPiece.rank

        if not isinstance(defendPiece, int):
            defVal = defendPiece.rank

        # Moves attacking piece into empty space
        if defendPiece == 0:

            self.setPiece(x2, y2, None, x1, y1, True)
            self.deletePiece(x1, y1)


        # Spy attacks Marshall(1)
        elif attkVal == 10 and defVal == 1:
            self.deletePiece(x2,y2)
            self.setPiece(x2, y2, None, x1, y1, True)
            self.deletePiece(x1, y1)
            
            if self.mainBoard: self.adjustProb(x2, y2, attkVal, 1) # Guaranteed spy 

            self.removePlaceable(defVal, defendPiece.team)

        # Equal value, both pieces die
        elif attkVal == defVal:                
            self.deletePiece(x1, y1)
            self.deletePiece(x2, y2)

            # if attkVal == 9:
            #     if self.mainBoard: self.adjustProb(x2, y2, defVal, 1) # Confirmed Miner
            #     if self.mainBoard: self.adjustProb(x1, y1, attkVal, 1)

            self.removePlaceable(defVal, defendPiece.team)
            self.removePlaceable(attkVal, attackPiece.team)

            
        # Miner(8) removes defending bomb
        elif attkVal == 8 and defVal == 12:
            self.deletePiece(x2,y2)
            self.setPiece(x2, y2, None, x1, y1, True)
            self.deletePiece(x1, y1)

            if self.mainBoard: self.adjustProb(x2, y2, attkVal, 1) # Confirmed Miner

            self.removePlaceable(defVal, defendPiece.team)

        # Bomb kills attack piece
        elif attkVal != 8 and defVal == 12:      
            self.deletePiece(x1, y1)

            if self.mainBoard: self.adjustProb(x2, y2, defVal, 1) # Confirmed bomb at defending position

            self.removePlaceable(attkVal, attackPiece.team)

        # Found the flag!
        elif defVal == 11 and attackPiece.team != defendPiece.team:
            self.game_over = True
            self.winner = attackPiece.team
            if self.mainBoard:
                print("\n\n***FOUND THE FLAG***")
                print("AT position:", x2, y2)
                print("Player", attackPiece.team+1, "wins")
            
        
        # attacker kills defending piece
        elif attkVal < defVal:
            self.deletePiece(x2,y2)
            self.setPiece(x2, y2, None, x1, y1, True)
            self.deletePiece(x1, y1)

            if self.mainBoard: self.adjustProb(x2, y2, attkVal, 1) # attacking value is confirmed

            self.removePlaceable(defVal, defendPiece.team)

        # attacker dies to defending piece
        elif attkVal > defVal:                   
            self.deletePiece(x1, y1)

            if self.mainBoard: self.adjustProb(x2, y2, defVal, 1) # defending value confirmed

            self.removePlaceable(attkVal, attackPiece.team)

        else:
            print("SOMETHING GOT THROUGH********\n\n")