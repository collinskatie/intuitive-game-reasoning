import pathlib
import os

FILE_PATH = pathlib.Path(__file__).parent.resolve()
BASE = os.path.join(FILE_PATH, '..')

ALL_GAMES_PTH = os.path.join(BASE, 'stimuli/parsable_stimuli_labels.csv')
THINK_STIMULI_PTH = os.path.join(BASE, 'stimuli/cogsci_just_think_stimuli.csv')
PLAY_STIMULI_PTH = os.path.join(BASE, 'stimuli/human_human_pilot_stimuli.csv')
PLAY_STIMULI_PTH_FULL = os.path.join(BASE, 'stimuli/updated_final_play_game.csv')


THINK_HUMAN_DATA = os.path.join(BASE, 'human-data/think-exp/human_data.csv')
PLAY_HUMAN_DATA = os.path.join(BASE, 'human-data/play-exp/human-v-human/humanhuman_data.json')
CREATED_GAME_HUMAN_DATA=os.path.join(BASE, "human-data/create-exp/final_create_games.csv")

MODEL2NAME = {"ours": "Ours", 
              "random": "Random (Partial)",
              "random_terminal": "Random (Full)",
              "expert": "Depth-5",
              "expert_mcts": "MCTS",
              "expert_mcts1k": "MCTS (1k)",
              "expert_mcts_sub": "MCTS (Sub, Same Outcomes)",
              "gpt_nocot": "GPT (Zero-Shot)",
              "gpt_cot": "GPT (CoT)",}

THINK_MODEL_DIR = os.path.join(BASE, "model-data/think-exp/")
MODEL2PTH = {
    "think": {
            "ours": f"{THINK_MODEL_DIR}heuristics_results_merged.txt",
            "random": f"{THINK_MODEL_DIR}main_rand_results_400.txt",
             "random_terminal": f"{THINK_MODEL_DIR}main_rand_untilend_results_400.txt",
             "expert": f"{THINK_MODEL_DIR}heuristic_search_results_merged.txt",
            "expert_mcts": f"{THINK_MODEL_DIR}mcts_results_merged.txt",
            "gpt_cot": f"{THINK_MODEL_DIR}llms/gpt_responses_advantage/agg_advantage_True_20240130-2159.json",
             "gpt_nocot": f"{THINK_MODEL_DIR}llms/gpt_responses/agg_advantage_False_20240131-0023.json",
            "gpt_cot_fun": f"{THINK_MODEL_DIR}llms/gpt_responses_fun/agg_how_fun_True_20240130-2253.json",
             "gpt_nocot_fun": f"{THINK_MODEL_DIR}llms/gpt_responses/agg_how_fun_False_20240131-0029.json",
            }

}



PROCESSED_RES_DIR = "final_processed_res/"
FINAL_FIGURES_DIR = "final_figures/"
FIG_DATA_DIR = "fig_data_files/"

PAPER_MODEL2NAME = {
    "ours":              "Intuitive Gamer", # for the just-think, this is partial (for play/watch, full)
    "ours_full":         "Intuitive Gamer", # to termination
    "depth3":            "Intuitive Gamer (Depth-3)",
    "ours-depth3":       "Intuitive Gamer (Depth-3)",
    "random":            "Random",
    "random_terminal":   "Random Gamer",
    "expert":            "Expert Gamer",
    "expert_mcts":       "MCTS",
    "expert_mcts1k":     "MCTS (1k)",
    "expert_mcts_sub":   "MCTS (Sub, Same Outcomes)",
    "gpt_nocot":         "GPT (Direct)",
    "gpt_cot":           "GPT (CoT)",
    "gpt_5":             "GPT-5",
    "deepseek-r1":       "DeepSeek R1",
    "deepseek-v3":       "DeepSeek v3",
    "split-human":       "Split-Halve Human",
    "human":             "Human",
    "temp0-ours":        "Non-Prob",
}

PAPER_AGENT2COLOR = {
    "expert":             "blue",
    "ours":               "red",
    "ours_full":          "red",
    "ours-depth3":        "orange",
    "depth3":             "orange",
    "split-human":        "pink",
    "random":             "grey",
    "random_terminal":    "grey",
    "expert_mcts":        "maroon",
    "opt":                "green",
    "deepseek-r1":        "darkgreen",
    "deepseek-v3":        "teal",
    "gpt_nocot":          "cyan",
    "gpt_cot":            "deepskyblue",
    "llama3170b-vanilla": "brown",
    "llama3170b-cot":     "magenta",
    "gpt-o1":             "olive",
    "gpt-o3":             "teal",
    "gpt-5":              "#A48E16",
    "deepseek-qwen":      "#6A5ACD",
    "temp0-ours":         "purple",
}

PAPER_GAME_TYPE2FMT = {
    "diff-win":            "Second Player \n M-1 to Win",
    "infinity":            "Infinite \n Board",
    "loss":                "M in a Row Loses",
    "no-diag":             "No Diagonal \n Win Allowed",
    "only-diag":           "Only Diagonal \n Win Allowed",
    "player1-2pieces":     "First Player \n Moves 2 Pieces",
    "player1-constraintA": "First Player \n Handicap (A)",
    "player1-constraintB": "First Player \n Handicap (B)",
    "player2-2pieces":     "Second Player \n Moves 2 Pieces",
    "rectangle-board":     "M in a Row\nRectangle",
    "simple-win":          "M in a Row\nSquare",
}

PAPER_ORDER_GAME_TYPES = [
    "M in a Row\nSquare",
    "M in a Row\nRectangle",
    "Infinite \n Board",
    "M in a Row Loses",
    "No Diagonal \n Win Allowed",
    "Only Diagonal \n Win Allowed",
    "First Player \n Moves 2 Pieces",
    "Second Player \n Moves 2 Pieces",
    "First Player \n Handicap (A)",
    "First Player \n Handicap (B)",
    "Second Player \n M-1 to Win",
]
