import sys
import os
import json

if __name__ == '__main__':
    gameplay_data_path = sys.argv[1]
    with open(gameplay_data_path) as f:
        gameplay_data = json.load(f)
    for game in gameplay_data.keys():
        for arena_idx, arena in enumerate(gameplay_data[game]['arena']):
            boards = eval(gameplay_data[game]['boards'][arena_idx])
            if boards: 
                rows, cols = len(boards[0]), len(boards[0][0])
                empty_board = [[0 for _ in range(cols)] for _ in range(rows)]
                boards = [empty_board] + boards
                boards_str = str(boards)
                gameplay_data[game]['boards'][arena_idx] = boards_str
                if 'move_times' in gameplay_data[game].keys():
                    move_times = gameplay_data[game]['move_times'][arena_idx]
                    gameplay_data[game]['move_times'][arena_idx] = [float("nan")] + move_times
    game_keys = list(gameplay_data.keys())
    with open(gameplay_data_path, "w") as f:
        json.dump(gameplay_data, f)