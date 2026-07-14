import copy
import random
import time

import numpy as np

import models.agents.heuristics as heuristics
import models.utils as utils


class Node:
    def __init__(
        self,
        state,
        turn_idx=0,
        player_turn_seq=None,
        parent=None,
        value=0,
        action=None,
        val_at_expansion=0,
    ):
        self.state = state
        self.parent = parent
        self.value = value
        self.action = action
        # it's possible one player can play more than once
        # maintain a list of who's turn it is
        self.player_turn_seq = player_turn_seq
        # maintain which turn number we're on
        self.turn_idx = turn_idx
        # extract which player is playing ("X" or "O")
        self.player_type = self.player_turn_seq[self.turn_idx]

        # initialize with no children
        self.children = []
        self.val_at_expansion = val_at_expansion

        # Recursively track the number of nodes in the tree
        self.num_nodes_in_subtree = 1  # Start with self

    def __str__(self):
        return f"\nPrinting node ....\n\tcurrent player: {self.player_type} (turn: {self.turn_idx})\n\tvalue: {self.value}\n\taction: {self.action}\n\tstate: {self.state}\n\tnum children: {len(self.children)}\n"


def display_children(children):
    return [f"{child.value:.2f}" for child in children]


def make_move(
    board,
    player_turn_seq,
    turn_idx,
    win_nums,
    constraints,
    for_win,
    steps,
    prune_threshold,
    softmax_temp,
    outcome_weighting,
    normalize,
    normalize2,
    normalize3,
    epsilon,
):

    # Instantiate the root node
    root = Node(state=board, turn_idx=turn_idx, player_turn_seq=player_turn_seq)
    root_player_type = root.player_type

    # Precompute the distance from the center
    center_dists = {}
    center = ((len(board) - 1) / 2, (len(board[0]) - 1) / 2)
    for y in range(len(board)):
        for x in range(len(board[0])):
            pos = (y, x)
            dist = np.sqrt((pos[0] - center[0]) ** 2 + (pos[1] - center[1]) ** 2)
            dist /= np.sqrt(center[0] ** 2 + center[1] ** 2)
            center_dists[pos] = dist

    # For each step...
    actual_num_steps_run = 0
    for step in range(steps):
        # Select a node to expand using best-first search.
        node = select_node(root, root_player_type, epsilon)

        expand_node(
            node,
            root_player_type,
            win_nums,
            constraints,
            for_win,
            prune_threshold=prune_threshold,
            outcome_weighting=outcome_weighting,
            normalize=normalize,
            center_dists=center_dists,
        )

        backprop(node, root_player_type, outcome_weighting)

        actual_num_steps_run += 1

    if normalize:
        normalization_const = sum(map(lambda x: x.value, root.children)) + 1e-3
        action_dist = {
            node.action: node.value / normalization_const for node in root.children
        }
    elif normalize2:
        normalization_constant = abs(sum(map(lambda x: x.value, root.children))) + 1e-3
        action_dist = {
            node.action: node.value / normalization_constant for node in root.children
        }
    elif normalize3:
        normalization_constant = sum(map(lambda x: abs(x.value), root.children)) + 1e-3
        action_dist = {
            node.action: node.value * abs(node.value) / normalization_constant
            for node in root.children
        }
    else:
        action_dist = {node.action: node.value for node in root.children}

    dist = utils.softmax_dist(action_dist, T=softmax_temp)
    action = random.choices(list(dist.keys()), list(dist.values()))[0]

    pv_depth = utils.get_pv_depth(root)
    ave_depth = utils.get_ave_depth(root)
    num_nodes = root.num_nodes_in_subtree

    return action, action_dist, pv_depth, ave_depth, actual_num_steps_run, num_nodes


def select_node(node, root_player_type, epsilon):
    while len(node.children) != 0:
        if node.player_type == root_player_type:
            node, _ = utils.epsilon_greedy_max(
                node.children, key=lambda x: x.value, epsilon=epsilon
            )
        else:
            node, _ = utils.epsilon_greedy_min(
                node.children, key=lambda x: x.value, epsilon=epsilon
            )
    return node


def expand_node(
    node,
    root_player_type,
    win_nums,
    constraints,
    for_win,
    prune_threshold,
    outcome_weighting,
    normalize,
    center_dists,
):
    """
    Expands a node (selected by best-first search) by instantiating and evaluating each of its children

    Args:
        node: Node -- the node to expand
        root_player_type: str -- the player type of the root node
        win_nums: dict[str, int] -- the number of pieces in a row needed to win for each player
        constraints: dict[str, dict[str, int]] -- constraints for each player on the directions
            they can use to win. Each player has 1 or 0 for "hv" and "diag"
        for_win: int -- 1 if the game is for a win (standard), 0 if it's for a loss (misere)
        outcome_weighting: float -- the value (positive or negative) to assign to wins / losses
        center_dists: dict[(int, int), float] -- the normalized distance of each position from the center of the board
    """

    state = node.state  # board
    player_turn_seq = node.player_turn_seq

    # current node is the player who has just made a move ("current player")
    # that player is now checking if they have won
    # if not, they assess children from that node
    current_player_type = node.player_type
    current_player_turn = node.turn_idx

    # If the game is over, then the search terminates immediately
    # Can be 'current_player_type' or 'root_player_type' since this just checks termination
    if utils.win_score(
        state, root_player_type, win_nums, for_win, constraints
    ) != 0 or utils.is_draw(state):
        # can't expand any further -- game is over
        return 0

    # otherwise, the game is not yet determined
    # get all legal moves from that state
    avail_moves = utils.get_available_moves(state)

    next_turn_idx = current_player_turn + 1  # this is now the turn of the child
    for move in avail_moves:
        new_state = copy.deepcopy(state)

        utils.place_piece(new_state, move, current_player_type)

        # check whether the game is determined from this new state
        # did the move the current player made lead them to win (or lose, or draw)
        win_score = utils.win_score(
            new_state,
            root_player_type,
            win_nums,
            for_win,
            constraints,
            outcome_weighting=outcome_weighting,
        )

        draw = utils.is_draw(new_state)
        determined = win_score != 0 or draw

        if determined:
            value = (win_score + outcome_weighting) / 2 if normalize else win_score
        else:
            value = heuristics.update_val(
                new_state,
                move,
                node.val_at_expansion,
                node.player_type,
                root_player_type,
                win_nums,
                constraints,
                for_win,
                normalize,
                center_dists,
            )

        child = Node(
            new_state,
            turn_idx=next_turn_idx,
            player_turn_seq=player_turn_seq,
            value=value,
            action=move,
            parent=node,
            val_at_expansion=value,
        )
        node.children.append(child)


def backprop(node, root_player_type, outcome_weighting):

    current_player_type = node.player_type

    min_max_func = (
        utils.max_child if current_player_type == root_player_type else utils.min_child
    )

    children = node.children
    if len(children) != 0:
        node.value = min_max_func(children, key=lambda x: x.value)

        # Update num_nodes_in_subtree based on children
        node.num_nodes_in_subtree = 1 + sum(
            child.num_nodes_in_subtree for child in children
        )

    # recursively backpropogate to parent(s)
    if node.parent:
        backprop(node.parent, root_player_type, outcome_weighting)


def act(
    board,
    player,
    win_nums,
    for_win,
    constraints,
    plays,
    player_sequence,
    steps=636,
    prune_threshold=float("inf"),
    softmax_temp=1,
    outcome_weighting=1000,
    normalize=False,
    normalize2=False,
    normalize3=False,
    epsilon=0.0001,
):
    """
    Performs best-first search on the given board for the specified player

    Args:
        board: list[list[str]] -- the current state of the board with each position as "X", "O", or "_"
        player: str -- the player to act as ("X" or "O")
        win_nums: dict[str, int] -- the number of pieces in a row needed to win for each player
        for_win: int -- 1 if the game is for a win (standard), 0 if it's for a loss (misere)
        constraints: dict[str, dict[str, int]] -- constraints for each player on the directions
            they can use to win. Each player has 1 or 0 for "hv" and "diag"
        plays: int -- the number of plays that have been made so far
        player_sequence: list[str] -- the sequence of players in the game
        steps: int -- the number of best-first rollouts to perform during the search
        softmax_temp: float -- during exploration, the temperature to apply to the children
            values to determine the probability of selecting each child
        outcome_weighting: float -- the value (positive or negative) to assign to wins / losses
        softmax_explore: bool -- whether to use softmax exploration or not
    """
    start_time = time.time()

    # If the game is over, then the search terminates immediately
    if utils.win_score(
        board, player, win_nums, for_win, constraints
    ) != 0 or utils.is_draw(board):
        return None

    (
        action,
        action_distribution,
        pv_depth,
        ave_depth,
        actual_num_steps_run,
        num_nodes,
    ) = make_move(
        board,
        player_turn_seq=player_sequence,
        turn_idx=plays,
        win_nums=win_nums,
        for_win=for_win,
        steps=steps,
        constraints=constraints,
        prune_threshold=prune_threshold,
        softmax_temp=softmax_temp,
        outcome_weighting=outcome_weighting,
        normalize=normalize,
        normalize2=normalize2,
        normalize3=normalize3,
        epsilon=epsilon,
    )

    # reformat action dist to match others
    # (pos_x, pos_y): value
    # note: convert from numpy -> int and float (this could be cleaner)
    # dist = {(int(entry["action"][0]), int(entry["action"][1])): float(entry["norm_value"]) for entry in action_distribution}

    execution_time = time.time() - start_time
    # execution_time = None
    metadata = {
        "move": action,
        "dist": action_distribution,
        "pv_depth": pv_depth,
        "ave_depth": ave_depth,
        "num_steps": actual_num_steps_run,
        "num_nodes": num_nodes,
        "time_elapsed": execution_time,
        "logprob": 0,
    }
    return metadata
