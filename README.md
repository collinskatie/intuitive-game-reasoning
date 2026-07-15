# Intuitive game reasoning!

Welcome to the repo for "People use fast and flat simulation to reason about new games" by Katherine M. Collins*, Cedegao E. Zhang*, Lionel Wong*, Mauricio Barba da Costa*, Graham Todd*, Adrian Weller, Samuel J. Cheyette, Thomas L. Griffiths, and Joshua B. Tenenbaum!

This repo hosts the human data as well as model implementations and analyses from our paper https://arxiv.org/abs/2510.11503 


## Installation
To install the required packages, run 
```
uv venv
source .venv/bin/activate
uv sync
```

You can try out a demo of reading data and the Intuitive Gamer model at `demo.ipynb`. A full list of games and summary of "just think" predictions are also included at the end of our Supplement.

## Directory structure

### Human data and experimental interfaces 

**`human-data/`**: Contains data for each human experiment. Participants IDs for participants are removed (as they are only pseudoanonymized) and replaced with unique codes. 

Subdirectories:
- **`think-exp/`**: Judgements from participants from "just thinking" about the game (before any play). 
  - Human judgements in `human_data.csv` (including other details e.g., rxn time, scratchpad data, etc)
  - If you would like a more processed version focused just on judgements, take a look at `analysis/final_processed_res/human_processed.json` (which has keys per game and participant judgements). You can see example loading in `demo.ipyb`

- **`play-exp/`**: Participants played each other live in one match of a set of games
  - Main data: `human-v-human/final_agg.json`
  - See example loading in the final cell of `demo.ipyb`
  - Keys are game variants
  - Each variant then has a series of lists, where each entry is matched to the "arena". 
  - An "arena" refers to one match (between two participants). The same two participants played each other in 6 different matches. 
  - The "boards" key has the move sequences.
  - Extracted post-play funness judgements for some analyses in `analysis` are made more easily accessible in `play_human_fun.json` 

- **`watch-exp/`**: Participants watched others' matches, which were paused at various points and participants predicted outcomes
  - Main data: `final_res.json`
  - See example loading in the final cell of `demo.ipyb`
  - Each key is a participant, and holds their predicted actions at each time step. 
  - See `watch_exp_example_boards.ipynb` for example code visualizing participant (and models') predicted distributions of clicks when watching others play. 

**`human-exp-interfaces/`**: Code for the human experiment interfaces. 
- The `just think` and `watch` experiments both used jsPsych and were run through Pavlovia. 
- The `human-human-play-exp` was run with Empirica.
- If you extend any of the interfaces, make sure to adjust the consent form to your appropriate institutional review board/group (and attain consent!) 

### Model simulations and additional model data 
**`model-data/`**: Saved runs for each agent model, follows similar structure as `human-data` folder
Please download from: https://zenodo.org/records/21348139 and open in the main folder! 
- **`think-exp/`**: Model evaluation data (corresponding to human "just think" experiments)
- **`play-exp/`**: Model gameplay data (distributions over potential next actions)
(note: `heuristics.txt` is the Intuitive Gamer)
- **`intermodel/`**: Inter-model comparison results
- Funness features are also included for the Intuitive Gamer fun model `local_model_readout_fun_features.csv` and alternate models `expert_model_readout_fun_features.csv` (Expert Gamer), `random_model_readout_fun_features.csv` (Random Gamer).

### Stimuli (`stimuli/`)
Contains all games and subsets for particular studies.

**Key files:**
- `cogsci_just_think_stimuli.csv`: Full set of stimuli for the 121 games (board sizes, winning conditions, categories)
- `parsable_stimuli_labels.csv`: Labeled game configurations
- `game2idx.json`: Mapping from games to indices (used in some analyses)
- `updated_final_play_game.csv`: Finalized play experiment games (further subset of the 121)
- `watch_game_stimuli.csv`: Stimuli for watch experiments (further subset of the play-games)

### Models (`models/`)
Contains agent models and utility functions for operating within and over models. 

NOTE: if you are interested in running the Intuitive Gamer or related models more efficiently, we recommend checking out the [Ludax repository](https://github.com/gdrtodd/ludax)! Ludax is a DSL for board games that uses JAX to allow for massive parallelization of environments and search algorithms on the GPU. Reach out to Graham Todd (gdrtodd@gmail.com) from our author team if you need help with setup or implementations.

**Subdirectories:**
- **`agents/`**: Base gameplay agents implementing different strategies:
  - `heuristics.py`: Core heuristic evaluation functions for board states
  - `heuristic_search_eg.py`: Tree-based heuristic search agent with pruning and softmax exploration
  - `mcts.py`: Monte Carlo Tree Search implementation
  - `uni_random.py`: Uniform random agent baseline
  - `additional/`: Other variants

- **`play/`**: Scripts for running intermediate full game simulations
  - `run_models_intermediate_act.py`, `run_models_intermediate_full.py`: Model execution scripts
  - `merge_files.py`, `recover_missing.py`: Data management utilities
  - `shell_scripts/`: Batch execution scripts

- **`just_think/`**: "Think-only" experiments where models evaluate games without playing
  - `run_models.py`: Main execution script
  - `heur_vs_rand.py`: Head-to-head comparisons
  - `shell_scripts/`: Batch processing scripts

- **`intermodel/`**: Inter-model comparison experiments
  - `run_models.py`: Main execution for model vs. model comparisons
  - `heur_vs_rand.py`: Additional strategy comparison utilities
 
### Analysis (`analysis/`)
Contains main files for analyses, e.g., loading and processing human and model data; comparing predictions for payoffs, funness, move selections; R scripts for additional modeling (funness, draw requests). 

**Some example key analysis files:**
- Main paper figures: `figures_think.ipynb` (just-think data), `figures_play_watch.ipynb` (play and watch comparisons), `figures_param_ablations.ipynb` (lesion analyses), `watch_exp_example_boards.ipynb` (Fig 6 showing example boards [and a demonstration of how to visualize predicted distributions over next actions!])
- `explore_variance.ipynb`: simulation sample complexity analyses
- `draw-combined.R`: draw request acceptance/rejection decision modeling
- `play_analyses.ipynb`: Processing play analysis data and running admixture
- `watch_analyses.ipynb`: Processing watch analysis data and running admixture
- `draw_process.ipynb`: Processing draw and surrender data
- `analysis/process_human.ipynb`: Additional processing for human just think data (including scratchpad analyses)
- `post_experience_judgements.ipynb`: analyzing post-experience judgements and other descriptive analyses from play + watch data
- Specific for funness model: 
`cd analysis/funness/`
`Rscript main_funness_model.R` (primary funness model comparisons)
`Rscript generalization_test.R` (comparing funness model from Intuitive Gamer against alternate models)
`Rscript post_play.R` (comparing pre-play [`just think'] and post-play [in human-human play exp])
- `payoff.R`: Non-simulation based payoff modeling
- Processing for ablations of heuristic value function components for think data (`param_fit_novice_think.ipynb`) and for play and watch data (`param_fit_novice_watch_play.ipynb`) 
- Additional files for processing, as well as post-processed cached outputs for analysis visualization, are also included here.

## Contact 

If you have any questions about our code or data, please reach out to Katie Collins (katiemc@mit.edu), Ced Zhang (cedzhang@mit.edu), and/or anyone from our author team!


## Citation 

If you draw on our human data or model code, or are otherwise inspired by our work, please consider citing us! 

[ADD WITH REF!]
