import os
import numpy as np
from models.play.run_models_intermediate_act import *
import pathlib
import pickle
import random

FILE_PATH = pathlib.Path(__file__).parent.resolve()

# INPUTS
model_name = "heuristic_search_eg"
date = "2025-07-23"
results_dir = os.path.join(FILE_PATH, f"results", date, f"{model_name}")
stimuli_dir = os.path.join(FILE_PATH, f"../../human-data/play-exp/human-v-human/final-play/final_agg.json")
out_file = os.path.join(FILE_PATH, "to_recover", date, f"{model_name}.pickle")
num_sims = 50
param_configs = [{}]
n_repeats = 1

def get_all_boards(all_stimuli_data, num_sims):
    res = []
    for game in all_stimuli_data.keys():
        for arena_idx, arena in enumerate(all_stimuli_data[game]['arena']):
            for move_idx, board in enumerate(eval(all_stimuli_data[game]['boards'][arena_idx])):
                for seed in range(0,num_sims):
                    res.append((arena, game2idx[game], move_idx, seed))
    return res

def cp(*args):
    """
    Returns the cartesian product of a list of lists. Each element of 
    *args is a list of integers/floats or tuples. 
    """
    res = [()]
    for arg in args[::-1]:
        if type(arg[0]) != tuple:
            arg = [(x,) for x in arg]
        res = [x+y for x in arg for y in res]
    return res

os.makedirs(results_dir, exist_ok=True)
dir = os.listdir(results_dir)

with open(stimuli_dir) as f:
    all_stimuli_data = json.load(f)
all_boards = get_all_boards(all_stimuli_data, num_sims)
all_configs = cp(param_configs, all_boards)

files_to_recover_list = []
for config in all_configs:
    results_path = os.path.join(results_dir,*map(lambda x: str(x), config))+".txt"
    if not os.path.exists(results_path):
        files_to_recover_list.append(config)

random.shuffle(files_to_recover_list)
os.makedirs(os.path.dirname(out_file), exist_ok=True)
with open(out_file, "wb") as f:
    pickle.dump(n_repeats * files_to_recover_list, f)

print(len(n_repeats * files_to_recover_list))
