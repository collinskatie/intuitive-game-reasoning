#!/bin/bash
#SBATCH --time=3:00:00
#SBATCH --mem-per-cpu=8GB
#SBATCH --array=0-49%50
#SBATCH --mail-user=barba@mit.edu
#SBATCH --mail-type=ALL
#SBATCH --output=log/%A_%a.out
#SBATCH --error=log/%A_%a.err
srun hostname
python -u /om2/user/barba/intuitive-game-theory/analysis/surrenders_draws/surrenders.py $SLURM_ARRAY_TASK_ID
