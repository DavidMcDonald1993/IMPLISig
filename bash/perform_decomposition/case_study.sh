#!/bin/bash

#SBATCH --job-name=CASESTUDY
#SBATCH --output=CASESTUDY_%A_%a.out
#SBATCH --error=CASESTUDY_%A_%a.err
#SBATCH --array=0-11
#SBATCH --time=05:00:00
#SBATCH --ntasks=1
#SBATCH --mem=1G

grns=(gastric egfr tcim)
modes=("pos neg" "pos" "neg" "all")

num_grns=${#grns[@]}
num_modes=${#modes[@]}

grn_id=$((SLURM_ARRAY_TASK_ID / num_modes % num_grns))
mode_id=$((SLURM_ARRAY_TASK_ID % num_modes))

grn=${grns[${grn_id}]}
mode=${modes[${mode_id}]}

edgelist=datasets/${grn}/edgelist.tsv 
output=implisig_output/${grn}
modes=mode
max_loop_size=12

args=$(echo --edgelist ${edgelist} \
    --output ${output} \
    --mode ${mode} \
    --max_loop_size ${max_loop_size} \
    --draw)

python implisig/IMPLISig.py ${args}