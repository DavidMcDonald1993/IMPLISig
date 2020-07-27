#!/bin/bash

#SBATCH --job-name=EXPSYNTH
#SBATCH --output=EXPSYNTH_%A_%a.out
#SBATCH --error=EXPSYNTH_%A_%a.err
#SBATCH --array=9000-11999
#SBATCH --time=05:00:00
#SBATCH --ntasks=1
#SBATCH --mem=1G

# module purge
# module load bluebear
# module load bear-apps/2019a
# module load Python/3.7.2-GCCcore-8.2.0

# pip install --user numpy networkx pandas PyBoolNet
num_cores=(6 10 15 30)
seeds=({000..999})
feedback_loops=(pos_neg pos neg)

n_cores=${#num_cores[@]}
n_seeds=${#seeds[@]}
n_feedback_loops=${#feedback_loops[@]}

core_id=$((SLURM_ARRAY_TASK_ID / (n_seeds * n_feedback_loops)  % n_cores))
seed_id=$((SLURM_ARRAY_TASK_ID / n_feedback_loops % n_seeds))
loop_id=$((SLURM_ARRAY_TASK_ID % n_feedback_loops))

num_core=${num_cores[$core_id]}
seed=${seeds[$seed_id]}
loop=${feedback_loops[$loop_id]}

num_in=3

output_dir=expressions/synthetic_bow_tie/${num_core}/${seed}/${loop}
output_nodes="all"

if [ ! -f ${output_dir}/n$((num_in+num_core))_expressions.csv.gz ]
then
    args=$(echo "--edgelist synthetic_bow_tie/${num_core}/${seed}/${loop}/edgelist.tsv 
    --output ${output_dir}
    --primes synthetic_bow_tie/${num_core}/${seed}/${loop}/network.bnet 
    --output_nodes ${output_nodes}
    --control_modification ''
    ")

    python calculate_expressions/calculate_expressions.py ${args} 
fi