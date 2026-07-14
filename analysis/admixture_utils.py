# helpers for admixture
# previously had one file for play and one for watch (as watch has slightly different objective, given distributional data for the latter)
# merging into a single file ..... but this code could definitely use a refactor if extended to reduce code redundancy!

import models.utils as utils
import models.agents.uni_random as uni_random
import models.agents.heuristics as heuristics
import models.agents.mcts as mcts
import analysis.analysis_utils as analysis_utils
import matplotlib.pylab as plt
import seaborn as sns
import itertools
import pandas as pd
from tqdm import tqdm
from tqdm import trange
import random
import multiprocessing
import datetime
import importlib
from itertools import chain
import constants
import numpy as np
import json
from scipy.optimize import minimize_scalar
from scipy.optimize import minimize
import analysis_utils
import gc


# =============================================================================
# play exp 
# =============================================================================

def score_individ_single_move(move_dists, human_move, alpha=0.95, num_legal=1, apply_softmax=True, temperature=1.0):
    # score a single individual's prediction under model on a single game
    # model_level_dist = move dist for one game/arena
    if apply_softmax:
        move_dists = [analysis_utils.softmax_dist(m, T=temperature) for m in move_dists]
    log_prob_under_model = np.mean([np.log(alpha * m.get(human_move, 0)+(1-alpha)*(1/num_legal)) for m in move_dists])
    return log_prob_under_model

def score_arena(model_data_arena, participant_arena_data, alpha=0.95, apply_softmax=True, temperature=1.0, game_stage='all'):
    tot_score_players = {'X': [], 'O': []}

    # Get total number of moves to determine stage boundaries
    total_moves = len(participant_arena_data)

    mid_move_idx = (total_moves // 2  + 1) - 1 # ---- note: everything is zero-indexed, unlike watch format

    # Filter move indices based on game_stage
    valid_move_indices = []
    if (mid_move_idx <= 3 or ((total_moves-3) <= mid_move_idx)) and not game_stage=='all': # only apply filtering for game stage cases
        return tot_score_players # not long enough -- return empty

    if game_stage == 'all':
        valid_move_indices = list(participant_arena_data.keys())

    elif game_stage == 'early':
        valid_move_indices = [2,3]
    elif game_stage == 'middle':
        valid_move_indices = [mid_move_idx]
    elif game_stage == 'late':
        valid_move_indices = [total_moves-3, total_moves-2]

    # Process only the moves from the requested game stage
    for move_idx in valid_move_indices:

        if move_idx not in participant_arena_data: continue
        h_move, player_id = participant_arena_data[move_idx]
        # number of legal moves left at this stage
        m_dist, num_legal = model_data_arena[move_idx]
        if m_dist is None: continue

        tot_score_players[player_id].append(score_individ_single_move(m_dist, h_move, alpha,
                                                                 num_legal=num_legal,
                                                                 apply_softmax=apply_softmax,
                                                                 temperature=temperature))


    return tot_score_players  # log prob

def score_game(model_data, participant_data, alpha=0.95, arena_subset=None,individ_player_order=None,
               apply_softmax=True,temperature=1.0,game_stage='all', game_name=''):
    # score all (or a subset) of arenas for a single game

    all_individ_scores = []
    individ_arena_player_scores = [] # keep distinction per arena
    arena_ordering = []




    for i, arena in enumerate(participant_data):
        if arena_subset is None or arena in arena_subset:
            tot_score_players = score_arena(model_data[arena],participant_data[arena], alpha=alpha,
                                            apply_softmax=apply_softmax,temperature=temperature,game_stage=game_stage)

            if len(tot_score_players['X']) == 0 and len(tot_score_players['O']) == 0:
                continue # not long enough for game stage

            # if modeling just an indvidual
            # pull out the player's order
            # use that to index into the results to just score that player's moves
            if individ_player_order is not None:
                # filter out the other players' score - we don't need it
                tot_score_players = {individ_player_order: tot_score_players[individ_player_order]}




            individ_arena_player_scores.append([tot_score_players, arena]) # {p1: score, p2: score}

            all_individ_scores.extend(list(tot_score_players.values()))
            arena_ordering.append(arena)

    return all_individ_scores, individ_arena_player_scores, arena_ordering # log prob



def score_model_param(model_data_games, all_participant_data_games, alpha=0.95,
                      arena_subset=None, game_subset=None,participant_play_order=None,apply_softmax=True,
                      temperature=1.0, game_stage='all'):

    all_agg_scores = []
    all_arena_individ_scores = []
    game_ordering = []
    for i, game in enumerate(all_participant_data_games):



        individ_player_order = None
        if participant_play_order is not None:
            # check that the game is in what the player played
            if game not in participant_play_order: continue
            # pull out the player's order
            # use that to index into the results to just score that player's moves
            individ_player_order = participant_play_order[game]


        if game_subset is not None and game not in game_subset:
            #print("skipping: ", game)
            continue
        agg_score, individ_arena_player_scores, arena_ordering = score_game(model_data_games[game],
                               all_participant_data_games[game],
                               alpha=alpha,
                               arena_subset=arena_subset,
                               individ_player_order=individ_player_order,apply_softmax=apply_softmax,
                               temperature=temperature, game_stage=game_stage,
                               game_name=game)


        all_agg_scores.extend(agg_score)
        all_arena_individ_scores.append(individ_arena_player_scores)
        game_ordering.append([game, arena_ordering])

    score = np.mean(sum(all_agg_scores, []))
    return score, all_agg_scores, all_arena_individ_scores, game_ordering

def score_fixed_alpha(param_tag, all_model_data, all_participant_data, alpha=0.95,
                    arena_subset_prop=-1, game_subset_prop=-1,game_id=None, arena_id=None,
                    participant_play_order=None,apply_softmax=True,
                    temperature=1, game_stage='all'):
    model_data = all_model_data[param_tag]

    # subset games and arenas here, if we do subsample at all
    poss_arenas = set()
    poss_games = set()
    for game, game_data in all_participant_data.items():
        poss_arenas.update(set(game_data.keys()))
        poss_games.add(game)

    print("poss games: ", len(poss_games))
    poss_arenas = sorted(list(poss_arenas))
    poss_games = sorted(list(poss_games))
    if arena_id is not None:
        poss_arenas = [arena_id]
    elif arena_subset_prop != -1:
        print("subsampling arenas!")
        # subsample from possible arenas
        poss_arenas = np.random.choice(poss_arenas,
                                       int(arena_subset_prop * len(poss_arenas)),
                                       replace=True)
    if game_id is not None:
        # just consider that game
        poss_games = [game_id]
    elif game_subset_prop != -1:
        # subsample from possible games
        poss_games = np.random.choice(poss_games,
                                       int(game_subset_prop * len(poss_games)),
                                       replace=True)

    print("poss arenas: ", len(poss_arenas))

    return score_model_param(model_data, all_participant_data, alpha=alpha,
                                  arena_subset=poss_arenas, game_subset=poss_games,
                                  participant_play_order=participant_play_order, apply_softmax=apply_softmax,
                                  temperature=temperature, game_stage=game_stage)


def find_best_alpha(param_tag, all_model_data, all_participant_data,
                    arena_subset_prop=-1, game_subset_prop=-1,game_id=None, arena_id=None,
                    participant_play_order=None,apply_softmax=True):
    model_data = all_model_data[param_tag]

    # subset games and arenas here, if we do subsample at all
    poss_arenas = set()
    poss_games = set()
    for game, game_data in all_participant_data.items():
        poss_arenas.update(set(game_data.keys()))
        poss_games.add(game)
    poss_arenas = list(poss_arenas)
    poss_games = list(poss_games)
    if arena_id is not None:
        poss_arenas = [arena_id]
    elif arena_subset_prop != -1:
        # subsample from possible arenas
        poss_arenas = np.random.choice(poss_arenas,
                                       int(arena_subset_prop * len(poss_arenas)),
                                       replace=True)
    if game_id is not None:
        # just consider that game
        poss_games = [game_id]
    elif game_subset_prop != -1:
        # subsample from possible games
        poss_games = np.random.choice(poss_games,
                                       int(game_subset_prop * len(poss_games)),
                                       replace=True)

    def score_alpha(alpha):
        return -score_model_param(model_data, all_participant_data, alpha=alpha,
                                  arena_subset=poss_arenas, game_subset=poss_games,
                                  participant_play_order=participant_play_order, apply_softmax=apply_softmax)[0]
    res = minimize_scalar(score_alpha, bounds=[0.0,1.0], method="Bounded")
    best_alpha = res.x
    best_score = -res.fun
    return best_alpha, best_score


def optimize_alpha(all_model_data, all_participant_data, arena_subset_prop=-1, game_subset_prop=-1, game_id=None,apply_softmax=True):
    opt_results = {}
    for param_tag in all_model_data:
        opt_results[param_tag] = find_best_alpha(param_tag, all_model_data, all_participant_data,
                                                 arena_subset_prop=arena_subset_prop,
                                                 game_subset_prop=game_subset_prop,game_id=game_id,apply_softmax=apply_softmax)

    # get the parameter w/ the highest log likelihood
    param_tags = sorted(all_model_data.keys())
    scores = [opt_results[param_tag][1] for param_tag in param_tags] # b/c dict form = {param_tag: (best_alpha, best_score)}
    best_param = param_tags[np.argmax(scores)]

    return opt_results[best_param], best_param, opt_results




def optimize_alpha_per_individ(all_model_data, all_participant_data, arena_subset_prop=-1, game_subset_prop=-1, game_id=None,
                               participant_id_map={},apply_softmax=True):
    opt_results = {participant_id: {param_tag: {} for param_tag in all_model_data} for participant_id in participant_id_map}
    for param_tag in all_model_data: # model_data = {param_tag: block_dist, ...}
        for participant_id, player_data in participant_id_map.items():
            arena_id = player_data['arena']
            opt_results[participant_id][param_tag] = find_best_alpha(param_tag, all_model_data, all_participant_data,
                                                    arena_subset_prop=arena_subset_prop,
                                                    game_subset_prop=game_subset_prop,
                                                    game_id=game_id,
                                                    arena_id=arena_id,
                                                    participant_play_order=player_data,
                                                    apply_softmax=apply_softmax)

    participant_best ={participant_id: None for participant_id in participant_id_map}
    for participant_id, res in opt_results.items():
        # get the parameter w/ the highest log likelihood
        param_tags = sorted(res.keys())
        scores = [res[param_tag][1] for param_tag in param_tags] # b/c dict form = {param_tag: (best_alpha, best_score)}
        arg_best = np.argmax(scores)
        best_param = param_tags[arg_best]
        best_alpha = res[best_param][0]
        participant_best[participant_id] = [best_param, best_alpha]

    return participant_best, opt_results


def score_individ_single_move_mixture(move_dists, human_move, weights,
                                      num_legal=1, apply_softmax=True,
                                      temperature=1.0, eps_err=1e-12):
    """Score a single move using a mixture of model distributions
    """

    if apply_softmax:
        move_dists = {
            name: [analysis_utils.softmax_dist(m, T=temperature) for m in dists]
            for name, dists in move_dists.items()
        }


    log_probs = []
        # Get probability under each model
    if 'expert' in move_dists:
        n_runs = len(move_dists['expert'])
    else: n_runs = 1

    for run_idx in range(n_runs):
        model_probs = {}
        for name, dist in move_dists.items():
            if name == 'expert':
                dist = dist[run_idx]
            else: dist = dist[0] # b/c all same
            model_probs[name] = dist[human_move] if human_move in dist else 1e-12

        # Add random component
        # print('num legal: ', num_legal)
        model_probs['random'] = 1/num_legal

        # Compute weighted sum
        total_prob = sum(weights[name] * prob for name, prob in model_probs.items())
        try:
            log_probs.append(np.log(total_prob))
        except:
            log_probs.append(np.log(eps_err))
    try:
        agg_score = np.mean(log_probs)
    except:
        agg_score = np.log(eps_err)
    return agg_score


def score_arena_mixture(model_data_arena, participant_arena_data, weights, apply_softmax=True, temperature=1.0):
    """Score all moves in an arena using mixture model"""
    tot_score_players = {'X': 0, 'O': 0}
    individ_scores_players = {}

    for move_idx in participant_arena_data:
        h_move, player_id = participant_arena_data[move_idx]
        model_dists = {}
        for model_name in weights:
            if model_name != 'random':
                m_dist, num_legal = model_data_arena[model_name][move_idx]
                model_dists[model_name] = m_dist

        score = score_individ_single_move_mixture(
            model_dists, h_move, weights,
            num_legal=num_legal, apply_softmax=apply_softmax, temperature=temperature
        )
        tot_score_players[player_id] += score
        individ_scores_players.setdefault(player_id, [])
        individ_scores_players[player_id].append(score)

    return tot_score_players, individ_scores_players

def score_model_mixture(all_model_data, all_participant_data, weights,
                       arena_subset=None, game_subset=None,
                       participant_play_order=None, apply_softmax=True, temperature=1.0):
    """Score mixture model across all games and arenas"""
    all_agg_scores = []
    all_arena_individ_scores = []
    all_individ_logprob_scores = []
    for game in all_participant_data:
        if game_subset is not None and game not in game_subset:
            continue

        individ_player_order = None
        if participant_play_order is not None:
            if game not in participant_play_order:
                continue
            individ_player_order = participant_play_order[game]

        #Restructure model data for this game
        game_model_data = {
            model_name: all_model_data[model_name][game]
            for model_name in weights if model_name != 'random'
        }

        all_scores = []
        arena_scores = []

        individ_scores_logprobs =[]

        for arena in all_participant_data[game]:
            if arena_subset is None or arena in arena_subset:
                scores, individ_scores_players = score_arena_mixture(
                    {name: game_model_data[name][arena] for name in game_model_data},
                    all_participant_data[game][arena],
                    weights,
                    apply_softmax=apply_softmax,temperature=temperature
                )

                if individ_player_order is not None:
                    scores = {individ_player_order: scores[individ_player_order]}

                arena_scores.append([scores, arena])
                all_scores.extend(list(scores.values()))
                individ_scores_logprobs.extend(sum(list(individ_scores_players.values()), [])) # this has move logprobs separately
        all_agg_scores.extend(all_scores)
        all_arena_individ_scores.append(arena_scores)
        all_individ_logprob_scores.extend(individ_scores_logprobs)
    return np.mean(all_agg_scores), np.mean(all_individ_logprob_scores), all_agg_scores, all_arena_individ_scores

def optimize_mixture_weights(all_model_data, all_participant_data, model_names,
                           arena_subset_prop=-1, game_subset_prop=-1,
                           arena_id=None, game_id=None,
                           participant_play_order=None, apply_softmax=True, temperature=1.0):
    """Optimize mixture weights for multiple models plus random"""

    # subset games and arenas here, if we do subsample at all
    poss_arenas = set()
    poss_games = set()
    for game, game_data in all_participant_data.items():
        poss_arenas.update(set(game_data.keys()))
        poss_games.add(game)
    poss_arenas = list(poss_arenas)
    poss_games = list(poss_games)
    if arena_id is not None:
        poss_arenas = [arena_id]
    elif arena_subset_prop != -1:
        # subsample from possible arenas
        poss_arenas = np.random.choice(poss_arenas,
                                       int(arena_subset_prop * len(poss_arenas)),
                                       replace=True)
    if game_id is not None:
        # just consider that game
        poss_games = [game_id]
    elif game_subset_prop != -1:
        # subsample from possible games
        poss_games = np.random.choice(poss_games,
                                       int(game_subset_prop * len(poss_games)),
                                       replace=True)

    def objective(x):
        # Convert optimization vector to weights dict
        weights = {name: x[i] for i, name in enumerate(model_names)}
        weights['random'] = max(1 - sum(x), 0) # Remaining weight goes to random

        score_agg_match, score_agg_individmove, score_per_arena, score_metadata  = score_model_mixture(
            all_model_data, all_participant_data, weights,
            arena_subset=poss_arenas, game_subset=poss_games,
            participant_play_order=participant_play_order,
            apply_softmax=apply_softmax,temperature=temperature
        )
        return -score_agg_individmove

    # Optimize with constraint that weights sum to ≤ 1
    n_weights = len(model_names)
    bounds = [(0, 1)] * n_weights
    # make sure sums to 1
    constraint = {'type': 'ineq', 'fun': lambda x: 1 - sum(x)}

    result = minimize(
        objective,
        x0=np.ones(n_weights) / (n_weights+1),  # start uniform
        bounds=bounds,
        constraints=constraint,
        method='SLSQP'
    )

    # Get final weights including random
    opt_weights = {name: result.x[i] for i, name in enumerate(model_names)}
    opt_weights['random'] = max(1 - sum(result.x), 0)
    return opt_weights, -result.fun


# =============================================================================
# watch+predict exp 
# =============================================================================


def compute_mixture_distribution(move_dists, weights, apply_softmax=True, temperature=1.0, random_dist=None):
    """
    Compute the weighted mixture distribution over models.

    Args:
        move_dists: dict of model_name -> list of dicts of action probabilities
        weights: dict of model_name -> weight (should include 'random' if using random_dist)
        apply_softmax: whether to apply softmax to distributions
        temperature: temperature for softmax
        random_dist: dict of action probabilities for random baseline

    Returns:
        list of dicts of action probabilities (one per run if applicable)
    """
    # Create a copy to avoid modifying input
    move_dists_copy = {name: dists.copy() for name, dists in move_dists.items()}

    # Apply softmax if requested
    if apply_softmax:
        move_dists_copy = {
            name: [analysis_utils.softmax_dist(m, T=temperature) for m in dists]
            for name, dists in move_dists_copy.items()
        }

    # Determine number of runs
    if 'expert' in move_dists_copy:
        n_runs = len(move_dists_copy['expert'])
    else:
        n_runs = 1

    # random separate b/c we don't want to softmax again
    if random_dist is not None:
        move_dists_copy['random'] = [random_dist] * n_runs  # Replicate for each run

    mixture_dists = []
    for run_idx in range(n_runs):
        mix_dist = {}

        # Combine distributions with weights
        for name, dists in move_dists_copy.items():
            # Get the appropriate distribution for this run
            if name == 'expert':
                dist = dists[run_idx]
            else:
                # For non-expert models, use first distribution or run_idx if available
                dist_idx = min(run_idx, len(dists) - 1)
                dist = dists[dist_idx]

            # Add weighted probabilities
            weight = weights[name]
            for action, prob in dist.items():
                # add to mixture
                mix_dist[action] = mix_dist.get(action, 0.0) + weight * prob

        mixture_dists.append(mix_dist)

    return mixture_dists


# Alternative version with explicit weight normalization
def compute_mixture_distribution_normalized(move_dists, weights, apply_softmax=True, temperature=1.0, random_dist=None):
    """
    Version that explicitly normalizes weights to sum to 1.
    """
    # we know weights sum to 1 so sums to 1 by default
    # correct just in case not
    total_weight = sum(weights.values())
    if total_weight <= 0:
        raise ValueError("Total weight must be positive")

    normalized_weights = {k: v / total_weight for k, v in weights.items()}

    return compute_mixture_distribution(move_dists, normalized_weights, apply_softmax, temperature, random_dist)

def score_mixture_log_likelihood(human_dist, mixture_dist,
                                 eps=1e-12
                                 ):
    """
    Compute cross-entropy (negative log-likelihood) of human distribution under the mixture.
    """
    #return analysis_utils.get_tv(human_dist, mixture_dist, alpha=0.999999) #-sum(human_dist[a] * np.log(mixture_dist.get(a, eps)) for a in human_dist)
    return analysis_utils.get_jsd(human_dist, mixture_dist, alpha=0.999999) # use JSD b/c more smoother wrt differentiation?

def score_individ_single_move_mixture_likelihood(move_dists, human_dist, weights,
                                                 apply_softmax=True, temperature=1.0,random_dist={}):
    """
    Compute average negative log-likelihood of human distribution under mixture distribution.
    """
    mixture_dists = compute_mixture_distribution_normalized(move_dists, weights, apply_softmax, temperature,random_dist)
    scores = [score_mixture_log_likelihood(human_dist, mix_dist) for mix_dist in mixture_dists]
    return np.mean(scores)

def score_arena_mixture_watch(model_data_arena, participant_arena_data, weights, apply_softmax=True, temperature=1.0):
    """Score all moves in an arena using mixture model"""
    tot_score_players = {'X': 0, 'O': 0}
    individ_scores_players = {}
    for move_idx in participant_arena_data:
        player_id = 'X' # set rel to
        human_dist = participant_arena_data[move_idx]
        model_dists = {}
        for model_name in weights:
            if model_name != 'random':
                m_dist = model_data_arena[model_name][move_idx]

                model_dists[model_name] = m_dist

        score = score_individ_single_move_mixture_likelihood(
            model_dists, human_dist, weights,
           # num_legal=num_legal,
            apply_softmax=apply_softmax, temperature=temperature,
            random_dist = model_data_arena['random'][move_idx][0] # only one
        )
        tot_score_players[player_id] += score
        individ_scores_players.setdefault(player_id, [])
        individ_scores_players[player_id].append(score)

    return tot_score_players, individ_scores_players

def score_model_mixture_watch(all_model_data, all_participant_data, weights,
                       arena_subset=None, game_subset=None,
                       participant_play_order=None, apply_softmax=True, temperature=1.0):
    """Score mixture model across all games and arenas"""
    all_agg_scores = []
    all_arena_individ_scores = []
    all_individ_logprob_scores = []
    for game in all_participant_data:
        if game_subset is not None and game not in game_subset:
            #print("game subset skip")
            continue

        individ_player_order = None
        if participant_play_order is not None:
            if game not in participant_play_order:
                print("participant play order skip")
                continue
            individ_player_order = participant_play_order[game]

        #Restructure model data for this game
        game_model_data = {
            model_name: all_model_data[model_name][game]
            for model_name in weights 
        }

        all_scores = []
        arena_scores = []

        individ_scores_logprobs =[]

        for arena in all_participant_data[game]:
            if arena_subset is None or arena in arena_subset:
                scores, individ_scores_players = score_arena_mixture_watch(
                    {name: game_model_data[name][arena] for name in game_model_data},
                    all_participant_data[game][arena],
                    weights,
                    apply_softmax=apply_softmax,temperature=temperature
                )

                if individ_player_order is not None:
                    scores = {individ_player_order: scores[individ_player_order]}

                arena_scores.append([scores, arena])
                all_scores.extend(list(scores.values()))
                individ_scores_logprobs.extend(sum(list(individ_scores_players.values()), [])) # this has move logprobs separately
        all_agg_scores.extend(all_scores)
        all_arena_individ_scores.append(arena_scores)

        # individ_scores_logprobs is 12 for watch (4 arenas x 3 stages)
        all_individ_logprob_scores.extend(individ_scores_logprobs)

        if str(np.mean(all_agg_scores)) == 'nan':
           print('ERROR: ', all_agg_scores, individ_player_order)
    return np.mean(all_agg_scores), np.mean(all_individ_logprob_scores), all_agg_scores, all_arena_individ_scores

def optimize_mixture_weights_watch(all_model_data, all_participant_data, model_names,
                           arena_subset_prop=-1, game_subset_prop=-1,
                           arena_id=None, game_id=None,
                           participant_play_order=None, apply_softmax=True, temperature=1.0):
    """Optimize mixture weights for multiple models plus random"""

    # subset games and arenas here, if we do subsample at all
    poss_arenas = set()
    poss_games = set()
    for game, game_data in all_participant_data.items():
        poss_arenas.update(set(game_data.keys()))
        poss_games.add(game)
    poss_arenas = list(poss_arenas)
    poss_games = list(poss_games)
    if arena_id is not None:
        poss_arenas = [arena_id]
    elif arena_subset_prop != -1:
        # subsample from possible arenas
        poss_arenas = np.random.choice(poss_arenas,
                                       int(arena_subset_prop * len(poss_arenas)),
                                       replace=True)
    if game_id is not None:
        # just consider that game
        poss_games = [game_id]
    elif game_subset_prop != -1:
        # subsample from possible games
        poss_games = np.random.choice(poss_games,
                                       int(game_subset_prop * len(poss_games)),
                                       replace=True)

    def objective(x):
        # Convert optimization vector to weights dict
        weights = {name: x[i] for i, name in enumerate(model_names)}
        weights['random'] =  max(1 - sum(x), 0)  # Remaining weight goes to random

        score_agg_match, score_agg_individmove, score_per_arena, score_metadata  = score_model_mixture_watch(
            all_model_data, all_participant_data, weights,
            arena_subset=poss_arenas, game_subset=poss_games,
            participant_play_order=participant_play_order,
            apply_softmax=apply_softmax,temperature=temperature
        )#[0]
        return score_agg_individmove

    # Optimize with constraint that weights sum to ≤ 1
    n_weights = len(model_names)
    bounds = [(0, 1)] * n_weights
    # make sure sums to 1
    constraint = {'type': 'ineq', 'fun': lambda x: 1 - sum(x)}

    result = minimize(
        objective,
        x0=np.ones(n_weights) / (n_weights+1),  # start uniform
        bounds=bounds,
        constraints=constraint,
        method='SLSQP'
    )

    # Get final weights including random
    opt_weights = {name: result.x[i] for i, name in enumerate(model_names)}
    opt_weights['random'] =  max(1 - sum(result.x), 0)
    return opt_weights, -result.fun
