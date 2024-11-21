# Stratego_AI
NOTE: In-progress

# Dependencies
For Stratego Game Functionality
- Numpy  

For Machine Learning Files  
- Tensorflow
- Keras
- Collections
- SciPy

# How to Run
Run the game.py file and select what boards you want to compare

# Extra Information
Piece Format on Board  
-Rank,Count_Team ; (ex: 8,3_1 -> Rank 8(miner), the 3rd miner, on team P1)  

For Manual Board, move format:  
-row col direction(up(u), right(r), left(l), down(d)) ; (ex: 6 0 u -> moves piece at row 6, col 0 Up)

For Testing:  
-Comment out the p1, p2, hide = userInput() and then assign p1 and p2 to players

## Description of chanceBoard/probabilityBoard  
Short background information: Stratego is a partially observable game state, meaning that you don't know your opponents pieces. In our program we store a board as a 2d matrix of x,y's and at each index there is a Piece placed.

If for instance PlayerAB is Player 1, it won't know the Player 2 pieces until they are discovered through attack. So we created a chanceBoard, which is represented as a 3d matrix so chanceBoard[x][y] would produce a list of the probabilities(length 12 for each piece) for each piece that could be placed at this x,y. We then select a piece to be placed on our probBoard using each of these piece's probabilities of occuring. Each time pieces are moved the probabilites in the chanceBoard will be updated to account for this movement, for example if a piece moves it can no longer be a bomb or flag so its probabilities are updated as such. Also if an attack occurs, then the value of both pieces involved in the attack are revealed so the probability board updates the probability for those pieces at their respective x,y so that these locations are guaranteed to only be that piece since they have been revealed. For example, if the alpha-beta board moves a 9 into a bomb(12) at position 6,0, it will remember that position 6,0 is a bomb and will update the probability as such along with updating the board. It will then recreate the probBoard which is the same format at as the game board. 

### [update] Google Deepmind published a paper addressing the same problem (DeepNash) in 2022, reference this paper to learn more about writing an AI for Stratego.
https://deepmind.google/discover/blog/mastering-stratego-the-classic-game-of-imperfect-information/
