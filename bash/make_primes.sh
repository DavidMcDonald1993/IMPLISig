#!/bin/bash

#SBATCH --job-name=CREBPRIMES
#SBATCH --output=CREBPRIMES_%A_%a.out
#SBATCH --error=CREBPRIMES_%A_%a.err
#SBATCH --time=10-00:00:00
#SBATCH --ntasks=1
#SBATCH --mem=50G

module purge
module load bluebear

module load bear-apps/2020a
module load Python/3.8.2-GCCcore-9.3.0

pip install --user numpy pandas networkx 
pip install --user PyBoolNet-2.2.8_linux64.tar.gz

ulimit -c 0
python get_primes.py