import numpy as np
import models.utils as utils
import copy
import models.agents.uni_random as uni_random

import math
import time


class Node:
    def __init__(
        self, state, turn_idx=0, player_turn_seq=None, parent=None, value=0, action=None
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

        # keep track of visits
        self.visits = 0

        # initialize with no children
        self.children = []

        # Recursively track the number of nodes in the tree
        self.num_nodes = 1  # Start with self

    def __str__(self):
        return f"\nPrinting node ....\n\tcurrent player: {self.player_type} (turn: {self.turn_idx})\n\taction: {self.action}\n\tstate: {self.state}\n\tnum children: {len(self.children)}\n"


def make_move(
    state,
    player_turn_seq,
    turn_idx=0,
    win_nums="",
    constraints="",
    for_win="",  # parameters defining game dynamics
    steps=10000,
):

    root = Node(state=state, turn_idx=turn_idx, player_turn_seq=player_turn_seq)
    root_player_type = root.player_type

    for step in range(steps):
        node = select_node(root)
        expand_node(node, root_player_type, win_nums, constraints, for_win)
        game_outcome = simulate_depth_charge(
            node, root_player_type, win_nums, constraints, for_win
        )
        backprop(node, root_player_type, game_outcome)

    action = utils.rand_max(root.children, key=lambda x: x.visits)[0].action
    dist = {node.action: node.visits for node in root.children}
    num_nodes = root.num_nodes

    return action, dist, num_nodes


def node_score(node, scoring_method="ucb_normalized", explore_weight=math.sqrt(2)):
    # compute "value" of the node
    # here, use UCB
    if scoring_method == "ucb_normalized":
        # w_i / n_i + (c * sqrt(t) / n_i)
        n_visits = node.visits

        if n_visits == 0:
            score = float("inf")
        else:
            # score = exploit_term + explore_weight * explore_term
            adj_value = (node.value + node.visits) / (2 * node.visits)
            score = adj_value + np.sqrt(2 * np.log(node.parent.visits) / node.visits)
    elif scoring_method == "ucb":
        n_visits = node.visits

        if n_visits == 0:
            score = float("inf")
        else:
            score = node.value / node.visits + np.sqrt(
                2 * np.log(node.parent.visits) / node.visits
            )
    # for now, no alternatives.... could remove the if
    else:
        score = node.value
    return score


def select_node(node, scoring_method="ucb_normalized"):
    # as long as the node has children, select one to expand
    while len(node.children) != 0:
        # get the children from the current node
        children = node.children
        # choose node according to its current expected value
        node, _ = utils.rand_max(children, key=lambda x: node_score(x, scoring_method))
    return node


def expand_node(node, root_player_type, win_nums, constraints, for_win):

    state = node.state  # board
    player_turn_seq = node.player_turn_seq

    # current node is the player who has just made a move ("current player")
    # that player is now checking if they have won
    # if not, they assess children from that node
    current_player_type = node.player_type
    current_player_turn = node.turn_idx

    if utils.win_score(
        state, root_player_type, win_nums, for_win, constraints
    ) != 0 or utils.is_draw(state):
        # can't expand any further -- game is over
        return None

    # otherwise, the game is not yet determined
    # get all legal moves from that state
    avail_moves = utils.get_available_moves(state)

    for move in avail_moves:
        # create a new node that represents playing that move in this state

        new_state = copy.deepcopy(state)

        utils.place_piece(new_state, move, current_player_type)

        # value here is value for the current player
        # the child is then one "turn" ahead (increment turn counter)
        # that child will now be one move ahead
        next_turn_idx = current_player_turn + 1  # this is now the turn of the child
        child = Node(
            new_state,
            turn_idx=next_turn_idx,
            player_turn_seq=player_turn_seq,
            value=0,
            action=move,
            parent=node,
        )
        # add this child to the parent node
        node.children.append(child)

    # randomly select a child
    return None


def simulate_depth_charge(node, root_player_type, win_nums, constraints, for_win):
    game_outcome = 0
    game_over = False

    board = copy.deepcopy(node.state)
    player_turn_seq = (
        node.player_turn_seq
    )  # this is the same for all nodes, just change idx

    turn_idx = node.turn_idx

    # keep charging til the game is over
    while not game_over:
        # make a move randomly
        current_player_type = player_turn_seq[turn_idx]
        move_metadata = uni_random.act(
            board,
            current_player_type,
            win_nums,
            for_win,
            constraints,
            turn_idx,
            player_turn_seq,
        )
        if move_metadata is not None:
            # make move on board and incremement properties
            utils.place_piece(board, move_metadata["move"], current_player_type)

            turn_idx += 1
            current_player_type = player_turn_seq[turn_idx]

        else:
            # game is over
            win_score = utils.win_score(
                board, root_player_type, win_nums, for_win, constraints
            )
            if win_score:
                game_outcome = win_score
            else:
                game_over = 0

            game_over = True

    return game_outcome


def backprop(node, root_player_type, game_outcome):

    # update visit counts
    node.visits += 1

    # Update num_nodes based on children
    if len(node.children) > 0:
        node.num_nodes = 1 + sum(child.num_nodes for child in node.children)

    if node.parent:
        player_parent_type = node.parent.player_type
        if player_parent_type == root_player_type:
            node.value += game_outcome
        else:
            node.value -= game_outcome
        # recursively backpropogate to parent(s)
        backprop(node.parent, root_player_type, game_outcome)


def act(
    board, player, win_nums, for_win, constraints, plays, player_sequence, steps=10000
):
    start_time = time.time()

    action, action_distribution, num_nodes = make_move(
        board,
        player_turn_seq=player_sequence,
        turn_idx=plays,
        win_nums=win_nums,
        for_win=for_win,
        steps=steps,
        constraints=constraints,
    )

    elapsed_time = time.time() - start_time
    metadata = {
        "move": action,
        "dist": action_distribution,
        "pv_depth": None,
        "ave_depth": None,
        "num_nodes": num_nodes,
        "time_elapsed": elapsed_time,
        "logprob": 0,
    }
    return metadata
