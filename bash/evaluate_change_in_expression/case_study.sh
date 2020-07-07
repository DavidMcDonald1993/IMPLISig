#!/bin/bash

#SBATCH --job-name=SIGCASESTUDY
#SBATCH --output=SIGCASESTUDY_%A_%a.out
#SBATCH --error=SIGCASESTUDY_%A_%a.err
#SBATCH --array=0-2
#SBATCH --time=05:00:00
#SBATCH --ntasks=1
#SBATCH --mem=1G

datasets=(gastric egfr tcim)

dataset=${datasets[$SLURM_ARRAY_TASK_ID]}

args=$(echo -d expressions/${dataset})

python calculate_expressions/evaluate_change_significance.py ${args}