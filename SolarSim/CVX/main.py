#!/bin/python3
from scipy.optimize import minimize, Bounds
import numpy as np
import time
import sys
import matplotlib.pyplot as plt
from shutil import copyfile as rename

sys.path.append('E:\solar_car_race_strategy\S5')
sys.path.append('/ddn/home/wqpq24')
import S5.Tecplot as TP
from S5.HPC.file_io import write_vel, read_history,adjust_v
from S5.HPC.SolarSim import file_sweep, read_file_sweep, file_sweep_par, run_ss
from S5.HPC.optimisation import calc_strat,set_mean

strat_files = [
    '../IsolatedOptimisation//tvel_grad8.dat',
    '../IsolatedOptimisation//tvel_SI8.dat',
    '../IsolatedOptimisation//tvel_TI8.dat',
    '../IsolatedOptimisation//tvel_yaw8.dat',
    '../IsolatedOptimisation//tvel_hw8.dat'
]


def optim_fun(x, strat_files, v_bar):
    # SS = '../SolarSim.X'
    SS = '../SolarSim4.1.exe'
    metric = np.zeros(len(strat_files))
    for i,f in enumerate(strat_files):
        stratTP = TP.TecplotData(f)
        v_primei = calc_strat(stratTP.data['TargetVel (km/h)'], x[i], 0, stratTP.data['Distance (km)'])
        try:
            v_prime += v_primei
        except NameError:
            v_prime = v_primei

    # stratTP.data.loc[:, 'TargetVel (km/h)'] = v_prime + v_bar    
    # adjust_v(stratTP, v_bar)
    tvel = set_mean(v_prime,v_bar,stratTP.data['Distance (km)'],8,clip="kph")
    stratTP.data.loc[:, 'TargetVel (km/h)'] = tvel
    stratTP.write_tecplot('TargetVel.dat')

    run_ss(SS, 'SolarSim.in', 'Summary.dat', 'History.dat', 'SolarTotals.dat')
    driving_time, dist, SoC, avg_vel, Vstd, SoCMax, SoCMin = read_history(histfile='History.dat')

    # set up panelty function and consider 100 SoCMax, 0 SoCMin, mismatch of avg_vel as annoyance
    costfun = -SoC
    if SoCMax > 98:
        costfun += SoCMax - 98 # Deadzone linear
    if SoCMin < 5: #log barrier inf at SoCmin = 1
        u = 5-abs(SoCMin)
        if u < 4:
            costfun += 16*np.log(1-(u/4)**2)
        else:
            costfun += 100
    if dist < 3010:
        costfun += 1000
    if abs(avg_vel-v_bar) >3: # significantly faster or slower than it should be
            costfun += abs(avg_vel-v_bar)*1000

    print(f'{x}:\nMin:{SoCMin:.4}\tEnd:{SoC:.4}\tMax:{SoCMax:.4}\tCostFunction:{costfun:.4}')
    print(f'Driving Time:{round(driving_time)}\tAverage Velocity:{avg_vel:.4}\tVstd:{Vstd:.4}')
    # return cost function
    return costfun


x0 = np.array([0,0,0,0,0])
bd = Bounds(-5 * np.ones(len(x0)), 5 * np.ones(len(x0)))
v_bar = 73

o1 = minimize(fun=optim_fun, x0=x0, args=(strat_files, v_bar), bounds=bd,options={'eps':1,'ftol':0.001},method = 'L-BFGS-B')

print('='*25)
print(o1)
print(f'{o1.x}')
print('\n\n')
x0 = o1.x

optim_fun(o1.x,strat_files,v_bar)
