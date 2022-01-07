""" For the heuristic, it combines two factors:
   (1) the utility
   (2) the number of pieces on the left and right sides (which cannot be captured)
   """
from __future__ import nested_scopes
from checkers_game import *

cache = {} #you can use this to implement state caching!

# Method to compute utility value of terminal state
def compute_utility(state, color):
    r = 0
    b = 0
    for row in state.board:
        for item in row:
            if item == 'r':
                r += 1
            elif item == 'R':
                r += 2
            elif item == 'b':
                b += 1
            elif item == 'B':
                b += 2
    if color == 'r':
        return r - b
    return b - r



# Better heuristic value of board
def compute_heuristic(state, color):
    value = compute_utility(state, color)
    for row in state.board:
        if row[0] == color:
            value += 1
        if row[len(row)-1] == color:
            value += 1
        if row[0] == OppDic1[color]:
            value -= 1
        if row[len(row)-1] == OppDic1[color]:
            value -= 1
    s1 = successors(state, color)
    s2 = successors(state, OppDic1[color])
    d_moves = len(s1) - len(s2)
    return value + d_moves

############ MINIMAX ###############################
def minimax_min_node(state, color, limit, caching=0):
    if caching != 0 and state in cache:
        return cache[state], state
    if game_over(state) or limit == 0:
        return -1 * compute_utility(state, color), None
    suc_states = successors(state, color)
    return_value = float('inf')
    for board in suc_states:
        value, move = minimax_max_node(board, OppDic1[color], limit-1)
        if value < return_value:
            return_value = value
            return_state = board
    if caching != 0:
        cache[return_state] = return_value
    return return_value, return_state


def minimax_max_node(state, color, limit, caching=0):
    if caching != 0 and state in cache:
        return cache[state], state
    if game_over(state) or limit == 0:
        return compute_utility(state, color), None
    suc_states = successors(state, color)
    return_value = -1 * float('inf')
    for board in suc_states:
        value, move = minimax_min_node(board, OppDic1[color], limit-1)
        if value > return_value:
            return_value = value
            return_state = board
    if caching != 0:
        cache[return_state] = return_value
    return return_value, return_state

def game_over(state):
    b = False
    r = False
    board = state.board
    for row in board:
        if 'b' in row or 'B' in row:
            b = True
            break
    for row in board:
        if 'r' in row or 'R' in row:
            r = True
    if b and r:
        return False
    return True


def select_move_minimax(state, color, limit, caching=0):
    """
        Given a state (of type Board) and a player color, decide on a move.
        The return value is a list of tuples [(i1,j1), (i2,j2)], where
        i1, j1 is the starting position of the piece to move
        and i2, j2 its destination.  Note that moves involving jumps will contain
        additional tuples.

        Note that other parameters are accepted by this function:
        If limit is a positive integer, your code should enforce a depth limit that is equal to the value of the parameter.
        Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic
        value (see compute_utility)
        If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
        If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    """
    max, move = minimax_max_node(state, color, limit, caching)
    return move.move


############ ALPHA-BETA PRUNING #####################
def alphabeta_min_node(state, color, alpha, beta, limit, caching=0, ordering=0):
    if caching != 0 and state in cache:
        return cache[state], state
    if game_over(state) or limit == 0:
        return -1 * compute_utility(state, color), None
    suc_states = successors(state, color)
    if ordering != 0:
        suc_states.sort(key=lambda state: compute_utility(state, color))
    return_value = float('inf')
    for board in suc_states:
        value, move = alphabeta_max_node(board, OppDic1[color], alpha, beta, limit - 1)
        if value < return_value:
            return_value = value
            return_state = board
        if return_value < alpha:
            break
        if beta > return_value:
            beta = return_value
    if caching != 0:
        cache[return_state] = return_value
    return return_value, return_state


def alphabeta_max_node(state, color, alpha, beta, limit, caching=0, ordering=0):
    if caching != 0 and state in cache:
        return cache[state], state
    if game_over(state) or limit == 0:
        return compute_utility(state, color), None
    suc_states = successors(state, color)
    if ordering != 0:
        suc_states.sort(key=lambda state: compute_utility(state, color))
    return_value = -1 * float('inf')
    for board in suc_states:
        value, move = alphabeta_min_node(board, OppDic1[color], alpha, beta, limit-1)
        if value > return_value:
            return_value = value
            return_state = board
        if return_value > beta:
            break
        if alpha < return_value:
            alpha = return_value
    if caching != 0:
        cache[return_state] = return_value
    return return_value, return_state

def select_move_alphabeta(state, color, limit, caching=0, ordering=0):
    """
    Given a state (of type Board) and a player color, decide on a move.
    The return value is a list of tuples [(i1,j1), (i2,j2)], where
    i1, j1 is the starting position of the piece to move
    and i2, j2 its destination.  Note that moves involving jumps will contain
    additional tuples.

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enforce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations.
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations.
    """
    max, move = alphabeta_max_node(state, color, -1*float('inf'), float('inf'), limit, caching, ordering)
    return move.move


# ======================== Class GameEngine =======================================
class GameEngine:
    def __init__(self, str_name):
        self.str = str_name

    def __str__(self):
        return self.str

    # The return value should be a move that is denoted by a list
    def nextMove(self, state, alphabeta, limit, caching, ordering):
        global PLAYER
        PLAYER = self.str
        if alphabeta:
            result = select_move_alphabeta(Board(state), PLAYER, limit, caching, ordering)
        else:
            result = select_move_minimax(Board(state), PLAYER, limit, caching)

        return result