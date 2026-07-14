import random
from models.utils import *

def uniform_dist(board):
    # Returns a uniform distribution over valid moves on the board.
    # Repressented as a dictionary.
    dist = {}
    count = 0
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == '_':
                dist[(i, j)] = 1
                count += 1
    for key in dist:
        dist[key] /= count
    return dist

def act(board, player, win_nums, for_win, constraints, plays, player_sequence):
    if win_score(board, player, win_nums, for_win, constraints) != 0 or is_draw(board):
        return None
    else:
        dist = uniform_dist(board)
        # move = random.choices(list(prob.keys()), weights=prob.values(), k=1)[0]
        move = random.choices(list(dist.keys()), list(dist.values()))[0]
        return {"move": move, "dist": dist, "pv_depth": None, "ave_depth": None, "logprob": dist[move]}
