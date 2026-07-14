import copy
import numpy as np
from scipy.stats import entropy
import random

import pprint
players = ['X', 'O'] # Our convention is that Player 1 is 'X' and Player 2 is 'O'.
# win_num = {'X': 5, 'O': 5}
# for_win = 1
# constraints = {'X': {'hv': 1, 'diag': 1},
#                'O': {'hv': 1, 'diag': 1}}
two_pieces = {'X': 0, 'O': 0}

# Board indexing starts from top left.
def construct_board(size_x=5, size_y=5):
    return [['_'] * size_y for _ in range(size_x)]

def empty_board(board):
    return all(board[i][j] == '_' for i in range(len(board)) for j in range(len(board[0])))

def get_available_moves(board):
    valid_moves = []
    for i in range(len(board)):
        for j in range(len(board[0])):
            if is_valid_move(board, (i, j)):
                valid_moves.append((i,j))
    return valid_moves

def is_valid_move(board, move):
    return board[move[0]][move[1]] == '_'


def place_piece(board, pos, player):

    if pos != None:
        board[pos[0]][pos[1]] = player
    else:
        print("Game over (or invalid move)!")

def remove_piece(board, pos):

    if pos != None:
        board[pos[0]][pos[1]] = "_"
    else:
        print("Game over (or invalid move)!")


def place_piece_new(board, pos, player):
    # Place a new piece.
    # Returns the resulting board.

    if pos != None:
        new_board = copy.deepcopy(board)
        new_board[pos[0]][pos[1]] = player
        return new_board
    else:
        print("Game over (or invalid move)!")

def remove_piece_new(board, pos):
    # Place a new piece.
    # Retrurns the resulting board.

    if pos != None:
        new_board = copy.deepcopy(board)
        new_board[pos[0]][pos[1]] = "_"
        return new_board
    else:
        print("Game over (or invalid move)!")

def switch_player(player):
    # return players[(players.index(player) + 1) % num_players]
    return 'X' if player == 'O' else 'O'

def has_won(board, player, win_nums, for_win, constraints):
    if for_win: # N in a row wins
        return connect_n(board, player, win_nums[player], constraints)
    else: # N in a row loses
        # If the other player gets N in a row, you win.
        return connect_n(board, switch_player(player), win_nums[switch_player(player)], constraints)

def is_draw(board):
    full = True
    for row in board:
        if '_' in row:
            full = False
            break
    return full

def get_game_length(board): 
    # compute game length as the number of pieces made on the board
    # note: if we explore games where pieces can be removed, this needs to change
    piece_counts = 0
    for row in board:
        piece_counts += np.sum([1 for cell in row if cell != '_'])
    return piece_counts

def win_score(board, player, win_nums, for_win, constraints, outcome_weighting=1):
    if has_won(board, player, win_nums, for_win, constraints):
        return outcome_weighting * 1 # player won
    elif has_won(board, switch_player(player), win_nums, for_win, constraints):
        return outcome_weighting * -1 # player lost
    else:
        return 0 # game not over yet (or draw...)

def compute_emd(outcome_dist):
    ordered_keys = ['lose', 'draw', 'win']
    
    # Align keys based on the ordering
    p = {key: outcome_dist.get(key, 0) for key in ordered_keys}
    q = {'lose': 0.5, 'draw': 0, 'win': 0.5}
    
    # Compute cumulative distributions
    cdf_p = []
    cdf_q = []
    cumulative_p = 0
    cumulative_q = 0
    for key in ordered_keys:
        cumulative_p += p[key]
        cumulative_q += q[key]
        cdf_p.append(cumulative_p)
        cdf_q.append(cumulative_q)
    
    # Calculate EMD as the area between the two CDFs
    emd = sum(abs(cdf_p[i] - cdf_q[i]) for i in range(len(ordered_keys)))
    return emd

def compute_entropy(vals): 
    return entropy(vals)

def get_outcome_dist(game_scores): 
    score2outcome = {1: "win", -1: "lose", 0: "draw"}
    outcomes = {"win": 0, "lose": 0, "draw": 0} 
    for score in game_scores: 
        outcomes[score2outcome[score]] += 1
    num_games = len(game_scores)
    outcome_dist = {outcome: game_count/num_games for outcome, game_count in outcomes.items()}
    return outcome_dist

def compute_funness(outcome_dist, game_lengths=[], measure="entropy"): 
    if measure == "entropy": 
        return compute_entropy(list(outcome_dist.values())) 
    else:
        # todo: implement others, e.g., based on game length
        return 0
    
def print_board(board):
    for row in board:
        print(row)

def print_expected_values(board, moves_dict):
    copied_board = copy.deepcopy(board)
    for move in moves_dict.keys():
        copied_board [move[0]][move[1]] = moves_dict[move]
    for row in copied_board:
        print(row)

def rand_max(arr, key=None):
    if key is not None: 
        maxi = max(arr, key=key)
        choices = list(filter(lambda x: key(x) == key(maxi), arr))
        sel = random.choices(choices)[0]
    else: 
        maxi = max(arr)
        choices = list(filter(lambda x: x[1] == maxi, enumerate(arr)))
        sel = random.choices(choices)[0][0]
    return sel, np.log(len(choices))


def rand_min(arr, key=None):
    if key is not None: 
        maxi = min(arr, key=key)
        choices = list(filter(lambda x: key(x) == key(maxi), arr))
        sel = random.choices(choices)[0]
    else: 
        maxi = min(arr)
        choices = list(filter(lambda x: x[1] == maxi, enumerate(arr)))
        sel = random.choices(choices)[0][0]
    return sel, np.log(len(choices))

def sample_softmax(arr, key=None):
    dist = softmax_dist({idx: key(a) for idx, a in enumerate(arr)})
    action = random.choices(list(dist.keys()), list(dist.values()))[0]
    return arr[action], np.log(dist[action])

def epsilon_greedy_max(arr, epsilon, key=None):
    if random.random() < epsilon:
        return random.choice(arr), np.log(1 / len(arr))
    else:
        return rand_max(arr, key=key)
    
def epsilon_greedy_min(arr, epsilon, key=None):
    if random.random() < epsilon:
        return random.choice(arr), np.log(1 / len(arr))
    else:
        return rand_min(arr, key=key)

def sample_softmin(arr, key=None):
    dist = softmax_dist({idx: -key(a) for idx, a in enumerate(arr)})
    action = random.choices(list(dist.keys()), list(dist.values()))[0]
    return arr[action], np.log(dist[action])

def max_child(arr, key=None):
    if key is not None:
        maxi = key(max(arr, key=key))
    else:
        maxi = max(arr)
    return maxi

def min_child(arr, key=None):
    if key is not None:
        mini = key(min(arr, key=key))
    else:
        mini = min(arr)
    return mini

######################################################################
def calculate_player_sequence(board_size, two_pieces, players, buffer=10): 
    curr_player = players[0]
    player_sequence = []
    plays = 0
    if two_pieces[players[0]]:
        player_sequence += [players[0], players[0], players[1]]
        curr_player = players[0]
        plays += 3
    elif two_pieces[players[1]]:
        player_sequence += [players[0], players[1], players[1]]
        curr_player = players[0]
        plays += 3
    while plays < board_size + buffer:
        player_sequence += [curr_player]
        curr_player = players[1] if curr_player == players[0] else players[0]
        plays += 1
    return player_sequence
    


def normalize_dist(dist):
    # Normalize a distribution represented as a dictionary.
    d = dist.copy()
    total = sum(d.values())
    for key in d:
        d[key] /= total
    return d

def softmax_dist(dist, T=1):
    d = dist.copy()
    b = max(d.values())
    for key in d:
        d[key] = np.exp((d[key] - b) / T)
    total = sum(d.values())
    for key in d:
        d[key] /= total
    return d

def compute_utility(draw_resp, win_resp): 
    return (1 - (draw_resp + win_resp)) * (-1) + win_resp

def get_pwin(draw_resp, adv_resp): 
    return ((100 - draw_resp)/100) * (adv_resp/100) * 100

def get_n_win(win_cond):
    return int(win_cond.split(" pieces")[0].split(" ")[-1])

def compute_diagonal(board, i, j, direction, n):
    # left to right
    if direction == "lr":
        diag = [board[i + k][j + k] for k in range(n)]
    # right to left
    elif direction == "rl":
        diag = [board[i + k][j - k] for k in range(n)]
    else:
        raise ValueError("Invalid direction")
    return diag

def connect_n(board, player, n, constraints):

    if constraints[player]['hv']:
        # check rows
        for row in board:
            for i in range(len(row) - n + 1):
                if row[i:i+n].count(player) == n:
                    return True
        # check cols
        for col in range(len(board[0])):
            for i in range(len(board) - n + 1):
                if [row[col] for row in board[i:i+n]].count(player) == n:
                    return True
    
    if constraints[player]['diag']:
        # check diagonals
        diag_1, diag_2 = [], []  
        for i in range(len(board) - n + 1):
            for j in range(len(board[0]) - n + 1):
                diag_1.append(compute_diagonal(board, i, j, "lr", n))
        for i in range(0, len(board) - n + 1):
            for j in range(n - 1, len(board[0])):
                diag_2.append(compute_diagonal(board, i, j, "rl", n))
        for diag in diag_1 + diag_2:
            if diag.count(player) == n:
                return True
        
    return False

def node_to_table(node, fn):
    # get hash table keyed by board cell with metric on child
    d = {c.action: fn(c) for c in node.children}
    return d

######################################################################

def get_depth(node):
    if not node.children:
        return 0
    return 1+max(map(get_depth, node.children))

def get_pv_depth(node, root_player_type=None, debug=False):
    if debug:
        print(node)
    if root_player_type is None:
        root_player_type = node.player_type
    if not node.children:
        return 0
    selection_fn = max if root_player_type == node.player_type else min
    best = selection_fn(node.children, key=lambda x: x.value)
    return 1+get_pv_depth(best, root_player_type, debug)

def get_average_leaf_depth(root, current_depth=0):
    if not root.children:  # Leaf node
        return current_depth, 1
    
    total_depth = 0
    total_leaves = 0
    
    for child in root.children:
        depth, leaves = get_average_leaf_depth(child, current_depth + 1)
        total_depth += depth
        total_leaves += leaves
    
    return total_depth, total_leaves

def get_ave_depth(root):
    if not root:
        return 0
    total_depth, total_leaves = get_average_leaf_depth(root)
    return total_depth / total_leaves if total_leaves else 0

def get_num_nodes(node):
    # Dynamic programming solution with memoization
    # Use object id as key to avoid issues with node comparison
    memo = {}
    
    def count_nodes_dp(current_node):
        if current_node is None:
            return 0
        
        # Use id() to create unique identifier for each node object
        node_id = id(current_node)
        
        # Check if we've already computed this subtree
        if node_id in memo:
            return memo[node_id]
        
        # Base case: leaf node
        if not hasattr(current_node, 'children') or not current_node.children:
            memo[node_id] = 1
            return 1
        
        # Recursive case: sum of all children plus this node
        total = 1  # Count current node
        for child in current_node.children:
            total += count_nodes_dp(child)
        
        memo[node_id] = total
        return total
    
    return count_nodes_dp(node)

def prolific2standardboard(board):
    transformed = [["_" for _ in board[0]] for _ in board]
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 1:
                transformed[i][j] = "X"
            elif board[i][j] == 2:
                transformed[i][j] = "O"
    return transformed

def get_move_number(board):
    board = np.array(board)
    return board.size - np.count_nonzero(board == "_")