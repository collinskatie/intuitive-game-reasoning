import os
import pathlib
import numpy as np
import pickle
import json
from models.play.run_models_intermediate_act import *
FILE_PATH = pathlib.Path(__file__).parent.resolve()

# INPUTS
model_name = "intermodel"
date = "2025-08-17"
results_dir = os.path.join(FILE_PATH, "results", date, model_name)
out_file = os.path.join(FILE_PATH, "to_recover", date, f"{model_name}.pickle")
num_sims = 50
agents = ["heuristic_search_eg", "heuristics", "heuristics_depth", "uni_random"]
param_configs = [
        {"agent": "heuristic_search_eg", "other_agent": "heuristics", "p1": {"steps": 636 * 5}, "p2": {}},
        {"agent": "heuristics", "other_agent": "heuristic_search_eg", "p1": {}, "p2": {"steps": 636 * 5}}
]
n_repeats = 1

for kwarg in param_configs:
    os.makedirs(os.path.join(results_dir, f"{kwarg}"), exist_ok=True)

games_path = os.path.join(FILE_PATH, "../../human-data/play-exp/human-v-human/final-play/final_agg.json")
with open(games_path) as f:
    game_df = json.load(f)
games = list(map(lambda x: game2idx[x], game_df.keys())) # games in play experiment
# games = range(1,122) # games in think experiment

files_to_recover_list = []
for kwarg in param_configs:
        # games = os.listdir(os.path.join(results_dir, f"{kwarg}"))
        # for game_idx in games: 
        # for game_idx in [10, 11, 57, 107, 117]:
        for game_idx in [61, 71]:
            os.makedirs(os.path.join(results_dir, f"{kwarg}", f"{game_idx}"), exist_ok=True)
            seeds = os.listdir(os.path.join(results_dir, f"{kwarg}", f"{game_idx}"))
            for j in range(num_sims):
                if f"{j}.txt" not in seeds:
                    files_to_recover_list.append((kwarg, game_idx, j))

os.makedirs(os.path.dirname(out_file), exist_ok=True)
with open(os.path.join(out_file), "wb") as f:
    pickle.dump(n_repeats * files_to_recover_list, f)
print(len(n_repeats * files_to_recover_list))
