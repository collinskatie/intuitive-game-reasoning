from models.utils import *

import pandas as pd
from tqdm import tqdm
from tqdm import trange
import random
import multiprocessing
import datetime
import sys
import time 
import os
import pathlib
import pickle
import models.agents.heuristics as heuristics
import models.agents.mcts as mcts
import models.agents.uni_random as uni_random
FILE_PATH = pathlib.Path(__file__).parent.resolve()

# INPUTS 
model_name = "heuristics"
date = "2025-07-24"
recover_file = os.path.join(FILE_PATH, "to_recover", date, f"{model_name}.pickle")
out_dir = os.path.join(FILE_PATH, "results", date, model_name)

df = pd.read_csv(os.path.join(FILE_PATH, "../../stimuli/parsable_stimuli_labels.csv"))

games = []

for index, row in df.iterrows():
    games.append(row.to_dict())

def get_model_pred(game, agent, early_stop=False, num_sims=100, other_agent="self", intermediate_board=None, seed=None, **kwargs):
    if seed:
        random.seed(seed)
    index = game["index"]
    players = ["X", "O"]
    num_players = len(players)
    win_num = game["N"]
    for_win = game["N-for-win"]
    if game["diff-win"] == 1:
        win_nums = {"X": game["N"], "O": game["N"]-1}
    else:
        win_nums = {"X": game["N"], "O": game["N"]}
    two_pieces = {"X": game["player1-2pieces"], "O": game["player2-2pieces"]}
    constraints = {
        "X": {"hv": game["player1-hv-win"], "diag": game["player1-diag-win"]},
        "O": {"hv": game["player2-hv-win"], "diag": game["player2-diag-win"]}
    }
    board = construct_board(game["board-x"], game["board-y"])
    board_size = game["board-x"] * game["board-y"]

    player_sequence = calculate_player_sequence(board_size, two_pieces, players)
    
    if other_agent == "self": 
        other_agent = agent


    def simulate_one_game(starting_board, player_1, player_2, intermediate_board=None):

        # Simulate a game.
        num_plays = board_size
        if early_stop:
            num_plays = random.randint(1, board_size)
            
        p1_type = eval(player_1+ ".act")
        p2_type = eval(player_2+ ".act")

        all_pv_depths = []
        all_ave_depths = []
        all_num_nodes = []
        logprob = 0
        if intermediate_board is None:  
            plays = 0
            cur_player = players[0]
            
            board = [row[:] for row in starting_board]
            
            if two_pieces[players[0]] and num_plays > 1:
                metadata = p1_type(board, players[0], win_nums, for_win, constraints, plays, player_sequence, **kwargs)
                move_1 = metadata["move"]
                place_piece(board, move_1, players[0])
                all_pv_depths.append(metadata["pv_depth"])
                all_ave_depths.append(metadata["ave_depth"])
                all_num_nodes.append(metadata["num_nodes"])
                plays +=1
                metadata = p1_type(board, players[0], win_nums, for_win, constraints, plays, player_sequence, **kwargs)
                move_2 = metadata["move"]
                place_piece(board, move_2, players[0])
                all_pv_depths.append(metadata["pv_depth"])
                all_ave_depths.append(metadata["ave_depth"])
                all_num_nodes.append(metadata["num_nodes"])
                plays +=1
                cur_player = players[1]
            elif two_pieces[players[1]] and num_plays > 2:
                metadata = p1_type(board, players[0], win_nums, for_win, constraints, plays, player_sequence, **kwargs)
                move_0 = metadata["move"]
                place_piece(board, move_0, players[0])
                all_pv_depths.append(metadata["pv_depth"])
                all_ave_depths.append(metadata["ave_depth"])
                all_num_nodes.append(metadata["num_nodes"])
                plays +=1
                metadata = p2_type(board, players[1], win_nums, for_win, constraints, plays, player_sequence, **kwargs)
                move_1 = metadata["move"]
                place_piece(board, move_1, players[1])
                all_pv_depths.append(metadata["pv_depth"])
                all_ave_depths.append(metadata["ave_depth"])
                all_num_nodes.append(metadata["num_nodes"])
                plays +=1
                metadata = p2_type(board, players[1], win_nums, for_win, constraints, plays, player_sequence, **kwargs)
                move_2 = metadata["move"]
                place_piece(board, move_2, players[1])
                all_pv_depths.append(metadata["pv_depth"])
                all_ave_depths.append(metadata["ave_depth"])
                all_num_nodes.append(metadata["num_nodes"])
                plays +=1   
        else: 
            plays = int(np.sum(np.array(starting_board) != np.array(intermediate_board)))
            cur_player = player_sequence[plays]
            starting_board = intermediate_board
            board = [row[:] for row in starting_board]
  
        while not has_won(board, players[0], win_nums, for_win, constraints) and not has_won(board, players[1], win_nums, for_win, constraints) and not is_draw(board) and plays < num_plays:
            metadata = p1_type(board, cur_player, win_nums, for_win, constraints, plays, player_sequence, **kwargs) if cur_player == players[0] else p2_type(board, cur_player, win_nums, for_win, constraints, plays, player_sequence, **kwargs)
            move = metadata["move"]
            if move is None:
                break
            else:
                move = (move[0], move[1])
                place_piece(board, move, cur_player)
                all_pv_depths.append(metadata["pv_depth"])
                all_ave_depths.append(metadata["ave_depth"])
                all_num_nodes.append(metadata["num_nodes"])
                logprob += metadata["logprob"]
                plays += 1
                cur_player = players[1] if cur_player == players[0] else players[0]
        if early_stop and plays >= num_plays and win_score(board, players[0], win_nums, for_win, constraints) == 0:
            factor = 1 / (1 + np.exp(-(plays / (2 * win_num))))
            return {"game_score": 0, 
                    "game_length": plays,
                    "all_pv_depths": all_pv_depths,
                    "all_ave_depths": all_ave_depths,
                    "all_num_nodes": all_num_nodes,
                    "logprob": logprob, 
                    "early_stop": True,
                    "early_stop_plays": num_plays}
        return {"game_score": win_score(board, players[0], win_nums, for_win, constraints),
                "game_length": plays,
                "all_pv_depths": all_pv_depths,
                "all_ave_depths": all_ave_depths,
                "all_num_nodes": all_num_nodes,
                "logprob": logprob,
                "early_stop": False,
                "early_stop_plays": num_plays}

    game_scores = []
    game_lengths = []
    all_pv_depths = []
    all_ave_depths = []
    all_num_nodes = []
    logprob = 0
    all_early_stops = []
    all_early_stop_plays = []
    time_elapsed = []
    
    
    for i in range(num_sims):
        
        start = time.time()
        result = simulate_one_game(board, agent, other_agent, intermediate_board=intermediate_board)
        end = time.time()

        game_score = result["game_score"]
        game_length = result["game_length"]
        pv_depths = result["all_pv_depths"]
        ave_depths = result["all_ave_depths"]
        num_nodes = result["all_num_nodes"]
        logprob += result["logprob"]
        early_stop = result["early_stop"]
        early_stop_plays = result["early_stop_plays"]
        game_scores.append(game_score)
        game_lengths.append(game_length)
        all_pv_depths.append(pv_depths)
        all_ave_depths.append(ave_depths)
        all_num_nodes.append(num_nodes)
        all_early_stops.append(early_stop)
        all_early_stop_plays.append(early_stop_plays)
        time_elapsed.append(end-start)
    
    outcome = {"index": index,
               "game_scores": game_scores, 
               "game_lengths": game_lengths,
               "time_elapsed": time_elapsed, 
               "all_pv_depths": all_pv_depths,
               "all_ave_depths": all_ave_depths,
               "all_num_nodes": all_num_nodes,
               "logprob": logprob,
               "early_stop": all_early_stops,
               "early_stop_plays": all_early_stop_plays}
    return outcome

def make_model_pred_and_write(model_name, id):
    kwargs, game_idx, seed = id
    game = list(filter(lambda x: x["index"] == game_idx, games))[0]
    model_results = get_model_pred(
        game, 
        model_name, 
        seed=seed,
        num_sims=1,
        **kwargs
        )
    out_subdir = os.path.join(out_dir, f"{kwargs}/{game['index']}")
    out_file = os.path.join(out_subdir, f"{seed}.txt")
    os.makedirs(out_subdir, exist_ok=True)
    with open(out_file, "w") as f:
        f.write(str(model_results))
    return model_results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--setting', type=str, choices=['recover', 'local'], help='Setting to run: recover or local')
    parser.add_argument('--task_id', type=int)
    parser.add_argument('--interval', type=int)
    args = parser.parse_args()

    setting = args.setting
    task_id = args.task_id
    interval = args.interval

    with open(recover_file, "rb") as f:
        games_to_recover_list = pickle.load(f)

    if setting == "recover":
        filtered_games = games_to_recover_list[task_id*interval:(task_id+1)*interval]
        inputs = [(model_name, id) for id in filtered_games]
        print(f"task_id: {task_id}\ninterval: {interval}\n")
        with multiprocessing.Pool() as pool:
            model_results = pool.starmap(make_model_pred_and_write, inputs)
    
    elif setting == "local":
        inputs = [(model_name, id) for id in games_to_recover_list]
        with multiprocessing.Pool(12) as pool:
            model_results = pool.starmap(make_model_pred_and_write, inputs)
