import os
import pathlib
import multiprocessing
FILE_PATH = pathlib.Path(__file__).parent.resolve()

# INPUTS
model_name = "heuristics"
date = "2025-07-24"
results_dir = os.path.join(FILE_PATH, f"results", date, model_name)
out_dir = os.path.join(FILE_PATH, "merged_results", date, model_name)

param_configs = [kwarg for kwarg in os.listdir(results_dir)]
os.makedirs(out_dir, exist_ok=True)

def merge_one(kwarg):
    merged_files = []
    games_played = os.listdir(os.path.join(results_dir, f"{kwarg}"))
    for game_idx in games_played:
        merge_matches = {}
        matches = os.listdir(os.path.join(results_dir, f"{kwarg}/{game_idx}"))
        for idx, m in enumerate(matches):
            with open(os.path.join(results_dir, f"{kwarg}/{game_idx}/{m}"), "r") as file1:
                contents = file1.read()
            match_info = eval(contents)
            if idx == 0:
                merge_matches = match_info
            else:
                merge_matches['game_scores'] += match_info['game_scores']
                merge_matches['game_lengths'] += match_info['game_lengths']
                merge_matches['all_pv_depths'] += match_info['all_pv_depths']
                merge_matches['all_ave_depths'] += match_info['all_ave_depths']
                merge_matches['time_elapsed'] += match_info['time_elapsed']
                merge_matches['early_stop'] += match_info['early_stop']
                # FIX: Add the missing all_num_nodes merge
                if 'all_num_nodes' in merge_matches:
                    merge_matches['all_num_nodes'] += match_info['all_num_nodes']
        
        if merge_matches:
            merge_matches['draw_percent'] = len(list(filter(lambda x: x == 0, merge_matches["game_scores"])))/len(merge_matches["game_scores"])
            merge_matches['win_percent'] = len(list(filter(lambda x: x == 1, merge_matches["game_scores"])))/len(merge_matches["game_scores"])
            merged_files.append(merge_matches)
    
    with open(os.path.join(out_dir, f"{kwarg}.txt"), "w") as file1:
        file1.write(str(merged_files))

if __name__ == '__main__':
    with multiprocessing.Pool() as pool:
        pool.map(merge_one, param_configs)
