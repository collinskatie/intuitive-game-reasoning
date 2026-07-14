from models.utils import *
import models.agents.uni_random as uni_random
import models.agents.heuristics as heuristics
import models.agents.mcts as mcts
import models.agents.heuristic_search as heuristic_search

import pandas as pd
from tqdm import tqdm
from tqdm import trange
import random
import multiprocessing
import datetime
import sys
import time 
import os

df = pd.read_csv('../stimuli/parsable_stimuli_labels.csv')

games = []

for index, row in df.iterrows():
    games.append(row.to_dict())
games_sorted  = sorted(games, key=lambda x: x['board-x']*x['board-y'])

def get_model_pred(game, agent, early_stop=False, num_sims=100, other_agent="self", intermediate_board=None, seed=7, **kwargs):
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

        num_plays = board_size
        if early_stop:
            num_plays = random.randint(1, board_size)
            
        p1_type = eval(player_1+ ".act")
        p2_type = eval(player_2+ ".act")
        
        all_boards = [] 
        all_move_dists = []
        
        
        if intermediate_board is None:  
            plays = 0
            cur_player = players[0]
            
            board = [row[:] for row in starting_board]
            
            if two_pieces[players[0]] and num_plays > 1:
                metadata = p1_type(board, players[0], win_nums, for_win, constraints, plays, player_sequence, **kwargs)
                plays +=1
                move_1 = metadata["move"]
                place_piece(board, move_1, players[0])
                metadata = p1_type(board, players[0], win_nums, for_win, constraints, plays, player_sequence, **kwargs)
                plays +=1
                move_2 = metadata["move"]
                place_piece(board, move_2, players[0])
                cur_player = players[1]
            elif two_pieces[players[1]]and num_plays > 2:
                metadata = p1_type(board, players[0], win_nums, for_win, constraints, plays, player_sequence, **kwargs)
                move_0 = metadata["move"]
                place_piece(board, move_0, players[0])
                plays +=1
                metadata = p2_type(board, players[1], win_nums, for_win, constraints, plays, player_sequence, **kwargs)
                move_1 = metadata["move"]
                place_piece(board, move_1, players[1])
                plays +=1
                metadata = p2_type(board, players[1], win_nums, for_win, constraints, plays, player_sequence, **kwargs)
                move_2 = metadata["move"]
                place_piece(board, move_2, players[1])
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
               'game_scores': game_scores, 'game_lengths': game_lengths}
    return outcome


def mcts_20(game):
    pred = get_model_pred(game, 'mcts', num_sims=20)
    return pred

def heur(game):
    return get_model_pred(game, 'heuristics', num_sims=n_sim)

def rand(game):
    return get_model_pred(game, 'uni_random', num_sims=n_sim)


def heur_search_20(game): 
    start = time.time()
    pred = get_model_pred(game, 'heuristic_search', num_sims=20)
    end = time.time()
    return pred

def make_model_pred_20_and_write(game, model_name):
    start = time.time()
    model_results = get_model_pred(game, model_name, num_sims=20)
    end = time.time()
    out_file = f"results/2024-11-2/{model_name}/model_simulation_{game['index']}.txt"
    with open(out_file, 'w') as f:
        f.write(str(model_results))
    print(f"finish time: {end-start}\n")
    return model_results

def make_model_pred_1_and_write(game, seed, model_name):
    start = time.time()
    model_results = get_model_pred(game, model_name, num_sims=1, seed=seed)
    end = time.time()
    out_file = f"results/2024-11-2/{model_name}/model_simulation_{game['index']}/{seed}.txt"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w') as f:
        f.write(str(model_results))
    print(f"finish time: {end-start}\n")
    return model_results

def challenge1(game):
    return get_model_pred(game, 'heuristics', num_sims=n_sim, other_agent='uni_random')

def challenge2(game):
    return get_model_pred(game, 'uni_random', num_sims=n_sim, other_agent='heuristics')

n_sim = 200

if __name__ == '__main__':
    with multiprocessing.Pool(12) as pool:
        model_results_1 = pool.map(challenge1, games)
        model_results_2 = pool.map(challenge2, games)

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    with open(f'challenge1_results_{n_sim}_{timestamp}.txt', 'w') as f:
        f.write(str(model_results_1))
    with open(f'challenge2_results_{n_sim}_{timestamp}.txt', 'w') as f:
        f.write(str(model_results_2))