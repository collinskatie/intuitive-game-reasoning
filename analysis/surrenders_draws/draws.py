import pandas as pd 
import matplotlib.pylab as plt
import os 
import importlib
from analysis import analysis_utils
import numpy as np
import scipy
import sklearn.linear_model
from tqdm import trange
import json
from models.just_think.run_models import *
import pathlib
import pickle
import sys
FILE_PATH = pathlib.Path(__file__).parent.resolve()


class LazyGetModelPred:
    def __init__(self, game, agent, early_stop=False, num_sims=100, other_agent="self", intermediate_board=None, **kwargs):
        self.game = game
        self.agent = agent
        self.early_stop = early_stop
        self.num_sims = num_sims
        self.other_agent = other_agent
        self.intermediate_board = intermediate_board
        self.seed = None
        self.kwargs = kwargs
    def compute(self):
        evaluations = get_model_pred(self.game,
                                     self.agent,
                                     self.early_stop,
                                     self.num_sims,
                                     self.other_agent,
                                     self.intermediate_board,
                                     self.seed,
                                     **self.kwargs)
        return evaluations
        

def compute_lazy(x):
    print("Simulation started, ", x.agent, x.game['index'])
    evaluation = x.compute()
    print("Simulation completed, ", x.agent, x.game['index'])
    return evaluation

if __name__ == '__main__':
    suffix = sys.argv[1]

    data_path = os.path.join(FILE_PATH,"../../human-data/play-exp/human-v-human/final-play/final_agg.json")
    stimuli_path = os.path.join(FILE_PATH, '../../stimuli/cogsci_just_think_stimuli.csv')

    with open(data_path) as f:
        data = json.load(f)

    games, idx2game, gamename2idx, game_stimuli = analysis_utils.process_game_stimuli(stimuli_path)
    num_sims = 1
    draw_outcomes = {"request_player": [], "game": [], "board": [], "accept_reject": [], "heuristics_simulations": [], "hs_simulations": []}
    for gamename in data:
        draw_info = data[gamename]['draw_info']
        for draw in draw_info:
            for accept_board in draw['accept']:
                request_player, _, board = accept_board
                board = prolific2standardboard(board)
                gamename = gamename.replace(" Horizontal, vertical, and diagonal all count.", "")
                game_idx = gamename2idx[gamename]
                game = list(filter(lambda x: x["index"] == game_idx, games))[0]
                sims_h = LazyGetModelPred(game, "heuristics", early_stop=False, num_sims=num_sims, intermediate_board=board)
                sims_hs = LazyGetModelPred(game, "heuristic_search_eg", early_stop=False, num_sims=num_sims, intermediate_board=board)
                draw_outcomes['game'].append(gamename)
                draw_outcomes['board'].append(board)

                draw_outcomes['heuristics_simulations'].append(sims_h)
                draw_outcomes['hs_simulations'].append(sims_hs)
                draw_outcomes['request_player'].append("X" if request_player == 1 else "O")
                draw_outcomes['accept_reject'].append('accept')
            for reject_board in draw['reject']:
                request_player, _, board = reject_board
                board = prolific2standardboard(board)
                gamename = gamename.replace(" Horizontal, vertical, and diagonal all count.", "")
                game_idx = gamename2idx[gamename]
                game = list(filter(lambda x: x["index"] == game_idx, games))[0]
                sims_h = LazyGetModelPred(game, "heuristics", early_stop=False, num_sims=num_sims, intermediate_board=board)
                sims_hs = LazyGetModelPred(game, "heuristic_search_eg", early_stop=False, num_sims=num_sims, intermediate_board=board)
                draw_outcomes['game'].append(gamename)
                draw_outcomes['board'].append(board)

                draw_outcomes['heuristics_simulations'].append(sims_h)
                draw_outcomes['hs_simulations'].append(sims_hs)
                draw_outcomes['request_player'].append("X" if request_player == 1 else "O")
                draw_outcomes['accept_reject'].append('reject')

    print("Total simulations: ", len(draw_outcomes['heuristics_simulations']))

    with multiprocessing.Pool() as pool:
        draw_outcomes['heuristics_simulations'] = pool.map(compute_lazy, draw_outcomes['heuristics_simulations'])
    draw_outcomes['p1_pwin_heuristics'] = [np.mean(np.array(x['game_scores']) == 1) for x in draw_outcomes['heuristics_simulations']]
    draw_outcomes['p1_plose_heuristics'] = [np.mean(np.array(x['game_scores']) == -1) for x in draw_outcomes['heuristics_simulations']]
    draw_outcomes['game_length_heuristics'] = [np.mean(x['game_lengths']) for x in draw_outcomes['heuristics_simulations']]

    with multiprocessing.Pool() as pool:
        draw_outcomes['hs_simulations'] = pool.map(compute_lazy, draw_outcomes['hs_simulations'])
    draw_outcomes['p1_pwin_hs'] = [np.mean(np.array(x['game_scores']) == 1) for x in draw_outcomes['hs_simulations']]
    draw_outcomes['p1_plose_hs'] = [np.mean(np.array(x['game_scores']) == -1) for x in draw_outcomes['hs_simulations']]
    draw_outcomes['game_length_hs'] = [np.mean(x['game_lengths']) for x in draw_outcomes['hs_simulations']]

    del draw_outcomes['heuristics_simulations']
    del draw_outcomes['hs_simulations']


    with open(os.path.join(FILE_PATH, "draws_heuristics_depth", f'draw_outcomes_{suffix}.pkl'), 'wb') as f:
        pickle.dump(draw_outcomes, f)
