from datetime import datetime
import pandas as pd
from tqdm import tqdm
from tqdm import trange

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy.stats import pearsonr
import itertools
import json
import os
import re

from PIL import Image
from sklearn.metrics import mean_squared_error
from math import sqrt
from sklearn.linear_model import LinearRegression

import seaborn as sns
import numpy as np
from models.utils import *
try:
    from models.just_think import run_models  
except ImportError:
    run_models = None
from scipy.stats import pearsonr, norm

from scipy.stats import wasserstein_distance
from scipy.stats import entropy
import analysis.constants as constants
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib import animation
import matplotlib.patches as mpatches
from IPython.display import HTML


def process_game_stimuli(game_exp_subset='../stimuli/cogsci_just_think_stimuli.csv'): 
    # load in the raw game format from ced
    df = pd.read_csv(constants.ALL_GAMES_PTH)
    games = []
    for index, row in df.iterrows():
        games.append(row.to_dict())
    # games are ordered with the same index
    
    # now load in the games of interest
    all_games = pd.read_csv(game_exp_subset)

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
        
    game2idx = {v: k for k, v in idx2game.items()}
    return games, idx2game, game2idx, game_stimuli

def process_novice_run_payoff(results, idx2game,n_sim_participants=20, n_simulations=20, bootstrap=False):
    game_sims = {} # key = game id (board_rows*board_cols*win_condition), value are all simulations
    for entry in results:
        game_id = idx2game[entry["index"]]
        s = entry["game_scores"]
        
        if bootstrap: 
            tot_sample = n_sim_participants * n_simulations
            s = list(np.random.choice(s, tot_sample, replace=True))
        
        grouped = by_participants(s ,n=n_sim_participants,m=n_simulations)
        model_samples = map_score_to_judgment(grouped)

        m_payoff= [x['exp_util'] for x in model_samples]
        game_sims[game_id] = m_payoff

    return game_sims

def get_game_categories(human_df): 
    # # pulling out games according to Ced's game categories
    all_game_types = {}
    for i, entry in human_df.iterrows(): 
        game_type = entry.game_types
        game_id = entry.game_id
        if game_type not in all_game_types: all_game_types[game_type] = {game_id}
        else: all_game_types[game_type].add(game_id)
    game2game_type = {}
    for game_type, games_in_type in all_game_types.items():
        for game in games_in_type: 
            game2game_type[game] = game_type
    return all_game_types, game2game_type




def gen_latex_table(game_stats, output_file='game_table.tex'):
    """Generate LaTeX xltabular table from game_stats.
    
    Help from Claude"""

    lines = []
    
    lines.append(r'\begin{xltabular}{\textwidth}{')
    lines.append(r'>{\centering\arraybackslash}p{1.2cm}X>{\centering\arraybackslash}p{0.8cm}>{\centering\arraybackslash}p{0.8cm}>{\centering\arraybackslash}p{1cm}>{\centering\arraybackslash}p{0.8cm}}')
    lines.append(r'\toprule')
    lines.append(r'\textbf{Board} & \textbf{Rules} & \textbf{Fun} & \textbf{Payoff} & \textbf{P(Draw)} & \textbf{P(P1 Wins)} \\')
    lines.append(r'\midrule')
    lines.append(r'\endhead')
    
    for row in game_stats:
        board_fmt, win_conds, agg_fun, payoff, pdraw, pwin = row
        line = f'{board_fmt} & {win_conds} & {agg_fun:.1f} & {payoff:.1f} & {pdraw:.1f} & {pwin:.1f} \\\\'
        lines.append(line)
    
    lines.append(r'\bottomrule')
    lines.append(r'\end{xltabular}')
    
    table_str = '\n'.join(lines)
    
    with open(output_file, 'w') as f:
        f.write(table_str)
    
    return table_str


def tidy_game_code(game):
    base_game_objs, idx2game, game2idx, game_stimuli = process_game_stimuli(constants.THINK_STIMULI_PTH)

    human_df = pd.read_csv(constants.THINK_HUMAN_DATA)
    all_game_types, game2game_type = get_game_categories(human_df)
        
    if 'Inf' in game or 'inf' in game: 
        board_fmt = f'InfxInf'
    else: 
        n_rows, n_cols, win_conds = game.split("*")
        n_rows = int(float(n_rows))
        n_cols = int(float(n_cols))
    
        board_fmt = f'{n_rows}x{n_cols}'
    
    game_type = game2game_type[game]
    game_idx = game2idx[game] - 1 
    game_obj = base_game_objs[game_idx]
    K = game_obj['N']
    
    if game_type == 'diff-win': 
        win_fmt = f'{K} P1 / {K-1} P2'
    else: 
        win_fmt = f'{K}'
        if game_type == 'loss': 
            win_fmt += f' L'
        if game_type == 'only-diag': 
            win_fmt += f' D'
        if game_type == 'no-diag': 
            win_fmt += f' HV'
        if game_type == 'player1-2pieces': 
            win_fmt += f' (P1 2p)'
        if game_type == 'player2-2pieces': 
            win_fmt += f' (P2 2p)'
        if game_type == 'player1-constraintA': 
            win_fmt += f' (P1 HV)'
        if game_type == 'player1-constraintB': 
            win_fmt += f' (P1 D)'

    return f"{board_fmt} {win_fmt}"


def plot_individ_bars(participant_bootstrap_res, agents, filetag, label_x=[False, 'Participants'],main_save='./',
                      sel_temp=None, agent2color={}, model2name={}, incl_plot=True,
                      show_legend=False, ordered_game_ids=None):
    # create  a stacked barchart
    data = []
    entry_id2tot_fit = {}
    
    for entry_id, entries in participant_bootstrap_res.items(): 
        agent_vals = {}
        
        # get aggregate for each agent per person 
        agent_vals = {agent: [] for agent in agents}
        agent_vals['tot_lik'] = []
        
        for temp, results in entries.items(): 
            if sel_temp is not None and temp != sel_temp: continue # only take particular temp vals 
            proportions = results[0][0]
            tot_lik = results[0][-1]
            for agent in agents: 
                agent_vals[agent].append(proportions[agent])
            agent_vals['tot_lik'].append(tot_lik)

            entry_id2tot_fit.setdefault(entry_id, [])
            entry_id2tot_fit[entry_id].append(tot_lik)
           
        
        entry = {
                'entry_id': entry_id,
                'tot_lik': np.mean(agent_vals['tot_lik']),
            }
        for agent in agents: entry[agent] = np.mean(agent_vals[agent])
        data.append(entry)

    df = pd.DataFrame(data)
    if ordered_game_ids is not None:
        ordered_ids_present = [gid for gid in ordered_game_ids if gid in df['entry_id'].values]
        df = df.set_index('entry_id').loc[ordered_ids_present].reset_index()
    else:
        df = df.sort_values('ours', ascending=True)
        ordered_game_ids = df['entry_id']

    if not incl_plot: return df, None
    # Create figure and axis
    if label_x[0]: # then the games -- make even bigger?
        kept_games = len(df)
        if kept_games < 30: 
            height = 7
            width= 18
        else: 
            width = int(kept_games/2)
            height = 6
        fig = plt.figure(figsize=(width, height))
    else: 
        fig = plt.figure(figsize=(15, 6))

    # Create the stacked bar chart
    bottom = np.zeros(len(df))

    for agent in agents: 
        if agent == 'random': continue  # last is random

        plt.bar(range(len(df)), df[agent], bottom=bottom, color=agent2color[agent], label=model2name[agent])
        bottom += df[agent]
    
    plt.bar(range(len(df)), df['random'], bottom=bottom, color=agent2color['random'], label=model2name['random'])
        
    if label_x[0]:
        entry_names =[]
        
        # for game_id in entry.
        for _, entry in df.iterrows():
            game = entry['entry_id']
            game_title_fmt  = tidy_game_code(game)
            entry_names.append(game_title_fmt)

        plt.xticks(range(len(df)), entry_names, rotation=45, ha='right', fontsize=20)

    else:
        plt.xticks([])
    
    # Customize the plot
    xlabel = label_x[-1]
    plt.ylabel('Mixing Weight', fontsize=28)
    if show_legend: 
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=18)

    plt.ylim(0, 1.01)
    plt.yticks(fontsize=18)

    # Add grid for horizontal lines only
    plt.axhline(y=0.5, color='black', linestyle='-', alpha=0.5, linewidth=2)

    plt.tight_layout()
    fig.savefig(main_save + filetag, dpi=400)

    return df, fig, ordered_game_ids

def process_model_runs(model, model_pth, idx2game): 

    try:
        if "gpt" not in model: 
        
            with open(model_pth, 'r') as f:
                contents = f.read()
            results = eval(contents)
            
            game_sims = {} # key = game id (board_rows*board_cols*win_condition), value are all simulations
            for entry in results: 
                idx = entry["index"]
                game_id = idx2game[entry["index"]]
                game_sims[game_id] = entry  
        
        else: 
            if "fun" in model_pth: task = "how_fun"
            else: task="advantage"
            with open(model_pth, "r") as f: 
                raw_gpt_resps = json.load(f)
                
            props = []
            rev_gpt_resps = []
            for game_resps in raw_gpt_resps:
                counts = 0
                rev_resps = []
                resps = game_resps["resps"]
                # remove any cases of CoT where a scratchpad was not generated
                # and remove any cases of zero-shot where a scratchpad was generated
                for r in resps:
                    rev_resps.append(r)
                    if "nocot" in model: 
                        if len(r) > 40: counts += 1 
                        else: 
                            rev_resps.append(r)
                    elif "cot" in model: 
                        if len(r) < 40: counts += 1
                        else: 
                            rev_resps.append(r)
                props.append(counts / len(game_resps["resps"]))
                game_resps["resps"] = rev_resps
                rev_gpt_resps.append(game_resps)

            game_sims = get_game2gpt(rev_gpt_resps,task)
        
        return game_sims
    
    except Exception as e: 
        print("Error loading: ", model, model_pth, " error: ", e)
        return None

def get_stimuli_id(entry, use_expanded=False): 
    n_rows, n_cols = entry["Board size"].split(" x ")
    n_rows = float(n_rows)
    n_cols = float(n_cols)
    if use_expanded: key = 'Winning condition expanded'
    else: key = 'Winning condition'
    return f"{n_rows}*{n_cols}*{entry[key]}"

def convert_board_repr(board, replacement_map= {0: "_", 1: "X", 2: "O"}, invert=False):
    if invert: 
        # str -> number 
        replacement_map = {v: k for k, v in replacement_map.items()}
    return [[replacement_map[value] for value in row] for row in board]

def get_max_keys(d):
    max_value = max(d.values())
    return set([key for key, value in d.items() if value == max_value])

def by_participants(results, m=20, n=20):
    # m: sims
    # n: particiapnts
    assert m * n == len(results)
    return [results[i:i+m] for i in range(0, m*n, m)]

def map_score_to_judgment(results):
    ret_list = []
    for i in range(len(results)):
        p_win = results[i].count(1) / len(results[i])
        p_draw = results[i].count(0) / len(results[i])
        exp_util = p_win - (1 - p_win - p_draw)
        p_lose = 1-(p_win + p_draw)
        outcome_dist = [p_lose, p_win, p_draw]
        ent = compute_entropy(outcome_dist)
        ret_list.append({'p_win': p_win, 'p_draw': p_draw, 'exp_util': exp_util, 'ent': ent})
    return ret_list

def transform(preds):
    return [map_score_to_judgment(by_participants(p)) for p in preds]

def compute_se(vals): 
    return 1.96 * np.std(vals)/(len(vals) ** 0.5)

def compute_ci(vals, alpha=0.05): 
    return float(np.percentile(vals, 100*(alpha/2))), float(np.percentile(vals, 100 * (1 - alpha / 2)))

def compute_se_bars(all_vals): 
    return [compute_se(vals) for vals in all_vals]

def find_board_state(game_data, sel_board): 
    # try to find a particular board configuration in a game -- return the arena name(s) if so 
    # note: game_data should be human_gameplay_data[game]
    # pass board in like: [['_', '_', '_'], ['_', 'X', '_'], ['_', '_', '_']]
    # return empty list if none present
    matched_boards = []
    for arena, boards in zip(game_data['arena'], game_data['boards']):
        boards = eval(boards)
        for i, board in enumerate(boards): 
            board = convert_board_repr(board)
            if board == sel_board: 
                matched_boards.append([arena, i])

    return matched_boards

def compute_utility(draw_resp, win_resp): 
    return (1 - (draw_resp + win_resp)) * (-1) + win_resp

def get_pwin(draw_resp, adv_resp): 
    return ((100 - draw_resp)/100) * (adv_resp/100) * 100

def get_n_win(win_cond):
    return int(win_cond.split(" pieces")[0].split(" ")[-1])

def extract_gpt_resp(resps, task="advantage"): 
    extracted_numbers = []
    for resp in resps:
        try: 
            if task == "advantage": 
                numbers = re.findall(r'RESPONSE-Q[12] = (\d+)', resp)
                q1 = int(numbers[0]) if len(numbers) > 0 and 0 <= int(numbers[0]) <= 100 else None
                q2 = int(numbers[1]) if len(numbers) > 1 and 0 <= int(numbers[1]) <= 100 else None
                if q1 is None or q2 is None: continue
                extracted_numbers.append((q1, q2))
            else: 
                number = int(re.findall(r'RESPONSE = (\d+)', resp)[0])
                if number >= 0 and number <= 100: 
                    extracted_numbers.append(number)
        except: continue

    return extracted_numbers

def get_game2gpt(raw_gpt_resps, task="advantage"):
    game2gpt = {}
    print(len(raw_gpt_resps))
    for entry in raw_gpt_resps: 
        resps = entry["resps"]
        game = entry["game_id"]
        parsed_resps = extract_gpt_resp(resps, task=task)
        n_rows, n_cols, win_cond = game.split("*")
        if "nf" not in n_rows: 
            n_rows = float(n_rows)
            n_cols = float(n_cols)
            # for parity back with the human games
        else: 
            n_rows = "inf"
            n_cols = "inf"
        game_id = f"{n_rows}*{n_cols}*{win_cond}"
        game2gpt[game_id] = parsed_resps
    return game2gpt

def pearsonr_ci(x, y, alpha=0.05):
    # generated from GPT
    # Calculate Pearson correlation
    r, pval = pearsonr(x, y)

    # Fisher z-transformation
    z = np.arctanh(r)
    
    # Standard error of z
    se = 1 / np.sqrt(len(x) - 3)
    
    # Calculate the z critical value for 95% CI
    z_critical = norm.ppf(1 - alpha / 2)
    
    # Calculate the CI in the z-space
    z_ci_lower = z - z_critical * se
    z_ci_upper = z + z_critical * se
    
    # Transform the CI back to the r-space
    r_ci_lower = np.tanh(z_ci_lower)
    r_ci_upper = np.tanh(z_ci_upper)
    
    return r, pval, (r_ci_lower, r_ci_upper)


def epislon_equiv(v1, v2, epsilon=1e-7):
    return abs(v1 - v2) <= epsilon


def draw_colored_grid(num_rows, num_cols, color_map=None, label_map=None):
    if color_map is None:
        color_map = {}
    if label_map is None:
        label_map = {}

    fig, ax = plt.subplots()
    for row in range(num_rows):
        for col in range(num_cols):
            cell_id = (row, col)
            color = color_map.get(cell_id, 'white')
            rect = patches.Rectangle((col, row), 1, 1, linewidth=1, edgecolor='black', facecolor=color)
            ax.add_patch(rect)
            # Add label if present in label_map
            if cell_id in label_map:
                ax.text(col + 0.5, row + 0.5, str(label_map[cell_id] + 1), 
                        ha='center', va='center', fontsize=10, color="white")

    plt.xlim(0, num_cols)
    plt.ylim(0, num_rows)
    ax.set_aspect('equal', adjustable='box')
    plt.gca().invert_yaxis()
    plt.xticks([])
    plt.yticks([])
    fig.tight_layout()

    return fig,ax    

def construct_board(player_move_map, move_order_map, n_rows, n_cols, win_conds, 
                    draw_accepted=None,
                    draw_requests=None,
                    player_colors=None, 
                    player_orders=None,
                    player_judgements=None,
                    game_outcome=None):
    
    if player_colors is None: 
        colors = {1: "blue", 2: "red", 0: "white"}
    else: 
        colors = {order: player_colors[player] for order, player in player_orders.items()}
    
    color_map = {move: colors[player] for move, player in player_move_map.items()}

    if "inf" in str(n_rows) or "inf" in str(n_cols): 
        n_rows = 13
        n_cols=13


    fig, ax = draw_colored_grid(n_rows, n_cols, color_map, move_order_map)

    parsed_win_conds = win_conds.replace(".", ".\n")[:-1]
    title = f"{parsed_win_conds}"
    
    if game_outcome is not None: 
        if player_colors is not None: 
            if game_outcome != "Draw": title += f"\n{player_colors[game_outcome].capitalize()} won"
            else: title+= "\nGame ended in a draw."
    
    if draw_accepted is not None and draw_accepted: title += f"\nEnded from draw request"
    
    if draw_requests is not None: 
        if draw_requests[1] != 0:
            # counter per player
            player_counts = {1: 0, 2: 0}
            # Count occurrences
            for entry in data:
                player = entry[0]
                player_counts[player] += 1
    
    if player_judgements is not None and player_colors is not None:
        for player, color in player_colors.items(): 
            title += f"\n{color.capitalize()} player: {player_judgements[player]}"
                
    ax.set_title(title)#\n{resp}")
    return fig

def format_bold_keys(text):
    try:
        data = json.loads(text)
        formatted_text = ''
        for key, value in data.items():
            formatted_text += f'[B]{key}[/B]: {value}\n'
        return formatted_text
    except json.JSONDecodeError:
        return text
    
def construct_blank_board(size_x=5, size_y=5):
    return [['_'] * size_y for _ in range(size_x)]


def get_pmove(dist, val):
    if val not in dist: return 0
    else: return dist[val]

def get_log_pmove_slop(dist, val, game_dims, alpha=0.8):
    game_size = game_dims[0]*game_dims[1]
    # CHECK the "not in"
    if val not in dist: return np.log(1e-10)#(1-alpha)/game_size)
    else: return np.log(alpha*dist[val]+(1-alpha)/game_size)

def get_acc(dist, val):
    top_moves = list(get_max_keys(dist))
    top_move_idx = np.random.choice(np.arange(len(top_moves)), 1)[0] # check -- how to handle ties?
    top_move = top_moves[top_move_idx]
    return val == top_move

def get_acc_topK(dist, val, K=5, ties="include"):
    """
    Check if `val` is in the top-K keys by value in `dist`, handling ties at the cutoff.
    
    Args:
        dist (dict): Mapping from keys to scores.
        val: The key to check.
        K (int): Number of top items to consider.
        ties (str): 'include' to count all tied at K, 
                    'sample' to randomly sample one from the tied group if needed.
    Returns:
        bool
    """
    if not dist or K <= 0:
        return False

    # Sort items by score descending
    sorted_items = sorted(dist.items(), key=lambda x: x[1], reverse=True)
    N = len(sorted_items)
    if K > N:
        K = N

    # Score at K-th position
    kth_score = sorted_items[K-1][1] if K <= N else sorted_items[-1][1]

    # Keys above K-th (definitely in top-K)
    above_k_keys = [k for k, v in sorted_items if v > kth_score]
    num_above_k = len(above_k_keys)

    # Keys at the K-th score (the tied group)
    tied_keys = [k for k, v in sorted_items if v == kth_score]

    if val in above_k_keys:
        return True  # val is definitely in top-K

    if val in tied_keys:
        if ties == "include":
            return True
        elif ties == "sample":
            # Only sample from the tied group if there are more in the group than available slots
            slots_left = K - num_above_k
            if slots_left <= 0:
                return False
            sampled_keys = random.sample(tied_keys, slots_left)
            return val in sampled_keys
        else:
            raise ValueError("ties must be either 'include' or 'sample'")
        
    return False



def get_rank(dist, item):
    sorted_items = sorted(dist.items(), key=lambda kv: kv[1], reverse=True)
    rank_map = {}
    prev_score = None
    next_rank = 1

    for k, score in sorted_items:
        if score != prev_score:
            current_rank = next_rank
            prev_score = score
            next_rank += 1
        # else: reuse current_rank for ties
        rank_map[k] = current_rank
        
    rank = rank_map.get(item, -1)
    same_rank_counts = np.sum([v == rank for k,v in rank_map.items()])
    
    return rank, same_rank_counts


def get_kl(h_dist, m_dist, alpha=0.8, eps=1e-10):
    num_moves = len(m_dist.keys())
    pk = []
    qk = []
    for k, v in m_dist.items():
        pk.append(alpha*h_dist[k]+(1-alpha)/num_moves if k in h_dist else eps)# (1-alpha)/num_moves)
        qk.append(alpha*v+(1-alpha)/num_moves)
    return entropy(pk=pk, qk=qk)


def get_tv(h_dist, m_dist, alpha=0.8):
    num_moves = len(m_dist.keys())
    res = 0
    for k, v in m_dist.items():
        h_p = h_dist[k]
        m_p = alpha*v+(1-alpha)/num_moves
        res += abs(m_p-h_p)
    return res/2


def get_jsd(h_dist, m_dist, alpha=0.8):
    num_moves = len(m_dist.keys())
    jsd = 0
    
    for k in m_dist.keys(): 
        h_p = h_dist.get(k, 0)
        m_raw = m_dist.get(k, 0)
        m_p = alpha * m_raw + (1-alpha) / num_moves
        
        m = (h_p + m_p) / 2
        
        # Handle edge cases where probabilities are 0
        term1 = h_p * np.log2(h_p / m) if h_p > 0 else 0
        term2 = m_p * np.log2(m_p / m) if m_p > 0 else 0
        
        jsd += (term1 + term2) / 2
        
    return jsd

def process_game_states(boards):
    
    ''' 
    Convert list of boards into move trajectories over time 
    Have the player in each cell and then the move turn on which it was made
    '''
    
    if not boards:
        return []
    
    M = len(boards[0]) # num rows
    N = len(boards[0][0]) # num cols
    K = len(boards) # num moves in the game
    
    result = [[[None for _ in range(N)] for _ in range(M)] for _ in range(K)]
    
    for i in range(K):
        current_board = boards[i]
        prev_board = boards[i-1] if i > 0 else [[0]*N for _ in range(M)]
        
        # compare with previous state to find the move
        for row in range(M):
            for col in range(N):
                if i == 0:
                    result[i][row][col] = (current_board[row][col], 0)
                else:
                    if current_board[row][col] != prev_board[row][col]:
                        result[i][row][col] = (current_board[row][col], i)
                    else:
                        result[i][row][col] = result[i-1][row][col]
                        
    return result


def bootstrapped_mean_ci(data, n_boot=1000, ci=95, random_state=0):
    # special bootstrapping helper for means over diff obj
    rng = np.random.RandomState(random_state)
    boots = [np.mean(rng.choice(data, size=len(data), replace=True)) for _ in range(n_boot)]
    lower = np.percentile(boots, (100 - ci) / 2)
    upper = np.percentile(boots, 100 - (100 - ci) / 2)
    mean = np.mean(data)
    margin = upper - mean  # symmetric if distribution is not skewed
    return mean, margin


def bootstrap_mean_lo_hi(values, n_boot=1000, ci=95, random_state=None):
    """Bootstrap-mean + (lower, upper) CI bounds for a 1D list/array.

    Replaces the inline `for _ in range(n_boot): np.mean(np.random.choice(...))`
    pattern repeated throughout combined_figures_journal. Returns the *mean of
    bootstrap means* (not the sample mean) to match that pattern exactly.

    When ``random_state`` is None, uses the global numpy RNG so an outer
    ``np.random.seed(7)`` flows through; pass an int to make the call
    self-contained.
    """
    rng = np.random.RandomState(random_state) if random_state is not None else np.random
    boots = [np.mean(rng.choice(values, size=len(values), replace=True)) for _ in range(n_boot)]
    lo = float(np.percentile(boots, (100 - ci) / 2))
    hi = float(np.percentile(boots, 100 - (100 - ci) / 2))
    return float(np.mean(boots)), lo, hi


def bootstrap_column_subsample(data, n_boot=1000, subsample_fraction=0.8):
    """Bootstrap a 2D array by sampling columns; return per-row (mean, lo, hi).

    Was originally defined inline in combined_figures_journal cell 11. Lifted
    here so it can be reused as ``analysis_utils.bootstrap_column_subsample``.
    1D inputs are treated as a single row.
    """
    if isinstance(data, list):
        data = np.array(data)
    if data.ndim == 1:
        data = data.reshape(1, -1)

    n_rows, n_cols = data.shape
    n_subsample = int(n_cols * subsample_fraction)
    res = np.zeros((n_rows, n_boot))
    for i in range(n_boot):
        col_indices = np.random.choice(n_cols, size=n_subsample, replace=True)
        res[:, i] = np.mean(data[:, col_indices], axis=1)
    means = np.mean(res, axis=1)
    lower = np.percentile(res, 2.5, axis=1)
    upper = np.percentile(res, 97.5, axis=1)
    return means, lower, upper

def plot_agent_bar_with_ci(agent_stats, agents, agent2color, model2name,
                           ylabel, savepath=None, figsize=(5.5, 6),
                           invert_y=False, hline=None, hline_band=None,
                           csv_path=None):
    """Bar plot of per-agent means with bootstrap CI error bars.

    Captures the cells 24/26/49 pattern in combined_figures_journal.

    Args:
        agent_stats: ``{agent: {'mean': float, 'lower': float, 'upper': float}}``
            (the typical output of ``bootstrap_mean_lo_hi`` called once per agent).
        agents: list of agent keys in the desired left-to-right order.
        agent2color, model2name: shared lookup dicts from the notebook.
        ylabel: y-axis label.
        savepath: optional path to save the figure (PDF/PNG inferred by extension).
        invert_y: invert the y-axis (useful when "lower is better", e.g. log-likelihood).
        hline: optional reference value to draw as a dashed black line.
        hline_band: optional (lo, hi) translucent band around ``hline``
            (e.g. for split-half human CI).
        csv_path: optional path to dump the bar data as CSV for figure-data archival.
    """
    fig = plt.figure(figsize=figsize)
    labels = [model2name[a].replace(" ", "\n") for a in agents]
    means = [agent_stats[a]['mean'] for a in agents]
    colors = [agent2color[a] for a in agents]
    yerr = [
        [max(agent_stats[a]['mean'] - agent_stats[a]['lower'], 0) for a in agents],
        [max(agent_stats[a]['upper'] - agent_stats[a]['mean'], 0) for a in agents],
    ]

    plt.bar(labels, means, color=colors, alpha=0.7, edgecolor='black',
            linewidth=2, width=0.6)
    plt.errorbar(labels, means, yerr=yerr, fmt='none', ecolor='black',
                 capsize=10, linewidth=3)

    if hline_band is not None:
        lo, hi = hline_band
        plt.axhspan(lo, hi, color='black', alpha=0.3, zorder=0)
    if hline is not None:
        plt.axhline(hline, linestyle='--', linewidth=5, alpha=0.7, color='black')

    plt.ylabel(ylabel, fontsize=24)
    plt.tick_params(axis='both', which='major', labelsize=20)
    if invert_y:
        plt.gca().invert_yaxis()
    plt.tight_layout()

    if savepath is not None:
        plt.savefig(savepath, dpi=400)
    if csv_path is not None:
        pd.DataFrame({
            'agents': labels, 'means': means,
            'err_low': yerr[0], 'err_high': yerr[1],
        }).to_csv(csv_path, index=False)
    return fig


def parse_time(timestamp: str) -> float:
    # Note: empirica saves out all the way to nanoseconds! 
    # datetime can't handle that (?) so truncate 
    # Strip the 'Z' at the end of the timestamp
    timestamp = timestamp[:-1]
    # Truncate the nanoseconds to microseconds by slicing the string
    if '.' in timestamp:
        timestamp = timestamp[:timestamp.index('.') + 7]
    # Parse the datetime string
    dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
    # Convert the time to seconds since the epoch
    time_in_seconds = dt.timestamp()
    return time_in_seconds


def tidy_game_name(win_conds):
    # manually tidy some of the longer names
    subcond = "The second player can place 2 pieces as their first move, while the first player can only place 1 piece as their first move."
    subcond2 = "The first player can place 2 pieces as their first move, while the second player can only place 1 piece as their first move."
    win_conds = win_conds.replace(subcond, '\nSecond player plays twice.').replace(subcond2, '\nFirst player plays twice.')
    
    # handle double move
    subcond = "The first player needs 4 pieces in a row to win, but the second player only needs 3 pieces in a row to win."
    subcond2 = "The first player needs 3 pieces in a row to win, but the second player only needs 2 pieces in a row to win."
    win_conds = win_conds.replace(subcond, '\nFirst player needs 4 second player 3 in a row.').replace(subcond2, '\nFirst player needs 3, second player 2 in a row.')
    
    subcond = "However, a player cannot win by making a diagonal row. Only horizontal and vertical rows count."
    subcond2 = "However, a player can only win by making a diagonal row. Horizontal and vertical rows do not count."
    win_conds = win_conds.replace(subcond, '\nNo diagonal win.').replace(subcond2, '\nOnly diagonal allowed.')
    
    subcond = 'The first player can only win by making a diagonal row, but the second player does not have this restriction.'
    subcond2 = 'The second player can only win by making a diagonal row, but the first player does not have this restriction.'
    win_conds = win_conds.replace(subcond, '\nFirst player only diagonal.').replace(subcond2, '\nSecond player only diagonal.')
    
    subcond = 'The first player cannot win by making a diagonal row (only horizontal and vertical rows count), but the second player does not have this restriction.'
    subcond2 = 'The second player cannot win by making a diagonal row (only horizontal and vertical rows count), but the first player does not have this restriction.'
    win_conds = win_conds.replace(subcond, '\nFirst player no diagonal.').replace(subcond2, '\nSecond player no diagonal.')
    
    return win_conds

def create_game_animation(boards, interval=1800, figsize=(8, 8)):
    """
    Create an animation from a series of game boards.
    Help from Claude! 
    
    # Create and display the animation
    animation_html = create_game_animation(processed_boards)
    display(animation_html)
    
    Parameters:
    -----------
    boards : list of 2D arrays
        List of MxN arrays representing game states at each turn
    interval : int, optional
        Delay between frames in milliseconds, default is 1800 (1.8 second, like WJM)
    figsize : tuple, optional
        Figure size, default is (8, 8)
        
    Returns:
    --------
    IPython.display.HTML object containing the animation
    """
    # Convert list of boards to numpy array for easier handling
    boards_array = np.array(boards)
    
    # Number of frames (turns)
    n_frames = boards_array.shape[0]
    
    # Board dimensions
    m, n = boards_array.shape[1], boards_array.shape[2]
    
    # Create custom colormap: 0=white (empty), 1=blue, 2=red
    colors = ['white', 'blue', 'red']
    cmap = ListedColormap(colors)
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=figsize)
    
    # Function to initialize the animation
    def init():
        ax.clear()
        # Set the x and y limits for the plot
        ax.set_xlim(-0.5, n - 0.5)
        ax.set_ylim(-0.5, m - 0.5)
        # Invert y-axis so (0,0) is at the top left
        ax.invert_yaxis()
        return []
    
    # Function to update the animation for each frame
    def update(frame):
        ax.clear()
        
        # Display the board for the current frame
        im = ax.imshow(boards_array[frame], cmap=cmap, vmin=0, vmax=2, 
                       extent=(-0.5, n-0.5, m-0.5, -0.5), interpolation='none')
        
        # Add grid lines - place them at integer positions
        # Vertical lines
        for i in range(n+1):
            ax.axvline(i-0.5, color='black', linewidth=0.5)
        # Horizontal lines
        for i in range(m+1):
            ax.axhline(i-0.5, color='black', linewidth=0.5)
        
        # Set ticks in between grid cells
        ax.set_xticks(np.arange(n))
        ax.set_yticks(np.arange(m))
        
        # Hide tick labels
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        
        # Add title showing the turn number
        ax.set_title(f'Turn {frame}', fontsize=16)
        
        # Create legend
        blue_patch = mpatches.Patch(color='blue', label='Player 1 (Blue)')
        red_patch = mpatches.Patch(color='red', label='Player 2 (Red)')
        ax.legend(handles=[blue_patch, red_patch], loc='upper right', 
                  bbox_to_anchor=(1.1, 1.1))
        
        return [im]
    
    # Create the animation
    anim = animation.FuncAnimation(
        fig, update, frames=n_frames, init_func=init, blit=True, interval=interval
    )
    
    # Close the figure to prevent it from displaying separately
    plt.close(fig)
    
    # Return the animation as HTML for display in the notebook
    return HTML(anim.to_jshtml())

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

def process_game_moves(all_boards): 
    
    all_boards = np.array(eval(all_boards))
    
    n_rows, n_cols = all_boards[0].shape

    player_move_map = {}
    move_order_map = {}

    prev_board = np.zeros([n_rows, n_cols])

    for round, round_board in enumerate(all_boards):
        round_board = np.array(round_board)
        diff = round_board != prev_board  # Find where the boards differ
        row, col = np.where(diff)  # Get the indices of the differences
        row = int(row[0])
        col = int(col[0]) # only one change per turn
        val = int(round_board[row][col])
        player_move_map[(row, col)] = val
        move_order_map[(row, col)] = round
        prev_board = round_board
        
    return player_move_map, move_order_map

def pngs_to_pdf(image_directory='figs/', output_pth="gameplay.pdf", shrink_factor=0.8, quality=85,
                int_sort=True):
    # Convert a directory of PNGs to PDF and shrink images

    # Get a list of all PNG files in the directory
    image_files = [f for f in os.listdir(image_directory) if f.endswith('.png')]

    if int_sort: 
        # if the files are of the form ({int}.png)
        image_ids = [int(f.split(".png")[0]) for f in image_files]
        image_ids.sort()
        image_files = [f'{i}.png' for i in image_ids]
    else: image_files.sort()

    # Load the images
    images = [Image.open(os.path.join(image_directory, f)) for f in image_files]

    # Resize the images by the shrink factor
    resized_images = []
    for img in images:
        new_size = (int(img.width * shrink_factor), int(img.height * shrink_factor))
        resized_img = img.resize(new_size, Image.LANCZOS)
        resized_images.append(resized_img)

    # Convert the images to RGB (if they are not already)
    images_rgb = [img.convert('RGB') for img in resized_images]

    # Save the images as a PDF with specified quality
    images_rgb[0].save(output_pth, save_all=True, append_images=images_rgb[1:], quality=quality, optimize=True)

def prolific2standardboard(board):
    transformed = [["_" for _ in board[0]] for _ in board]
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 1:
                transformed[i][j] = "X"
            elif board[i][j] == 2:
                transformed[i][j] = "O"
    return transformed


def opt_game_outcome_mnk(m, n, k):
    """
    From: https://ieee-cog.org/2019/papers/paper_115.pdf
    Modified from Claude
    Determine the outcome of a k-in-a-row game on an m×n board.
    
    Args:
        m (int): Number of rows on the board
        n (int): Number of columns on the board
        k (int): Number of consecutive pieces needed to win
    
    Returns:
        1 (P1 wins), 0 ('draw'), or -1 (P2 wins)
    """
    
    if k >= 3 and (m < k or n < k):
        return 0
    
    # Strong 4-in-a-Row results from the paper
    if k == 4:
        # 5×5 board is a draw
        if m == 5 and n == 5:
            return 0
        
        # 5×6 board or larger with at least one dimension > 5 is a first-player win
        if m >= 5 and n >= 6:
            return 1
            
        if n >= 5 and m >= 6:
            return 1
        
        # # 4×n boards where n ≤ 8 are draws
        # if m == 4 and n <= 8:
        #     return 0
        # We can extend the above further
        if m <= 4 and n <= 8:
            return 0

        # By symmetry, n×4 boards follow the same pattern
        if n <= 4 and m <= 8:
            return 0
        
        # 4×n boards where n ≥ 9 are first-player wins
        if m == 4 and n >= 9:
            return 1

        if n == 4 and m >= 9:
            return 1
        
    if m == 10 and n == 10: 
        if k <= 4: 
            return 1
        elif k >= 8:
            return 0 
        
    return None




def view_table_nb(dist, board, player, move=None, fig=None, ax=None, vmin=0, vmax=1, with_text=True,
                  no_dist_color=False, cmap='plasma', text_xoffset=0, text_yoffset=0.05, add_colorbar=True):  
    """
    View statistics of search algorithm in a Python notebook with color coding.
    
    Parameters:
    -----------
    dist : dict
        Dictionary mapping positions (row, col) to probability values
    board : list of lists
        The current game board with 'X', 'O', and '_' for empty cells
    player : str
        Current player ('X' or 'O')
    move : tuple, optional
        Highlight this move position (row, col)
    fig, ax : matplotlib figure and axes, optional
        If provided, plot on these axes
    vmin, vmax : float
        Min and max values for colormap scaling
    with_text : bool
        Whether to display text values on cells
        
    Returns:
    --------
    fig, ax : The figure and axes objects
    """
    # Create a new board with probability values
    new_board = np.full((len(board), len(board[0])), np.nan)
    
    if dist is not None:
        agg_vals = 0
        for pos, val in dist.items():
            new_board[pos[0]][pos[1]] = float(val)
            agg_vals += float(val) 
    
    # Create figure and axes if not provided
    if fig is None and ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))
    
    # Create a mask for the board values (player positions)
    board_colors = np.full_like(new_board, np.nan)
    for ri in range(len(board)):
        for ci in range(len(board[0])):
            if board[ri][ci] == "X":
                board_colors[ri][ci] = 1  # X positions
            elif board[ri][ci] == "O":
                board_colors[ri][ci] = 2  # O positions
            else:
                # Don't assign default value so background shows through
                continue
    
    # Create a colormap
    base_cmap = plt.cm.get_cmap(cmap) 
    custom_cmap = base_cmap
    
    # Set bad value color to white (this will be used for non-empty cells)
    custom_cmap.set_bad('white')

    # Prepare data for visualization with masked array
    default_board = np.zeros_like(new_board)
    mask = np.ones_like(new_board, dtype=bool)  # Start with all cells masked

    for ri in range(len(board)):
        for ci in range(len(board[0])):
            if board[ri][ci] == "_":
                if (ri, ci) in dist:
                    prob = dist[(ri, ci)]
                    if no_dist_color and prob != 1:
                        continue 

                    default_board[ri][ci] = dist[(ri, ci)]
                    mask[ri][ci] = False  # Unmask cells that should show color
                    
    # Apply the mask to create a masked array
    masked_data = np.ma.array(default_board, mask=mask)

    # Plot the masked data (this will show colors only for empty cells with values)
    heatmap = ax.imshow(masked_data, cmap=custom_cmap, vmin=vmin, vmax=vmax)
    
    # Add colorbar
    if add_colorbar:
        cbar = fig.colorbar(heatmap)    
    
    # Add text to cells
    for ri in range(len(board)):
        for ci in range(len(board[0])):
            if np.isnan(new_board[ri][ci]):
                board_score = ""
            else:
                board_score = str(round(new_board[ri][ci], 2))
                
            if board[ri][ci] != "_":
                board_txt = board[ri][ci]  # Just show X or O
                text_color = "black"  # Use black text for X and O on white background
            elif (move is not None and (move[0] == ri and move[1] == ci)):
                board_txt = board_score + f"\n{board[ri][ci]}"
                text_color = "black"  # Use black text for probability values
            else:
                board_txt = board_score  # Just show the probability
                text_color = "black"  # Use black text for probability values
            
            if board[ri][ci] in ["X", "O"] or with_text:
                # ax.text(ci, ri, ...) follows matplotlib's convention where the first param is x-coord (col) 
                # and the second is the y-coord (row).
                ax.text(ci+text_xoffset, ri+text_yoffset, board_txt, ha="center", va="center", 
                        color=text_color, fontsize=12, fontweight='bold')
                
            # for the case of no_dist then overlay the played player
            if no_dist_color and board[ri][ci] == "_": 
                if (ri, ci) in dist:
                    prob = dist[(ri, ci)]
                    if prob == 1: 
                        text_color = "black"
                        # played move, overlay the player 
                        ax.text(ci+text_xoffset, ri+text_yoffset, player, ha="center", va="center", 
                        color=text_color, fontsize=12, fontweight='bold')
    
    # Remove ticks
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Add grid lines
    for i in range(1, len(board)):
        ax.axhline(i - 0.5, color='black', linestyle='-', linewidth=1)

    for i in range(1, len(board[0])):
        ax.axvline(i - 0.51, color='black', linestyle='-', linewidth=1)
    
    return fig, ax
