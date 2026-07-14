#!/bin/bash
#SBATCH --mail-user=barba@mit.edu
#SBATCH --mail-type=ALL
#SBATCH --output=log/%A_%a.out
#SBATCH --error=log/%A_%a.err
srun hostname
python -u /orcd/data/jbt/001/barba/intuitive-game-theory/models/just_think/merge_files.py
