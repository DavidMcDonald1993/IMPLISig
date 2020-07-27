#!/bin/bash

#SBATCH --job-name=EXPCASESTUDY
#SBATCH --output=EXPCASESTUDY_%A_%a.out
#SBATCH --error=EXPCASESTUDY_%A_%a.err
#SBATCH --array=3-4
#SBATCH --time=05:00:00
#SBATCH --ntasks=1
#SBATCH --mem=1G

all_datasets=(egfr gastric tcim bladder liver)
all_output_nodes=("elk1 creb ap1 cmyc p70s6_2 hsp27 pro_apoptotic" \
    "Caspase8 Caspase9 FOXO RSK TCF cMYC" \
    "Apoptosis CellCycleArrest Metastasis" \
    "Proliferation Apoptosis_b1 Apoptosis_b2 Growth_Arrest" \
    "BAD Myc CyclinD1 MCL_1 BIM p27Kip1"
    )
all_control_modification=("erbb11" "" "" "" "")

dataset=${all_datasets[$SLURM_ARRAY_TASK_ID]}
output_nodes=${all_output_nodes[$SLURM_ARRAY_TASK_ID]}
control_modification=${all_control_modification[$SLURM_ARRAY_TASK_ID]}

output_dir=expressions/${dataset}

args=$(echo "--edgelist datasets/${dataset}/edgelist.tsv 
    --output ${output_dir}
    --primes datasets/${dataset}/network.json 
    --control_modification ${control_modification} 
    --output_nodes ${output_nodes}
    ")

python calculate_expressions/calculate_expressions.py ${args}