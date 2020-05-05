from board import *
from piece import *
import copy
import math
import numpy


class BasePlayer:
    def __init__ (self, team):
        self.myPieces = []
        self.myMovables = []
        self.team = team   


    def getLikelyPiece(self, x, y, board, move = False, available = []):
        probLst = board.chanceBoard[x][y] 

        if isinstance(probLst, int):
            return None, probLst
        
        highest = max(probLst)
        
        updatedOdds = []
        if len(available) != 0:
            probLst = [probLst[i] if i+1 in available else 0 for i in range(len(probLst))]
        
        if move:
            # contains list of positions of highest value(s) in probLst
            randHigh = [i for i in range(len(probLst)-2) if probLst[i]==highest]  
        else:
            # contains list of positions of highest value(s) in probLst
            randHigh = [i for i in range(len(probLst)) if probLst[i]==highest] 


        if len(randHigh) == 1:
            valPos = randHigh[0]
            valProb = probLst[randHigh[0]]
        else:
            valPos = np.random.choice(randHigh)
            valProb = probLst[valPos]

        return valProb, valPos


    def getOtherTeam(self, team):
        if team == 1:
            return 0 
        else:
            return 1

    def printThis(self, board):
        # used to test board placements
        Board(trace = None, board = board).print()


    # Randomly places the given players pieces to start game
    def randomPlacements(self, trace):
        if self.team == RED_TEAM:
            Placeables = FULL_TEAM.copy()
            for i in range(4):
                for j in range(10):
                    if Placeables:
                        active = Placeables.pop(np.random.randint(len(Placeables)))
                        # moves from off board position to on board
                        trace.append((-1, -1, i, j, Piece(i, j, active[0], RED_TEAM, active[1], False)))
                        
                    
        else:
            Placeables = FULL_TEAM.copy()
            for i in range(6, 10):
                for j in range(10):
                    if Placeables:
                        active = Placeables.pop(np.random.randint(len(Placeables)))
                        trace.append((-1, -1, i, j, Piece(i, j, active[0], BLUE_TEAM, active[1], False)))
                       
    
    # Stores all of the movable pieces for the given player 
    # Force-populates myPieces and myMovables 
    def getMyPieces(self, board, team=None):
        self.myMovables = []
        if team == None:
            team = self.team
        else:
            team = team

        for i in range(10):
            for j in range(10):
                
                if board.board[i][j] != 0 and board.board[i][j] != LAKE:
                    if board.board[i][j].team == team:

                        self.myPieces.append(copy.copy(board.board[i][j]))

                        if board.board[i][j].rank != 11 and board.board[i][j].rank != 12:

                            self.myMovables.append(copy.copy(board.board[i][j]))


    # returns all the moves in a format of -> [(xOld, yOld, xNew, yNew), ...]
    def getAllMoves(self, board, team = None):
        self.getMyPieces(board, team)
        moves = []
        for i in self.myMovables:
            allMoves = i.getValidMoves(board)
            if allMoves != None:
                for j in allMoves:
                    moves.append(j)

        return moves


    # used in expectimax attempts
    def getProbs(self, board, team):   
        pieces = []
        for i in range(10):
            for j in range(10):
                
                if board.board[i][j] != 0 and board.board[i][j] != LAKE:
                    if board.board[i][j].team == team:

                        pieces.append(Piece(i, j,6,team,1)) # ? 6 is just a placeholder to make the move
        return pieces

    # used in expectimax attempts
    def getChanceMoves(self, pieces, board, team):
        moves = []
        moveDict = {}
        self.getProbs(board, team)
        for i in pieces:
            allMoves = i.getValidMoves(board)

            if allMoves != None:
                for j in allMoves:
                    pos = (j[0], j[1]) 
                    moveTo = (j[2],j[3])
                    if pos in moveDict:
                        moveDict[pos].append(moveTo)
                    else:
                        moveDict[pos] = [moveTo]
                    moves.append(j)
        
        return moveDict

                
    # Finds the other team
    def switchTeam(self, team):
        if team == 0:
            self.team = 0
        else:
            self.team = 1



    # Didn't end up getting to developing a complex heuristic
    def heuristic(self, board):
        value = len(board.p1Pieces) - len(board.p2Pieces)
        return value
        # for move in self.getAllMoves(board):
        #     # print("the move:", move)
        #     loc = board.board[move[2]][move[3]]
        #     if not isinstance(loc, int):
        #         if loc.rank ==11:
        #             # Found the flag
        #             if self.team == 0:
        #                 value += 30
        #             else:
        #                 value -= 30
                
        
        # # Don't leave flag open
        # for piece in self.myMovables:
        #     if self.team == 0: # player 1 on the top of the board
        #         if piece.X-1 >= 0 and (not isinstance(board.board[piece.X-1][piece.Y], int)) and board.board[piece.X-1][piece.Y].rank ==11:
        #             value -=5 # don't reveal your flag player 1

        #     else:
        #         if piece.X+1 <= 0 and (not isinstance(board.board[piece.X+1][piece.Y], int)) and board.board[piece.X+1][piece.Y].rank ==11:
        #             value +=5 # don't reveal your flag player 1


        # return 1
        # return len(board.p1Pieces) - len(board.p2Pieces)

# chooses and makes moves randomly
class RandomPlayer(BasePlayer):
    def __init__ (self, team):
        self.myPieces = []
        self.myMovables = []
        self.team = team
        self.lastMove = ()


    # Force-populates myPieces and myMovables 
    def getMyPieces(self, board):
        self.myMovables = []
        for i in range(10):
            for j in range(10):
                
                if board.board[i][j] != 0 and board.board[i][j] != LAKE:
                    if board.board[i][j].team == self.team:

                        self.myPieces.append(copy.copy(board.board[i][j]))

                        if board.board[i][j].rank != 11 and board.board[i][j].rank != 12:

                            self.myMovables.append(copy.copy(board.board[i][j]))

    # finds a random move for the random player
    def findMove(self, board):
        moves = []
        for i in self.myMovables:
            allMoves = i.getValidMoves(board)
            if allMoves != None:
                for j in allMoves:
                    moves.append(j)

        # ! it is currently 0
        if len(moves) == 0:
            return ()

        while len(moves) > 0 :
            rand = np.random.randint(len(moves)) # randomly selects a move
            chosenMove = moves.pop(rand)
            if chosenMove != (self.lastMove[:2] + self.lastMove[2:]):
                self.lastMove = chosenMove
                return chosenMove
            else:
                pass

         

class PlayerAB(BasePlayer):
    def __init__(self, team, hide=-1):
        self.hide = hide
        self.myPieces = []
        self.myMovables = []
        self.team = team   

    def alphaBeta(self, board, depth, alpha, beta, team, player):

        if board.game_over:
            # print("a game over move was found \n\n")
            if board.winner == 0:
                return (None, 10)
            elif board.winner == 1:
                return (None, -10)
        
        if depth ==0: # if terminal node
            value = self.heuristic(board)
            return (None, value)
        
        else:
            location = None
            largest = -math.inf
            smallest= math.inf

            if board.turn == 0:
                
                board = Board(board._trace, mainBoard = False, algorithmPlayer=player)

                availableMoves = self.getAllMoves(board)

                for move in availableMoves:

                    board.makeMove(*move)
                    pos, value = self.alphaBeta(board, depth-1, alpha, beta, 1, player)
                    board.undoMove()
                    board = Board(board._trace, mainBoard = False, algorithmPlayer=player)

                    if value > largest or (location is None):
                        largest = value
                        location = move
                    alpha = max(alpha, value)

                    if beta <= alpha:
                        return (None, alpha)

                return (location, largest)

            elif board.turn ==1:
                board = Board(board._trace, mainBoard = False, algorithmPlayer=player)
                self.switchTeam(1)
                availableMoves = self.getAllMoves(board)
                for move in availableMoves:
                    board.makeMove(*move)
                    pos, value = self.alphaBeta(board, depth-1, alpha, beta,  1, player)
                    board.undoMove()

                    board = Board(board._trace, mainBoard = False, algorithmPlayer=player)
                    if value < smallest or (location is None): # or (value == beta and move <location)):
                        smallest = value
                        location = move
                    beta = min(beta, value)
                    if beta <= alpha:
                        return (None, beta)

                return (location, smallest)

    def findMove(self, board, player):

        board = Board(board._trace, algorithmPlayer=player)
        store = self.team  
        player = 0
        
        if self.team == 0:
            probBoard = Board(trace = board.redTrace, mainBoard = False, algorithmPlayer=0)
            player = 0 
        else:
            probBoard = Board(trace = board.blueTrace, mainBoard = False, algorithmPlayer=1)
            player = 1
        # used to test by looking at playerab traces, set to True here to show
        if self.hide == -1:
            print("\n--PlayerAb board--\n")
            probBoard.print()
            print("--PlayerAb end--\n")


        move, score = PlayerAB.alphaBeta(self, probBoard, 2, -math.inf, math.inf, self.team, player = player)

        self.switchTeam(store)      

        return move

    
class ManualPlayer(BasePlayer):
    def __init__(self,team):
        self.myPieces = []
        self.myMovables = []
        self.team = team
        self.lastMove = ()
    
    # Manual Player findMove, and try except to catch wrong values
    def findMove(self, board):
        makeMove = ()
        while True:
            if(board.turn == 0):
                print("\n")
                selection = input("What piece location do you want to move: row col <[up, right, left, down]> ")
                selectList = selection.split(' ')

            else:

                print("\n")
                selection = input("What piece location do you want to move: row col <[u, r, l, d]>  ")
                selectList = selection.split(' ')

            # ? Check to see if valid input
            try: 
                print(selectList)
                row, col, pos = int(selectList[0]), int(selectList[1]), str(selectList[2])

            except (IndexError, ValueError) as e: 
                print("Format should be: row col pos (ex: 5 6 u)")
                continue

            # ? Check to see if a valid piece is selected
            try: 
                if board.board[row][col].isvalidPiece(board.board[row][col],self.team):
                    pass
                else:
                    raise AttributeError
            except AttributeError:
                print("invalid piece selected")
                continue 
            
            # ? Check to see if valid direction
            try: 
                print("Attempting:", (row, col), pos, "\n\n")
                
                moves = board.board[row][col].getValidMoves(board, formatted = True)


                if len(moves) > 0:

                    if pos == "down" or pos == "d":
                        # Checking if down is available move
                        if moves[0] != 0:
                            makeMove = moves[0]
                        else:
                            raise IndexError

                    elif pos == "up" or pos == "u":
                        # Checking if down is available move
                        if moves[1] != 0:
                            makeMove = moves[1]
                        else:
                            raise IndexError

                    elif pos == "right" or pos == "r":
                        # Checking if down is available move
                        if moves[2] != 0:
                            makeMove = moves[2]
                        else:
                            raise IndexError

                    elif pos == "left" or pos == "l":
                        # Checking if down is available move
                        if moves[3] != 0:
                            makeMove = moves[3]
                        else:
                            raise IndexError
                    else:
                        print("invalid direction")
                        raise IndexError

            except IndexError: 
                print("invalid Move")
                continue

            
            # Makes it so the Manual Player can't move back in forth [depends on rules you play with]
            try: 
                if False: #makeMove == (self.lastMove[2:] + self.lastMove[:2]) :
                    raise ValueError
                else:
                    self.lastMove = makeMove
                    return makeMove
            except ValueError:
                print("you can't move back and forth!")
                continue





# ? Attempted to implement Expectimax algorithm here
# Tried multiple ways of implementing an expectimax algorithm as shown by the multiple functions
# Ultimately didn't end up getting it to work properly in time
# Would have taken into account the chance again for a piece to by placed
# This would have allowed us to weight the moves and what the heuristic returned based 
# on the probability of a piece being the assigned value

'''
class PlayerEx(BasePlayer):
    def findMove(self, board):
        
        # board = Bocrard(trace)
        # board.print()
        boardMain = Board(board._trace)
        team = self.team

        probBoard = boardMain.probBoard
        p1Board = boardMain.p1Board
        p2Board = boardMain.p2Board
        


    
        # print("\n\n\n\n\n\n\n\n\n\n\n")
        # if team == 0: 
        #     board = boardMain.p1Board # partially observable board
        # else:
        #     board = boardMain.p2Board # partially observable board
        
        boardMain.print()

        move, score = PlayerEx.expect(self, boardMain, 3, team)


        # print("this is player: ", team)
        print("we are out of expectiminimax \n\n")
        print(move, score)
        # board.print()
        # print(board)

        return move


    
    # Returns probability, position of piece in list (add 1 for rank)
    def getLikelyPiece(self, x, y, board, move = False):
        probLst = board.chanceBoard[x][y] 

        if isinstance(probLst, int):
            return None, probLst

        highest = max(probLst)
    
        if move:
        # Subtract 2 from length to eliminate possibility of moving Flag or Bomb
            randHigh = [i for i in range(len(probLst)-2) if probLst[i]==highest] 
        else:
            randHigh = [i for i in range(len(probLst)) if probLst[i]==highest] 

        if len(randHigh) == 1:
            randVal = probLst[randHigh[0]]
        else:
            valPos = np.random.choice(randHigh)
        randVal = probLst[valPos]

        return randVal, valPos



    def exp(self, board, depth, team, startBoard):

        if depth == 0:
            return (None, self.heuristic(board))
        
        if depth ==3: #calculate chances first
            otherTeam = self.getOtherTeam(team)
            alpha = 0
            chancePieces = self.getProbs(board, otherTeam)

            # Goes through keys
            for piece in chancePieces:      
                randVal, valPos = self.getLikelyPiece(piece.X, piece.Y, board, move= True)

                tempPiece = Piece(piece.X, piece.Y, valPos+1, otherTeam, 1)
                board.board[piece.X][piece.Y] = tempPiece

                move, value = self.expect(board, depth-1, otherTeam)

                alpha += alpha + (randVal * value)
        
        else:
            otherTeam = self.getOtherTeam(team)
            location = None

            # Return value of maximum-valued child node
            if team == 0:
                alpha = -math.inf
            else:
                alpha = math.inf
            
            # print("could be altered:")
            # board.print()
            availableMoves = self.getAllMoves(board, team)

            for move in availableMoves:
                
                valProb, valPos = self.getLikelyPiece(move[2],move[3], board, move = False)
                if valProb is not None:
                    tempPiece = Piece(move[2], move[3], valPos+1, otherTeam, 1)
                    board.board[move[2]][move[3]] = tempPiece # reassigns value for probability
                
                board.makeMove(*move) 
                move, val = self.expect(board, depth-1, team)
                board.undoMove()
                board = Board(board._trace)

                # print(alpha, "vs", val, "new: ", move, "and", team)
                
                if team == 0 and alpha < val:
                    location = move 
                    alpha = val
                elif team ==1 and alpha > val:
                    location = move
                    alpha = val
                elif location is None:
                    location = move
                    alpha = val






    def expect(self, board, depth, team):
        
        print("depth: ", depth, "and turn", board.turn)

        # board.print()
        # print("\n\n\n\n\n\n")
        # Terminal node
        if depth == 0:
            val = self.heuristic(board)
            print(self.heuristic(board))
            return  (None, self.heuristic(board))
        

        # Minimaxplayer is playing
        if depth%2!=0: #board.turn == team:
            otherTeam = self.getOtherTeam(team)
            location = None

            # Return value of maximum-valued child node
            if team == 0:
                alpha = -math.inf
            else:
                alpha = math.inf
            
            # print("could be altered:")
            # board.print()
            availableMoves = self.getAllMoves(board, team)

            for move in availableMoves:
                
                valProb, valPos = self.getLikelyPiece(move[2],move[3], board, move = False)
                if valProb is not None:
                    tempPiece = Piece(move[2], move[3], valPos+1, otherTeam, 1)
                    board.board[move[2]][move[3]] = tempPiece # reassigns value for probability
                
                board.makeMove(*move) 
                move, val = self.expect(board, depth-1, team)
                board.undoMove()
                board = Board(board._trace)

                print(alpha, "vs", val, "new: ", move, "and", team)
                
                if team == 0 and alpha < val:
                    location = move 
                    alpha = val
                elif team ==1 and alpha > val:
                    location = move
                    alpha = val
                elif location is None:
                    location = move
                    alpha = val

            return (location, alpha)


        elif depth%2 ==0:
            otherTeam = self.getOtherTeam(team)
            alpha = 0
            chancePieces = self.getProbs(board, otherTeam)

            # Goes through keys
            for piece in chancePieces:      
                randVal, valPos = self.getLikelyPiece(piece.X, piece.Y, board, move= True)

                tempPiece = Piece(piece.X, piece.Y, valPos+1, otherTeam, 1)
                board.board[piece.X][piece.Y] = tempPiece

                move, value = self.expect(board, depth-1, otherTeam)

                alpha += alpha + (randVal * value)

                    # board.undoMove()
                    # board = Board(board._trace)

                return (move, alpha)


    
    def expectiminimax(self, board, depth, team):

        print("given", depth, team, board.turn)
        if depth == 0:
            val = self.heuristic(board)
            return  (None, self.heuristic(board))
        

        # Minimaxplayer is playing
        if board.turn == team:
            print("our team checking out \n")
            location = None

            # Return value of maximum-valued child node
            alpha = -math.inf
            availableMoves = self.getAllMoves(board)
            print(availableMoves)
            for move in availableMoves:
                board.makeMove(*move) 
                print("main person moving:", move)
                move, val = self.expectiminimax(board, depth-1, team)
                board.undoMove()
                board = Board(board._trace)
                
                if alpha < val or location is None:
                    location = move 
                    alpha = val

            return (location, alpha)


        elif board.turn != team:
            
            # otherTeam =  0 if team ==1 else 1
            otherTeam = self.getOtherTeam(team)
            print("Opposing team checking out\n")
            print(otherTeam)
            # Return weighted average of all child nodes' values
            alpha = 0
            chanceMoves = self.getProbs(board, otherTeam)

            # Goes through keys
            for move in chanceMoves:

                probLst = board.chanceBoard[move[0]][move[1]] 
                highest = max(probLst)

                # Subtract 2 from length to eliminate possibility of moving Flag or Bomb
                randHigh = [i for i in range(len(probLst)-2) if probLst[i]==highest] 

                if len(randHigh) == 1:
                    randVal = probLst[randHigh[0]]
                else:
                    valPos = np.random.choice(randHigh)
                randVal = probLst[valPos]

                
                for moveTo in chanceMoves[move]:

                    
                    tempPiece = Piece(move[0], move[1], valPos+1, otherTeam, 1)
                    board.makeMove(move[0], move[1],moveTo[0], moveTo[1], tempPiece)
                    tempPiece.print()
                    board.print()
                    move, value = self.expectiminimax(board, depth-1, team)

                    alpha += alpha + (randVal * value)

                    board.undoMove()
                    board = Board(board._trace)

                    return (move, alpha)
        # elif board.turn == team and team == 1:
        #     location = None
        #     # Return value of maximum-valued child node
        #     alpha = +math.inf
        #     availableMoves = self.getAllMoves(board)
        #     # print(availableMoves)
        #     for move in availableMoves:
        #         board.makeMove(*move) 
        #         move, val = self.expectiminimax(board, depth-1, team)
        #         board.undoMove()
        #         board = Board(board._trace)
                
        #         if alpha > val or location is None:
        #             location = move 
        #             alpha = val

        #     return (location, alpha)


    

        

class PlayerExpMax(BasePlayer):


    def expectimax(self, board, depth, team):

        if board.game_over:
            print("a game over move was found \n\n")
            return (None, 1000000000)
        
        if depth ==0: # if terminal node
            value = self.heuristic(board)
            # print("what value is returned for this:", value)
            return (None, value)
        
        else:
            location = None
            largest = -math.inf
            smallest= math.inf
            # finding max
            board = Board(board._trace)

            availableMoves = board.getAllValidMoves()
            
            if board.turn == 0:

                if team == 0:
                    for value in availableMoves:
                        board.makeMove(value)
                        temp_pos, temp = self.expectimax(board,depth-1)
                        board.undoMove()
                        if temp > largest or (location is None):
                            largest = temp
                            location = value
                    return (location, largest)
                else:
                    # for value in hiddenMoves:
                        
                    
                    pass
                    #prob
            elif board.turn ==1:
                if team ==1:
                    for value in availableMoves:
                        board.makeMove(value)
                        temp_pos, temp = self.expectimax(board,depth-1)
                        board.undoMove()
                        if temp < smallest or (location is None):
                            smallest = temp
                            location = value
                    return (location, smallest)
                else:
                    pass


        def findMove(self, board):
        
            # board = Board(trace)
            # board.print()
            board = Board(board._trace)
            store = self.team
            move, score = PlayerExpMax.expectimax(self, board, 2)

            self.switchTeam(store)
            # board.undoMove()
            # board.print()
            # board.printTrace()
            # board(board_trace).print()
            # board.print()

            return move


'''   
  