#!/bin/bash
#SBATCH --time=06:00:00
#SBATCH --array=0-447%448
#SBATCH -c 25
#SBATCH --mem-per-cpu=8GB
#SBATCH --mail-user=barba@mit.edu
#SBATCH --mail-type=ALL
#SBATCH --output=log/%A_%a.out
#SBATCH --error=log/%A_%a.err
srun hostname
INTERVAL="14"
python -u /orcd/data/jbt/001/barba/intuitive-game-theory/models/just_think/run_models.py recover $SLURM_ARRAY_TASK_ID $INTERVAL
