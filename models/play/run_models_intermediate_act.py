from models.utils import *
import models.agents.uni_random as uni_random
import models.agents.heuristics as heuristics
import models.agents.mcts as mcts
import models.agents.heuristic_search_eg as heuristic_search_eg
import models.agents.additional.heuristic_search_eg_no_inheritance as heuristic_search_no_inheritance

import pandas as pd
from tqdm import tqdm
from tqdm import trange
import random
import multiprocessing
import datetime
import sys
import time 
import os
import json
import pathlib
import pickle

FILE_PATH = pathlib.Path(__file__).parent.resolve()
MODEL_MAPPING = {
    "uni_random": uni_random,
    "heuristics": heuristics,
    "mcts": mcts,
    "heuristic_search_eg": heuristic_search_eg,
    "heuristic_search_no_inheritance": heuristic_search_no_inheritance
}

# INPUTS
model_name = "heuristic_search_eg"
date = "2025-07-23"
recover_file = os.path.join(FILE_PATH, "to_recover", date, f"{model_name}.pickle")
out_dir = os.path.join(FILE_PATH, "results", date)
all_stimuli_data_path = os.path.join(FILE_PATH, f"../../human-data/play-exp/human-v-human/final-play/final_agg.json")

df = pd.read_csv(os.path.join(FILE_PATH, "../../stimuli/parsable_stimuli_labels.csv"))
games = []

for _, row in df.iterrows():
    games.append(row.to_dict())
games_sorted  = sorted(games, key=lambda x: x['board-x']*x['board-y'])

# games are ordered with the same index
all_games = pd.read_csv(os.path.join(FILE_PATH, "../../stimuli/cogsci_just_think_stimuli.csv"))
livegameplay_games = pd.read_csv(os.path.join(FILE_PATH, "../../stimuli/updated_final_play_game.csv"))
def get_stimuli_id(entry): 
    n_rows, n_cols = entry["Board size"].split(" x ")
    n_rows = float(n_rows)
    n_cols = float(n_cols)
    return f"{n_rows}*{n_cols}*{entry['Winning condition']}"

livegameplay_games["stimuli_id"] = [get_stimuli_id(row) for idx, row in livegameplay_games.iterrows()]

parsed_games = []
idx2game = {}
game_stimuli = {}
for game_idx, game in all_games.iterrows():
    board_rows, board_cols = game["Board size"].split(" x ")
    win_conditions = game["Winning condition"]
    parsed_games.append([board_rows, board_cols, win_conditions])
    # match the human game id
    if "nf" not in board_rows: 
        board_rows = float(board_rows)
        board_cols = float(board_cols)
    else: 
        board_rows = "inf"
        board_cols = "inf"
        # for parity back with the human games
    game_id = f"{board_rows}*{board_cols}*{win_conditions}"
    idx2game[game_idx+1] = game_id
    game_stimuli[game_id] = games[game_idx]
    
play_game_objs = []
for game_id in livegameplay_games["stimuli_id"]:
    game = game_stimuli[game_id]
    game["stimuli_id"] = game_id
    play_game_objs.append(game)

game2idx = {item[1]: item[0] for item in idx2game.items()}

def get_board(id, all_stimuli_data):
    _, arena, game_idx, move_idx, _ = id
    arena_idx = all_stimuli_data[idx2game[game_idx]]['arena'].index(arena)
    boards = eval(all_stimuli_data[idx2game[game_idx]]['boards'][arena_idx])
    return boards[move_idx]

def act_1(model_name, game_id, all_stimuli_data):
    kwargs, arena, game_idx, move_idx, seed = game_id
    random.seed(seed)

    intermediate_board = get_board(game_id, all_stimuli_data)
    intermediate_board = prolific2standardboard(intermediate_board)
    game = list(filter(lambda x: x['index'] == game_idx, games))[0]

    index = game['index']
    for_win = game['N-for-win']
    if game['diff-win'] == 1:
        win_nums = {'X': game['N'], 'O': game['N']-1}
    else:
        win_nums = {'X': game['N'], 'O': game['N']}
    two_pieces = {'X': game['player1-2pieces'], 'O': game['player2-2pieces']}
    constraints = {
        'X': {'hv': game['player1-hv-win'], 'diag': game['player1-diag-win']},
        'O': {'hv': game['player2-hv-win'], 'diag': game['player2-diag-win']}
    }
    starting_board = construct_board(game['board-x'], game['board-y'])
    board_size = game['board-x'] * game['board-y']

    player_sequence = calculate_player_sequence(board_size, two_pieces, players)
    plays = int(np.sum(np.array(starting_board) != np.array(intermediate_board)))
    cur_player = player_sequence[plays]

    agent = MODEL_MAPPING[model_name]
    act_metadata = agent.act(
        intermediate_board, 
        cur_player, 
        win_nums, 
        for_win, 
        constraints, 
        plays, 
        player_sequence, 
        **kwargs
        )
    if act_metadata is not None:
        model_results = {
            "index": index,
            "dist": act_metadata["dist"],
            "pv_depth": act_metadata["pv_depth"],
            "ave_depth": act_metadata["ave_depth"],
            "time_elapsed": act_metadata["time_elapsed"],
        }
    else:
        model_results = {
            "index": index,
            "dist": None,
            "pv_depth": None,
            "ave_depth": None,
            "time_elapsed": None,
        }
    out_file = os.path.join(out_dir, f"{model_name}/{kwargs}/{arena}/{game_idx}/{move_idx}/{seed}.txt")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w') as f:
        f.write(str(model_results))
    return model_results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--setting', type=str, choices=['recover', 'local'], help='Setting to run: recover or local')
    parser.add_argument('--task_id', type=int)
    parser.add_argument('--interval', type=int)
    args = parser.parse_args()

    setting = args.setting
    task_id = args.task_id
    interval = args.interval

    with open(all_stimuli_data_path) as f:
        all_stimuli_data = json.load(f)
    with open(recover_file, "rb") as f:
        games_to_recover_list = pickle.load(f)
    
    if setting == "recover":
        filtered_games = games_to_recover_list[task_id*interval:(task_id+1)*interval]
        inputs = [(model_name, id, all_stimuli_data) for id in filtered_games]
        print(f"task_id: {task_id}\ninterval: {interval}\n")
        with multiprocessing.Pool() as pool:
            model_results = pool.starmap(act_1, inputs)

    if setting == "local":
        inputs = [(model_name, id, all_stimuli_data) for id in games_to_recover_list]
        with multiprocessing.Pool(12) as pool:
            model_results = pool.starmap(act_1, inputs)
