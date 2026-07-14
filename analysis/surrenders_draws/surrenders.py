import pandas as pd 
import matplotlib.pylab as plt
import os 
import importlib
from analysis import analysis_utils
import numpy as np
import scipy
import sklearn.linear_model
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
                                     self.intermediate_board)
        return evaluations
        

def compute_lazy(x):
    print("Simulation started, ", x.agent, x.game['index'])
    evaluation = x.compute()
    print("Simulation completed, ", x.agent, x.game['index'])
    return evaluation

if __name__ == '__main__':
    suffix = sys.argv[1]

    data_path = os.path.join(FILE_PATH, "../../human-data/play-exp/human-v-human/final-play/final_agg.json")
    stimuli_path = os.path.join(FILE_PATH, '../../stimuli/cogsci_just_think_stimuli.csv')

    with open(data_path) as f:
        data = json.load(f)

    games, idx2game, gamename2idx, game_stimuli = analysis_utils.process_game_stimuli(stimuli_path)
    num_sims = 1
    surrender_outcomes = {"surrendered_player": [], "game": [], "board": [], "heuristics_simulations": [], "hs_simulations": []}
    for gamename in data:
        surrender_info = data[gamename]['surrender_info']
        for surrender_instance in surrender_info:
            if surrender_instance is None:
                continue
            surrendered_player = "X" if surrender_instance[0] == 1 else "O"
            board = analysis_utils.prolific2standardboard(surrender_instance[2])
            gamename = gamename.replace(" Horizontal, vertical, and diagonal all count.", "")
            game_idx = gamename2idx[gamename]
            game = list(filter(lambda x: x["index"] == game_idx, games))[0]
            sims_h = LazyGetModelPred(game, "heuristics", early_stop=False, num_sims=num_sims, intermediate_board=board, block_weight=0)
            sims_hs = LazyGetModelPred(game, "heuristic_search_eg", early_stop=False, num_sims=num_sims, intermediate_board=board)

            surrender_outcomes['game'].append(gamename)
            surrender_outcomes['surrendered_player'].append(surrendered_player)
            surrender_outcomes['board'].append(board)
            surrender_outcomes['heuristics_simulations'].append(sims_h)
            surrender_outcomes['hs_simulations'].append(sims_hs)

    print("Total simulations: ", len(surrender_outcomes['heuristics_simulations']))

    with multiprocessing.Pool() as pool:
        surrender_outcomes['heuristics_simulations'] = pool.map(compute_lazy, surrender_outcomes['heuristics_simulations'])
    surrender_outcomes['p1_pwin_heuristics'] = [np.mean(np.array(x['game_scores']) == 1) for x in surrender_outcomes['heuristics_simulations']]
    surrender_outcomes['p1_plose_heuristics'] = [np.mean(np.array(x['game_scores']) == -1) for x in surrender_outcomes['heuristics_simulations']]
    surrender_outcomes['game_length_heuristics'] = [np.mean(x['game_lengths']) for x in surrender_outcomes['heuristics_simulations']]

    with multiprocessing.Pool() as pool:
        surrender_outcomes['hs_simulations'] = pool.map(compute_lazy, surrender_outcomes['hs_simulations'])
    surrender_outcomes['p1_pwin_hs'] = [np.mean(np.array(x['game_scores']) == 1) for x in surrender_outcomes['hs_simulations']]
    surrender_outcomes['p1_plose_hs'] = [np.mean(np.array(x['game_scores']) == -1) for x in surrender_outcomes['hs_simulations']]
    surrender_outcomes['game_length_hs'] = [np.mean(x['game_lengths']) for x in surrender_outcomes['hs_simulations']]


    del surrender_outcomes['heuristics_simulations']
    del surrender_outcomes['hs_simulations']

    with open(os.path.join(FILE_PATH, "2025-07-07_surrenders_heuristic_search_eg", f'surrender_outcomes_{suffix}.pkl'), 'wb') as f:
        pickle.dump(surrender_outcomes, f)
