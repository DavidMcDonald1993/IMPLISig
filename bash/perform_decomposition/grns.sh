#!/bin/bash

#SBATCH --job-name=GRNS
#SBATCH --output=GRNS_%A_%a.out
#SBATCH --error=GRNS_%A_%a.err
#SBATCH --array=0-19
#SBATCH --time=05:00:00
#SBATCH --ntasks=1
#SBATCH --mem=1G

grns=(saccharomyces_cerevisiae_cell_cycle schizosaccharomyces_pombe mouse_myeloid_development mammalian_cortical_development arabidopsis_thaliana_development)
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