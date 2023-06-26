#!/bin/csh

#SBATCH  -o  SS.out
#SBATCH  -e  SS.err

#SBATCH -J SolarSimVelSweep

#SBATCH  --mail-type=ALL
#SBATCH  --mail-user  tsz.m.foo@durham.ac.uk

#############################################################################

## This job requests number_of_tasks MPI tasks (without OpenMP)

#SBATCH  -N 1

# Request submission to a queue (partition) for parallel jobs

#SBATCH  -p par7.q


module purge
module load slurm/current
module load python/3.6.8
## Load any modules required here

## Execute the MPI program

python3 -u vel_sweep.py
