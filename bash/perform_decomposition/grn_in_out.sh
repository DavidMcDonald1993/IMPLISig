#!/bin/bash

#SBATCH --job-name=GRNS
#SBATCH --output=GRNS_%A_%a.out
#SBATCH --error=GRNS_%A_%a.err
#SBATCH --array=0-11
#SBATCH --time=05:00:00
#SBATCH --ntasks=1
#SBATCH --mem=1G

grns=(creb mouse_myeloid_development schizosaccharomyces_pombe saccharomyces_cerevisiae_cell_cycle mammalian_cortical_development arabidopsis_thaliana_development)
# modes=("pos neg" "neg pos" "pos" "neg")
modes=("all")
components=("in" "out")

num_grns=${#grns[@]}
num_modes=${#modes[@]}
num_components=${#components[@]}

grn_id=$((SLURM_ARRAY_TASK_ID / (num_components * num_modes) % num_grns))
mode_id=$((SLURM_ARRAY_TASK_ID / num_components % num_modes))
component_id=$((SLURM_ARRAY_TASK_ID % num_components))

grn=${grns[${grn_id}]}
mode=${modes[${mode_id}]}
component=${components[${component_id}]}


edgelist=datasets/${grn}/${component}.gml 
output=implisig_output/${grn}/${component}
max_loop_size=12

args=$(echo --edgelist ${edgelist} \
    --output ${output} \
    --mode ${mode} \
    --min_loop_size 3 \
    --max_loop_size ${max_loop_size} \
    --undirected
    )

python implisig/IMPLISig.py ${args}