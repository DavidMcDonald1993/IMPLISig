#!/bin/bash

#SBATCH --job-name=CASESTUDY
#SBATCH --output=CASESTUDY_%A_%a.out
#SBATCH --error=CASESTUDY_%A_%a.err
#SBATCH --array=0-5
#SBATCH --time=05:00:00
#SBATCH --ntasks=1
#SBATCH --mem=1G

nets=(gastric egfr tcim)
# modes=("pos neg" "neg pos" "pos" "neg")
modes=("all")
components=("in" "out")

num_nets=${#nets[@]}
num_modes=${#modes[@]}
num_components=${#components[@]}

net_id=$((SLURM_ARRAY_TASK_ID / (num_components * num_modes) % num_nets))
mode_id=$((SLURM_ARRAY_TASK_ID / num_components % num_modes))
component_id=$((SLURM_ARRAY_TASK_ID % num_components))

net=${nets[${net_id}]}
mode=${modes[${mode_id}]}
component=${components[${component_id}]}

edgelist=datasets/${net}/${component}.gml 
output=implisig_output/${net}/${component}
max_loop_size=12

args=$(echo --edgelist ${edgelist} \
    --output ${output} \
    --mode ${mode} \
    --min_loop_size 3 \
    --max_loop_size ${max_loop_size} \
    --undirected)

python implisig/IMPLISig.py ${args}