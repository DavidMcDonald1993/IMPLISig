#!/bin/bash

#SBATCH --job-name=SYNTHETIC
#SBATCH --output=SYNTHETIC_%A_%a.out
#SBATCH --error=SYNTHETIC_%A_%a.err
#SBATCH --array=0-2
#SBATCH --time=05:00:00
#SBATCH --ntasks=1
#SBATCH --mem=1G

num_cores=(6 10 15)
num_core=${num_cores[$SLURM_ARRAY_TASK_ID]}

num_in=10 
num_out=10 
max_in_connections=3
num_input_nodes=${num_in}
num_output_nodes=${num_out}

args=$(echo --num_in ${num_in} \
    --num_core ${num_core} \
    --num_out ${num_out} \
    --max_in_connections ${max_in_connections} \
    --num_input_nodes ${num_input_nodes} \
    --num_output_nodes ${num_output_nodes} \
    --root_directory synthetic_bow_tie/${num_core} )

python generate_synthetic_bow_tie.py ${args}