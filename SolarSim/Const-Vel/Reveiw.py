#!/bin/env/python3
import sys, os

sys.path.append('E:\solar_car_race_strategy\S5')
sys.path.append('/ddn/home/wqpq24')
import S5.HPC.SolarSim as SS
import numpy as np
import matplotlib.pyplot as plt

import matplotlib
matplotlib.rcParams.update({
    'font.family': 'serif',
    'font.size':8,
})
plt.rcParams.update({'font.serif':'Times New Roman'})



cmap = plt.get_cmap("tab10").colors
winter = plt.get_cmap("viridis")
winter = winter(np.linspace(0,1,4))
vel = np.linspace(60,80,81)
Sweep = SS.read_vel_sweep(vel,'.')


fig, axs = plt.subplots(13, 1, sharex=True)


gs = axs[0].get_gridspec()
for ax in axs[:]:
    ax.remove()
Vel = fig.add_subplot(gs[0:4])
SoC = fig.add_subplot(gs[4:])


Vel.plot(Sweep['tVel'], Sweep['AverageVel'],c=cmap[1], label="Average Velocity")
Vel.set_ylabel('Average\nVelocity (km/h)')
Vel.xaxis.set_visible(False)



SoC.plot(Sweep['tVel'], [80]*Sweep.shape[0],c=winter[0], label="Starting",lw=1)
SoC.plot(Sweep['tVel'], Sweep['SoC'],c=winter[1], label="Ending",lw=1)
SoC.plot(Sweep['tVel'], Sweep['SoCMax'],c=winter[2], label="Max",lw=1)
SoC.plot(Sweep['tVel'], Sweep['SoCMin'],c=winter[3], label="Min",lw=1)

SoC.set_ylabel('SoC (\%)')
SoC.set_xlabel('Target Velocity (km/h)')
SoC.xaxis.set_ticks(np.linspace(60,80,11))
lgd = SoC.legend(ncol=2)

SoC.set_ylim(0, 100)  # most of the data
Vel.set_xlim([min(vel),max(vel)])
SoC.set_xlim([min(vel),max(vel)])
fig.set_size_inches(7.16,2)

fig.subplots_adjust(bottom=0.2,hspace=0.5,right=0.99,left=0.1)
fig.tight_layout()
fig.show()

fig.savefig('E:\\solar_car_race_strategy\\Report\\ConstVelSweep.eps')
fig.savefig('E:\\solar_car_race_strategy\\Report\\ConstVelSweep.png')

lin = Sweep.loc[Sweep.SoCMax<99].loc[Sweep.SoCMin>0]
x= lin.AverageVel.to_list()
y=lin.SoC.to_list()
import scipy.stats as stats
reg = stats.linregress(x,y)
x = np.array(x)
fig2,ax2 = plt.subplots(1)
ax2.plot(x,y,'x')
ax2.plot(x,reg.slope*x+reg.intercept)
fig2.show()
