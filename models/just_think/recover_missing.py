import os
import pathlib
import numpy as np
import pickle
FILE_PATH = pathlib.Path(__file__).parent.resolve()

# INPUTS
model_name = "heuristics"
date = "2025-07-24"
results_dir = os.path.join(FILE_PATH, "results", date, model_name)
out_file = os.path.join(FILE_PATH, "to_recover", date, f"{model_name}.pickle")
num_sims = 50
n_repeats = 1
param_configs = [
    {}
]

for kwarg in param_configs:
    os.makedirs(os.path.join(results_dir, f"{kwarg}"), exist_ok=True)

files_to_recover_list = []
for kwarg in param_configs:
        for game_idx in range(1,122):
            os.makedirs(os.path.join(results_dir, f"{kwarg}", f"{game_idx}"), exist_ok=True)
            seeds = os.listdir(os.path.join(results_dir, f"{kwarg}", f"{game_idx}"))
            for j in range(num_sims):
                if f"{j}.txt" not in seeds:
                    files_to_recover_list.append((kwarg, game_idx, j))

os.makedirs(os.path.dirname(out_file), exist_ok=True)
with open(out_file, "wb") as f:
    pickle.dump(n_repeats * files_to_recover_list, f)
print(len(n_repeats * files_to_recover_list))
