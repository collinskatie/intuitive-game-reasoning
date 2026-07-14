import os
import numpy as np
import pathlib
import pickle
import multiprocessing
FILE_PATH = pathlib.Path(__file__).parent.resolve()

# INPUTS
model_name = "heuristics"
date = "2025-07-23"
results_dir = os.path.join(FILE_PATH, "results", date, model_name)
out_dir = os.path.join(FILE_PATH, "merged_results", date, model_name)
merge_outputs = False

param_configs = [eval(kwarg) for kwarg in os.listdir(results_dir)]
def average_dicts(dict_list):
    if not dict_list:
        return {}
    if dict_list[0] is None:
        return None
    # Convert list of dicts to dict of lists
    combined = {
        key: [d[key] for d in dict_list]
        for key in dict_list[0].keys()
    }
    # Calculate means for each key
    return {
        key: np.mean(values) 
        for key, values in combined.items()
    }

def nanmean(arr):
    if all(i is None for i in arr):
        return None
    return np.mean(arr)
    
os.makedirs(out_dir, exist_ok=True)

def merge_one(kwarg):
    merge_matches = {}
    arenas = os.listdir(os.path.join(results_dir,f"{kwarg}"))
    for arena in arenas:
        print("arena:", arena)
        games_played = os.listdir(os.path.join(results_dir,f"{kwarg}/{arena}"))
        merge_matches[arena] = {}
        for game_idx in games_played:
            print("game_idx:", game_idx)
            all_moves = os.listdir(os.path.join(results_dir,f"{kwarg}/{arena}/{game_idx}"))
            merge_matches[arena][game_idx] = {}
            for move_idx in all_moves:
                seeds = os.listdir(os.path.join(results_dir,f"{kwarg}/{arena}/{game_idx}/{move_idx}"))
                for idx, seed_file in enumerate(seeds):
                    with open(os.path.join(results_dir,f"{kwarg}/{arena}/{game_idx}/{move_idx}/{seed_file}"), "r") as file1:
                        contents = file1.read()
                    if contents:
                        match_info = eval(contents)
                    else:
                        match_info = {'index': game_idx, "dist": None, "pv_depth": None, "ave_depth": None, "time_elapsed": None, "num_nodes": None}
                    if idx == 0:
                        merge_matches[arena][game_idx][move_idx] = {
                            'index': match_info['index'], 
                            'dist': [match_info['dist']], 
                            'pv_depth': [match_info['pv_depth']], 
                            'ave_depth': [match_info['ave_depth']],
                            'time_elapsed': [match_info.get('time_elapsed', None)],
                            'num_nodes': [match_info.get('num_nodes', None)]
                        }
                    else:
                        merge_matches[arena][game_idx][move_idx]['dist'] += [match_info['dist']]
                        merge_matches[arena][game_idx][move_idx]['pv_depth'] += [match_info['pv_depth']]
                        merge_matches[arena][game_idx][move_idx]['ave_depth'] += [match_info['ave_depth']]
                        merge_matches[arena][game_idx][move_idx]['time_elapsed'] += [match_info.get('time_elapsed', None)]
                        merge_matches[arena][game_idx][move_idx]['num_nodes'] += [match_info.get('num_nodes', None)]
                if merge_outputs:
                    merge_matches[arena][game_idx][move_idx]['dist'] = average_dicts(merge_matches[arena][game_idx][move_idx]['dist'])
                    merge_matches[arena][game_idx][move_idx]['pv_depth'] = nanmean(merge_matches[arena][game_idx][move_idx]['pv_depth'])
                    merge_matches[arena][game_idx][move_idx]['ave_depth'] = nanmean(merge_matches[arena][game_idx][move_idx]['ave_depth'])
                    merge_matches[arena][game_idx][move_idx]['time_elapsed'] = nanmean(merge_matches[arena][game_idx][move_idx]['time_elapsed'])
                    merge_matches[arena][game_idx][move_idx]['num_nodes'] = nanmean(merge_matches[arena][game_idx][move_idx]['num_nodes'])


    with open(os.path.join(out_dir, f"{kwarg}.pickle"), "wb") as file1:
        pickle.dump(merge_matches, file1)

if __name__ == '__main__':
    with multiprocessing.Pool() as pool:
        pool.map(merge_one, param_configs)
