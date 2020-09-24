"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None

class ActionError(Exception):
    # Raised when action invalid
    pass

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # Initialize count numbers
    xCount = 0
    oCount = 0

    # Count up number of symbols on board
    for i in range(3):
        for j in range(3):
            if board[i][j] == X:
                xCount += 1
            elif board[i][j] == O:
                oCount += 1

    # If no symbols have been placed, default to X
    if xCount == 0 and oCount == 0:
        return "X"
    elif xCount > oCount:
        return "O"
    elif xCount == oCount:
        return "X"


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    
    # Initialize empty set
    actions = set()

    # Wherever an empty tile exists, create a tuple of coordinates and add it to set
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                possibleAction = (i, j)
                actions.add(possibleAction)
    
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    # If invalid action, raise an exception
    if board[action[0]][action[1]] != EMPTY:
        raise ActionError("Invalid Action")

    # Copy board, check current player's turn
    resultBoard = copy.deepcopy(board)
    currentPlayer = player(board)

    # Return resulting copy of board
    resultBoard[action[0]][action[1]] = currentPlayer
    return resultBoard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # Diagonal checks
    if board[0][0] == board[1][1] and board[1][1] == board [2][2]:
        return board[1][1]
    elif board[2][0] == board[1][1] and board[1][1] == board [0][2]:
        return board[1][1]
    else:
        # Vertical checks
        for j in range(3):
            currentSymbol = board[0][j]
            if (currentSymbol != EMPTY and currentSymbol == board[1][j]
                and currentSymbol == board[2][j]):
                    return currentSymbol
        
        # Horizontal checks
        for i in range(3):
            currentSymbol = board[i][0]
            if (currentSymbol != EMPTY and currentSymbol == board[i][1]
                and currentSymbol == board[i][2]):
                    return currentSymbol

        # If no winner found, return None
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    # If no winner yet, iterate through board to check if its full
    if winner(board) == None:
        for i in range(3):
            for j in range(3):
                if board[i][j] == EMPTY:
                    return False
        return True
    else:
        return True
    


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # Call winner function, then return result based on that
    Winner = winner(board)
    if Winner == "X":
        return 1
    elif Winner == "O":
        return -1
    else:
        return 0


def max_state(board):
    if terminal(board):
            return utility(board)
    v = -math.inf
    actionSet = actions(board)
    for action in actionSet:
        v = max(v, min_state(result(board, action)))
    return v

def min_state(board):
    if terminal(board):
            return utility(board)
    v = math.inf
    actionSet = actions(board)
    for action in actionSet:
        v = min(v, max_state(result(board, action)))
    return v

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    # Determine optimal value to fight for
    currentPlayer = player(board)

    # If terminal state, return none
    if terminal(board):
        return None

    if currentPlayer == "X":
        v = -math.inf
        for action in actions(board):
            k = min_state(result(board, action))
            if k > v:
                v = k
                best_move = action
    else:
        v = math.inf
        for action in actions(board):
            k = max_state(result(board, action))
            if k < v:
                v = k
                best_move = action
    return best_move
