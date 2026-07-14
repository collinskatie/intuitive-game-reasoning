import numpy as np
import random
import time
from models.utils import *

########################################################################


def rotate_board_90_clockwise(board):
    """
    Rotates a board 90 degrees clockwise.
    For example,
    [['X' 'O' '_']
    ['O' 'X' '_']
    ['_' '_' '_']
    ['_' '_' 'X']]
    becomes
    [['_' '_' 'O' 'X']
    ['_' '_' 'X' 'O']
    ['X' '_' '_' '_']]
    """
    transposed = [list(row) for row in zip(*board)]

    # Reverse each row
    rotated = [row[::-1] for row in transposed]

    return rotated


def rotate_pos(board, pos):
    # Return the new position after rotating the board 90 degrees clockwise.
    # For example, (0, 1) becomes (1, 3)

    new_row = pos[1]
    new_col = len(board) - 1 - pos[0]
    return (new_row, new_col)


########################################################################


def compute_distance_from_center(board, pos):
    # Returns the distance of a position from the center of the board.
    # "Normalized" by the maximum possible distance.

    center = ((len(board) - 1) / 2, (len(board[0]) - 1) / 2)
    dis = np.sqrt((pos[0] - center[0]) ** 2 + (pos[1] - center[1]) ** 2)
    return dis / np.sqrt(center[0] ** 2 + center[1] ** 2)


def check_connect(board, player, pos, n, constraints, win_num):

    r = 1
    r_live = 0
    c = 1
    c_live = 0
    d1 = 1  # topleft to bottomright
    d1_live = 0
    d2 = 1  # bottomleft to topright
    d2_live = 0

    if constraints[player]["hv"]:
        # check rows
        for i in range(pos[1] - 1, -1, -1):
            if board[pos[0]][i] == player and r_live == 0:
                r += 1
            else:
                if board[pos[0]][i] == "_" or board[pos[0]][i] == player:
                    r_live += 1
                else:
                    break
        curr_r_live = r_live
        for i in range(pos[1] + 1, len(board[0])):
            if board[pos[0]][i] == player and curr_r_live == r_live:
                r += 1
            else:
                if board[pos[0]][i] == "_" or board[pos[0]][i] == player:
                    r_live += 1
                else:
                    break

        # check cols
        for i in range(pos[0] - 1, -1, -1):
            if board[i][pos[1]] == player and c_live == 0:
                c += 1
            else:
                if board[i][pos[1]] == "_" or board[i][pos[1]] == player:
                    c_live += 1
                else:
                    break
        curr_c_live = c_live
        for i in range(pos[0] + 1, len(board)):
            if board[i][pos[1]] == player and curr_c_live == c_live:
                c += 1
            else:
                if board[i][pos[1]] == "_" or board[i][pos[1]] == player:
                    c_live += 1
                else:
                    break

    if constraints[player]["diag"]:
        # check diagonals
        ind = min(pos[0], pos[1])
        for i in range(1, ind + 1):
            if board[pos[0] - i][pos[1] - i] == player and d1_live == 0:
                d1 += 1
            else:
                if (
                    board[pos[0] - i][pos[1] - i] == "_"
                    or board[pos[0] - i][pos[1] - i] == player
                ):
                    d1_live += 1
                else:
                    break
        ind = min(len(board) - pos[0] - 1, len(board[0]) - pos[1] - 1)
        curr_d1_live = d1_live
        for i in range(1, ind + 1):
            if board[pos[0] + i][pos[1] + i] == player and curr_d1_live == d1_live:
                d1 += 1
            else:
                if (
                    board[pos[0] + i][pos[1] + i] == "_"
                    or board[pos[0] + i][pos[1] + i] == player
                ):
                    d1_live += 1
                else:
                    break

        rot_board = rotate_board_90_clockwise(board)
        rot_pos = rotate_pos(board, pos)
        ind = min(rot_pos[0], rot_pos[1])
        for i in range(1, ind + 1):
            if rot_board[rot_pos[0] - i][rot_pos[1] - i] == player and d2_live == 0:
                d2 += 1
            else:
                if (
                    rot_board[rot_pos[0] - i][rot_pos[1] - i] == "_"
                    or rot_board[rot_pos[0] - i][rot_pos[1] - i] == player
                ):
                    d2_live += 1
                else:
                    break
        ind = min(len(rot_board) - rot_pos[0] - 1, len(rot_board[0]) - rot_pos[1] - 1)
        curr_d2_live = d2_live
        for i in range(1, ind + 1):
            if (
                rot_board[rot_pos[0] + i][rot_pos[1] + i] == player
                and curr_d2_live == d2_live
            ):
                d2 += 1
            else:
                if (
                    rot_board[rot_pos[0] + i][rot_pos[1] + i] == "_"
                    or rot_board[rot_pos[0] + i][rot_pos[1] + i] == player
                ):
                    d2_live += 1
                else:
                    break

    params = [[r, r_live], [c, c_live], [d1, d1_live], [d2, d2_live]]
    for i in range(len(params)):
        if params[i][0] + params[i][1] < win_num:
            params[i][0] = 1
    live_n = [params[i][0] for i in range(len(params))]

    return max(live_n) == n


def max_connect(board, player, pos, constraints, win_num):

    r = 1
    r_live = 0
    c = 1
    c_live = 0
    d1 = 1  # topleft to bottomright
    d1_live = 0
    d2 = 1  # bottomleft to topright
    d2_live = 0

    if constraints[player]["hv"]:
        # check rows
        for i in range(pos[1] - 1, -1, -1):
            if board[pos[0]][i] == player and r_live == 0:
                r += 1
            else:
                if board[pos[0]][i] == "_" or board[pos[0]][i] == player:
                    r_live += 1
                else:
                    break
        curr_r_live = r_live
        for i in range(pos[1] + 1, len(board[0])):
            if board[pos[0]][i] == player and curr_r_live == r_live:
                r += 1
            else:
                if board[pos[0]][i] == "_" or board[pos[0]][i] == player:
                    r_live += 1
                else:
                    break

        # check cols
        for i in range(pos[0] - 1, -1, -1):
            if board[i][pos[1]] == player and c_live == 0:
                c += 1
            else:
                if board[i][pos[1]] == "_" or board[i][pos[1]] == player:
                    c_live += 1
                else:
                    break
        curr_c_live = c_live
        for i in range(pos[0] + 1, len(board)):
            if board[i][pos[1]] == player and curr_c_live == c_live:
                c += 1
            else:
                if board[i][pos[1]] == "_" or board[i][pos[1]] == player:
                    c_live += 1
                else:
                    break

    if constraints[player]["diag"]:
        # check diagonals
        ind = min(pos[0], pos[1])
        for i in range(1, ind + 1):
            if board[pos[0] - i][pos[1] - i] == player and d1_live == 0:
                d1 += 1
            else:
                if (
                    board[pos[0] - i][pos[1] - i] == "_"
                    or board[pos[0] - i][pos[1] - i] == player
                ):
                    d1_live += 1
                else:
                    break
        ind = min(len(board) - pos[0] - 1, len(board[0]) - pos[1] - 1)
        curr_d1_live = d1_live
        for i in range(1, ind + 1):
            if board[pos[0] + i][pos[1] + i] == player and curr_d1_live == d1_live:
                d1 += 1
            else:
                if (
                    board[pos[0] + i][pos[1] + i] == "_"
                    or board[pos[0] + i][pos[1] + i] == player
                ):
                    d1_live += 1
                else:
                    break

        rot_board = rotate_board_90_clockwise(board)
        rot_pos = rotate_pos(board, pos)
        ind = min(rot_pos[0], rot_pos[1])
        for i in range(1, ind + 1):
            if rot_board[rot_pos[0] - i][rot_pos[1] - i] == player and d2_live == 0:
                d2 += 1
            else:
                if (
                    rot_board[rot_pos[0] - i][rot_pos[1] - i] == "_"
                    or rot_board[rot_pos[0] - i][rot_pos[1] - i] == player
                ):
                    d2_live += 1
                else:
                    break
        ind = min(len(rot_board) - rot_pos[0] - 1, len(rot_board[0]) - rot_pos[1] - 1)
        curr_d2_live = d2_live
        for i in range(1, ind + 1):
            if (
                rot_board[rot_pos[0] + i][rot_pos[1] + i] == player
                and curr_d2_live == d2_live
            ):
                d2 += 1
            else:
                if (
                    rot_board[rot_pos[0] + i][rot_pos[1] + i] == "_"
                    or rot_board[rot_pos[0] + i][rot_pos[1] + i] == player
                ):
                    d2_live += 1
                else:
                    break

    params = [[r, r_live], [c, c_live], [d1, d1_live], [d2, d2_live]]
    for i in range(len(params)):
        if params[i][0] + params[i][1] < win_num:
            params[i][0] = 1
    live_n = [params[i][0] for i in range(len(params))]
    best_n = max(live_n)
    best_n = best_n if best_n >= 2 else float("-inf")
    best_n = best_n if best_n < win_num else float("-inf")  # min(best_n, win_num-1)
    return best_n


def connection_score(board, player, pos, win_nums, constraints, win_encourage):
    score = 0
    place_piece(board, pos, player)
    for i in range(2, win_nums[player]):
        if check_connect(board, player, pos, i, constraints, win_nums[player]):
            score = 2**i
    if connect_n(board, player, win_nums[player], constraints):
        score = 2 ** (win_nums[player] + win_encourage)
    remove_piece(board, pos)
    return score


def block_score(board, player, pos, win_nums, constraints, block_discourage):
    score = 0
    place_piece(board, pos, switch_player(player))
    for i in range(2, win_nums[switch_player(player)]):
        if check_connect(
            board,
            switch_player(player),
            pos,
            i,
            constraints,
            win_nums[switch_player(player)],
        ):
            score = 2 ** (i - block_discourage)
    if connect_n(
        board, switch_player(player), win_nums[switch_player(player)], constraints
    ):
        score = 2 ** win_nums[switch_player(player)]
    remove_piece(board, pos)
    return score


def calculate_move_distribution(
    board, player, win_nums, constraints, for_win, win_encourage=1, block_discourage=1
):
    dist = {}
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == "_":
                dist[(i, j)] = 0
    for pos in dist.keys():
        dis = compute_distance_from_center(board, pos)
        dist[pos] += 2 ** (1 - dis)
    for pos in dist.keys():
        connect = connection_score(
            board, player, pos, win_nums, constraints, win_encourage
        )
        dist[pos] += connect
    for pos in dist.keys():
        block = block_score(board, player, pos, win_nums, constraints, block_discourage)
        dist[pos] += block

    if for_win == 0:
        max_score = max(dist.values())
        for pos in dist.keys():
            dist[pos] = max_score * (np.arctan(-dist[pos]) + np.pi / 2)
    return dist


########################################################################


# adding in board-based metric
def calculate_state_value(
    board, root_player_type, win_nums, constraints, for_win, normalize
):

    # sum the scores for each player
    player_scores = {"X": 0, "O": 0}

    # sweep over all pieces on the board
    for row_idx in range(len(board)):
        for col_idx in range(len(board[0])):
            player = board[row_idx][col_idx]
            pos = [row_idx, col_idx]
            if player == "_":
                continue

            # three components
            # (1) center bias
            # (2) self-connectedness
            # (3) blocking

            piece_score = 0

            # (1) center bias
            center_dis = compute_distance_from_center(board, pos)
            piece_score += 2 ** (1 - center_dis)
            # (2) self-connectedness [relative to player]
            for i in range(2, win_nums[player]):
                if check_connect(board, player, pos, i, constraints, win_nums[player]):
                    piece_score = 2**i
            if connect_n(board, player, win_nums[player], constraints):
                piece_score = 2 ** (win_nums[player] + 1)
            # (3) blocking
            place_piece(board, pos, switch_player(player))
            for i in range(2, win_nums[switch_player(player)]):
                if check_connect(
                    board,
                    switch_player(player),
                    pos,
                    i,
                    constraints,
                    win_nums[switch_player(player)],
                ):
                    piece_score = 2 ** (i - 0.5)
            if connect_n(
                board,
                switch_player(player),
                win_nums[switch_player(player)],
                constraints,
            ):
                piece_score = 2 ** win_nums[switch_player(player)]
            place_piece(board, pos, player)
            player_scores[player] += piece_score

    state_value = 0
    for player, player_cumulative_pos_score in player_scores.items():
        if player == root_player_type:
            state_value += player_cumulative_pos_score
        else:
            if not normalize:
                state_value -= player_cumulative_pos_score
    if not for_win:
        if normalize:
            state_value = 1 / (0.1 + state_value)
        else:
            state_value = -state_value
    return state_value


def update_val(
    board,
    pos,
    parent_val,
    player_type,
    root_player_type,
    win_nums,
    constraints,
    for_win,
    normalize,
    center_dists,
):

    # sum the scores for each player

    # sweep over all pieces on the board

    # three components
    # (1) center bias
    # (2) self-connectedness
    # (3) blocking

    piece_score = 0

    # (1) center bias
    center_dis = center_dists[pos]
    piece_score += 2 ** (1 - center_dis)

    # (2) self-connectedness [relative to player_type]
    connection_score = max_connect(
        board, player_type, pos, constraints, win_nums[player_type]
    )
    piece_score += 2**connection_score
    if connect_n(board, player_type, win_nums[player_type], constraints):
        piece_score += 2 ** (win_nums[player_type] + 1)

    # (3) blocking
    opp = switch_player(player_type)
    block_score = max_connect(board, opp, pos, constraints, win_nums[opp])
    piece_score += 2 ** (block_score - 0.5)
    if connect_n(board, opp, win_nums[opp], constraints):
        piece_score += 2 ** win_nums[opp]

    if normalize:
        if player_type != root_player_type:
            piece_score = 0
        else:
            if not for_win:
                piece_score = 1 / piece_score
    else:
        if player_type != root_player_type:
            piece_score = -piece_score
        if not for_win:
            piece_score = -piece_score

    player_score = parent_val + piece_score

    return player_score


########################################################################


def act(
    board,
    player,
    win_nums,
    for_win,
    constraints,
    plays,
    player_sequence,
    center_weight=1,
    connect_weight=1,
    block_weight=1,
    win_encourage=1,
    block_discourage=0.5,
    normalize=False,
    softmax_temp=1,
):
    start_time = time.time()

    if win_score(board, player, win_nums, for_win, constraints) != 0 or is_draw(board):
        return None
    else:
        dist = {}
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == "_":
                    dist[(i, j)] = 0
        for pos in dist.keys():
            dis = compute_distance_from_center(board, pos)
            dist[pos] += center_weight * (2 ** (1 - dis))

        for pos in dist.keys():
            connect = connection_score(
                board, player, pos, win_nums, constraints, win_encourage
            )
            dist[pos] += connect_weight * connect

        for pos in dist.keys():
            block = block_score(
                board, player, pos, win_nums, constraints, block_discourage
            )
            dist[pos] += block_weight * block

        if for_win == 0:
            max_score = max(dist.values())
            for pos in dist.keys():
                dist[pos] = max_score * (np.arctan(-dist[pos]) + np.pi / 2)

        if normalize:
            normalization_constant = sum(dist.values())
            dist = {k: v / normalization_constant for k, v in dist.items()}
        d = softmax_dist(dist, softmax_temp)
        move = random.choices(list(d.keys()), list(d.values()))[0]

        execution_time = time.time() - start_time
        metadata = {
            "move": move,
            "dist": dist,
            "pv_depth": None,
            "ave_depth": None,
            "logprob": np.log(d[move]),
            "num_nodes": len(d.keys()),
            "time_elapsed": execution_time,
        }

        return metadata
