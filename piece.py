from board import * 


FLAG = 11
BOMB = 12
LAKE = -1

class Piece:
        def __init__(self, x, y, rank, team, count, knownStat = []):
            self.X = x
            self.Y = y
            self.rank = rank # switche id to rank for better naming
            self.count = count
            self.team = team
            self.isKnown = knownStat

        def print(self, show = True):
            if show:
                output = "Piece: (" + str(self.X) +"," + str(self.Y) + "), rank: " + str(self.rank) + ", team:" + str(self.team) +", count:" + str(self.count)
                print(output)
            else:
                output = "Piece(" + str(self.X) +"," + str(self.Y) + ", " + str(self.rank) + ", " + str(self.team) + ", " + str(self.count) + ")"
                return output

        def inBoard(self, pos):
            if pos >= 0 and pos <=9:
                return True
            return False

        def isvalidPiece(self, piece, team):

            if piece == 0 or piece == -1 or piece.rank == BOMB or piece.rank == FLAG:
                # print("invalid piece selection")
                return False
            elif piece.rank == 11:
                return False
            
            if not (piece.inBoard(piece.X) and piece.inBoard(piece.Y)):
                return False
            
            if piece.team != team:
                return False
            return True

        
        def isValidMove(self, piece, team):
            if piece == 0:
                return True
            if piece == LAKE:
                return False
            if piece.team == team:
                return False
            else:
                # Attacks
                return True

        # gets all the valid moves for the piece
        def getValidMoves(self,board, formatted = False):
            if board.board[self.X][self.Y]==0 or board.board[self.X][self.Y] ==11 or board.board[self.X][self.Y]==12 or board.board[self.X][self.Y] == FLAG:
                if formatted:
                    return [0,0,0,0]
                else:
                    return []

            elif self.rank != 9: 
                out = []
                form = []
                neibs = [(self.X + 1, self.Y), (self.X - 1, self.Y),
                         (self.X, self.Y + 1), (self.X, self.Y-1)]
                
                for i in neibs:

                    if self.inBoard(i[0]) and self.inBoard(i[1]):

                        if self.isValidMove(board.board[i[0]][i[1]],board.board[self.X][self.Y].team):
                            out.append((self.X, self.Y, i[0], i[1]))
                            form.append((self.X, self.Y, i[0], i[1]))
                        else:
                            form.append(0) # placeholder value for direction used for ManualPlayer
                    else:
                        form.append(0)
                if formatted:
                    return form
                else:
                    return out
                    
            else:
                # Scout handling                
                # order [Down, Up, Right, Left]
                directions = [(1,0),(-1,0),(0,1),(0,-1)]
                out = []
                for d in directions:
                    val = self.scoutHandle(board,d[0],d[1],formatted)
                    if formatted:
                        out.append(val)
                    elif val != None:
                        out.append(val)
                return out


        # Returns the valid moves for a scout
        def scoutHandle(self, board, xMove, yMove, formatted=False):
            team = board.board[self.X][self.Y].team

            x = self.X
            y = self.Y

            while True:
                if self.inBoard(x+xMove) and self.inBoard(y+yMove):
                    if board.board[x+xMove][y+yMove] == 0:
                        x+=xMove
                        y+=yMove
                    else:
                        if board.board[x+xMove][y+yMove] != LAKE and board.board[x+xMove][y+yMove].team != team:
                            x+=xMove
                            y+=yMove
                        break
                else:
                    # out of bounds
                    break
            
            if not (x == self.X and y == self.Y):
                return (self.X, self.Y, x, y)
 
            elif formatted:
                # used for formatting for manual player
                return 0 
