from models.utils import *
import models.agents.uni_random as uni_random
import models.agents.heuristics as heuristics
import models.agents.mcts as mcts
import models.agents.heuristic_search_eg as heuristic_search
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


FILE_PATH = pathlib.Path(__file__).parent.resolve()
MODEL_MAPPING = {
    "uni_random": uni_random,
    "heuristics": heuristics,
    "mcts": mcts,
    "heuristic_search_eg": heuristic_search,
    "heuristic_search_no_inheritance": heuristic_search_no_inheritance
}

df = pd.read_csv(os.path.join(FILE_PATH, "../../stimuli/parsable_stimuli_labels.csv"))

games = []

for _, row in df.iterrows():
    games.append(row.to_dict())
games_sorted  = sorted(games, key=lambda x: x['board-x']*x['board-y'])

with open(os.path.join(FILE_PATH, "../../human-data/play-exp/human-v-human/all_stimuli_data.json")) as f:
    all_stimuli_data = json.load(f)

# games are ordered with the same index
all_games = pd.read_csv(os.path.join(FILE_PATH, "../../stimuli/cogsci_just_think_stimuli.csv"))
livegameplay_games = pd.read_csv(os.path.join(FILE_PATH, "../../stimuli/human_human_pilot_stimuli.csv"))
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

def get_model_pred(game, agent, early_stop=False, num_sims=100, other_agent="self", intermediate_board=None, seed=7, **kwargs):
    print(game)
    random.seed(seed)
    index = game['index']
    players = ['X', 'O']
    num_players = len(players)
    win_num = game['N']
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
    board = construct_board(game['board-x'], game['board-y'])
    board_size = game['board-x'] * game['board-y']

    player_sequence = calculate_player_sequence(board_size, two_pieces, players)
    
    if other_agent == "self": 
        other_agent = agent


    def simulate_one_game(starting_board, player_1, player_2, intermediate_board=None):

        # Simulate a game.
        num_plays = board_size
        if early_stop:
            num_plays = random.randint(1, board_size)
            
        p1_type = MODEL_MAPPING[player_1]
        p2_type = MODEL_MAPPING[player_2]
        
        all_boards = [] # katie added for tracking
        all_move_dists = []
        
        
        if intermediate_board is None:  
            plays = 0
            cur_player = players[0]
            
            board = [row[:] for row in starting_board]
            
            if two_pieces[players[0]] and num_plays > 1:
                metadata = p1_type.act(board, players[0], win_nums, for_win, constraints, plays, player_sequence, **kwargs)
                plays +=1
                move_1 = metadata["move"]
                place_piece(board, move_1, players[0])
                metadata = p1_type.act(board, players[0], win_nums, for_win, constraints, plays, player_sequence, **kwargs)
                plays +=1
                move_2 = metadata["move"]
                place_piece(board, move_2, players[0])
                cur_player = players[1]
            elif two_pieces[players[1]]and num_plays > 2:
                metadata = p1_type.act(board, players[0], win_nums, for_win, constraints, plays, player_sequence, **kwargs)
                move_0 = metadata["move"]
                place_piece(board, move_0, players[0])
                plays +=1
                metadata = p2_type.act(board, players[1], win_nums, for_win, constraints, plays, player_sequence, **kwargs)
                move_1 = metadata["move"]
                place_piece(board, move_1, players[1])
                plays +=1
                metadata = p2_type.act(board, players[1], win_nums, for_win, constraints, plays, player_sequence, **kwargs)
                move_2 = metadata["move"]
                place_piece(board, move_2, players[1])
                plays +=1   
        else: 
            plays = int(np.sum(np.array(starting_board) != np.array(intermediate_board)))
            cur_player = player_sequence[plays]
            starting_board = intermediate_board
            board = [row[:] for row in starting_board]
        
                

         
        
        
        while not has_won(board, players[0], win_nums, for_win, constraints) and not has_won(board, players[1], win_nums, for_win, constraints) and not is_draw(board) and plays < num_plays:
            metadata = p1_type.act(board, cur_player, win_nums, for_win, constraints, plays, player_sequence, **kwargs) if cur_player == players[0] else p2_type.act(board, cur_player, win_nums, for_win, constraints, plays, player_sequence, **kwargs)
            move = metadata["move"]
            if move is None:
                break
            else:
                move = (move[0], move[1])
                place_piece(board, move, cur_player)
                saved_board = copy.deepcopy(board)
                all_boards.append(saved_board)
                all_move_dists.append(metadata["dist"])


                cur_player = players[1] if cur_player == players[0] else players[0]
                plays += 1
        if early_stop and plays >= num_plays and win_score(board, players[0], win_nums, for_win, constraints) == 0:
            factor = 1 / (1 + np.exp(-(plays / (2 * win_num))))
            return (random.choices([0, 1, -1], [factor, (1-factor)/2 , (1-factor)/2], k=1)[0], plays)
        return (win_score(board, players[0], win_nums, for_win, constraints), plays, all_move_dists, all_boards)

    game_scores = []
    game_lengths = []
    all_boards = []
    all_move_dists = []
    time_elapsed = []
    
    
    for i in range(num_sims):

        start = time.time()
        result = simulate_one_game(board, agent, other_agent, intermediate_board=intermediate_board)
        end = time.time()

        game_score = result[0]
        game_scores.append(game_score)
        game_length = result[1]
        game_lengths.append(game_length)
        time_elapsed.append(end-start)
        
        all_move_dists.append(result[-2])
        all_boards.append(result[-1])

    draws = game_scores.count(0)
    wins = game_scores.count(1)
    draw_percent = draws / num_sims
    win_percent = wins / num_sims
    
    outcome = {'index': index, 'draw_percent': draw_percent, 'win_percent': win_percent,
               "all_boards": all_boards, "all_move_dists": all_move_dists, 
               'game_scores': game_scores, 'game_lengths': game_lengths, 'time_elapsed': time_elapsed}
    return outcome

def get_all_boards(stimuli_data):
    res = []
    for game in stimuli_data.keys():
        for arena_idx, arena in enumerate(stimuli_data[game]['arena']):
            for move_idx, board in enumerate(stimuli_data[game]['boards'][arena_idx]):
                for seed in range(0,5):
                    res.append((arena, game2idx[game], move_idx+1, seed))
    return res

def get_board(id, stimuli_data):

    arena_idx = stimuli_data[idx2game[id[1]]]['arena'].index(id[0])
    boards = stimuli_data[idx2game[id[1]]]['boards'][arena_idx]
    return boards[id[2]-1]


def pred_1_intermediate(game_id, model_name):
    start = time.time()
    arena, game_idx, move_idx, seed = game_id
    intermediate_board = get_board(game_id, all_stimuli_data)
    print(intermediate_board)
    game = list(filter(lambda x: x['index'] == game_idx, games))[0]
    intermediate_board = prolific2standardboard(intermediate_board)
    model_results = get_model_pred(game, model_name, num_sims=1, intermediate_board=intermediate_board, seed=seed)
    end = time.time()
    out_file = f"results/{model_name}/{arena}/{game_idx}/{move_idx}/{seed}.txt"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w') as f:
        f.write(str(model_results))
    print(f"finish time: {end-start}\n")
    return model_results

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--setting', type=str, choices=["recover", "local"], help="Whether to recover missing files or run locally")
    parser.add_argument('--num_sims', type=int, help="Number of simulations to run per game")
    parser.add_argument('--task_id', type=int)
    parser.add_argument('--model_name', type=str, help="Name of the model to run")
    parser.add_argument('--offset', type=int, default=0, help="Offset for which files to recover")
    args = parser.parse_args()

    setting = args.setting
    num_sims = args.num_sims
    task_id = args.task_id
    model_name = args.model_name
    offset = args.offset

    if setting == "recover":
        with open(f"models/intermediate_boards/helpers/games_to_recover_{model_name}_list.txt", "r") as f:
            contents = f.read()
        games_to_recover_list = eval(contents)
        games_idx, seed = games_to_recover_list[offset+task_id]
        print(f"task_id: {task_id}\noffset: {offset}\nseed: {seed}\ngames_idx: {games_idx}\ngame_id: {game['index']}\n")
        model_results = pred_1_intermediate(game, seed, model_name)
    elif setting == "local":
        with open(f"models/intermediate_boards/helpers/games_to_recover_{model_name}_list.txt", "r") as f:
            contents = f.read()
        games_to_recover_list = eval(contents)
        inputs = [(id, model_name) for id in games_to_recover_list]
        with multiprocessing.Pool(12) as pool:
            model_results = pool.starmap(pred_1_intermediate, inputs)
