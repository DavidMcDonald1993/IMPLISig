#!/bin/bash

#SBATCH --job-name=CASESTUDY
#SBATCH --output=CASESTUDY_%A_%a.out
#SBATCH --error=CASESTUDY_%A_%a.err
#SBATCH --array=0-7
#SBATCH --time=05:00:00
#SBATCH --ntasks=1
#SBATCH --mem=1G

# nets=(gastric egfr tcim)
nets=(bladder liver)
modes=("pos neg" "neg pos" "pos" "neg")

num_nets=${#nets[@]}
num_modes=${#modes[@]}

net_id=$((SLURM_ARRAY_TASK_ID / num_modes % num_nets))
mode_id=$((SLURM_ARRAY_TASK_ID % num_modes))

net=${nets[${net_id}]}
mode=${modes[${mode_id}]}

edgelist=datasets/${net}/edgelist.tsv 
output=implisig_output/${net}
modes=mode
max_loop_size=12

args=$(echo --edgelist ${edgelist} \
    --output ${output} \
    --mode ${mode} \
    --max_loop_size ${max_loop_size} \
    --draw)

python implisig/IMPLISig.py ${args}