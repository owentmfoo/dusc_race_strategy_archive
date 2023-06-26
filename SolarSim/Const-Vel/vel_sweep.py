import sys, os
sys.path.append('/ddn/home/wqpq24')
import S5.HPC.SolarSim as SS
import S5.HPC.file_io as io
import multiprocessing as mp
import numpy as np

sys.path.append(os.getcwd())

t = np.datetime64("now")


print(mp.cpu_count())
vel = [i for i in range(60,80)]
SS.vel_sweep_par(vel,'../SolarSim.X')
print(f'All calculations completed in {str(np.datetime64("now") - t)}, time now is {str(np.datetime64("now"))}.')

