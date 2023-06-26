import pandas as pd
import sys
sys.path.append('E:\solar_car_race_strategy\S5')
print(sys.path)
import numpy as np
import S5.Tecplot as TP

import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'serif',
    'text.usetex': False,
    'pgf.rcfonts': False,
    'font.size':8,
})

plt.rcParams.update({'font.serif':'Times New Roman'})

H1 = TP.TecplotData('E:\solar_car_race_strategy\SolarSim\History-Grad.dat')
Road = TP.TecplotData('E:\solar_car_race_strategy\Weather\RoadFile-LatLon-Hillier.dat')
T1 = TP.TecplotData('E:\solar_car_race_strategy\SolarSim\TargetVel-Grad.dat')
fig,ax = plt.subplots(1,sharex=True)

ax.plot(T1.data['Distance (km)'],T1.data['TargetVel (km/h)'])
ax.plot(H1.data['Distance(km)'],H1.data['CarVel(km/h)'])
ax.plot(Road.data['Distance (km)'],Road.data['SpeedLimit (km/h)'],c='k',lw = 1)


ax.set_ylabel("Velocity (km/h)")
ax.set_xlabel("Distance (km)")
ax.set_xlim([0,3030])
# Road.data.plot(x='Distance (km)', y='Altitude (m)',ax=ax[1])
# ax[0].set_ylabel('BatteryCharge (%)')
# ax[0].legend(['0.Baseline','Strategy'])
# ax[1].legend('')
# ax[1].set_ylabel('Altitude (m)')
lgdlst  = ["Target","Driving","Speed Limit"]
lgd = fig.legend(lgdlst,bbox_to_anchor=(0.5, 0.98), loc='upper center' ,ncol=3)
# Eaerofig.set_size_inches(3.5,2.8)
# Eaerofig.subplots_adjust(top = 0.8,bottom=0.15,left=0.15)

fig.set_size_inches(3.5, 2)
# fig.subplots_adjust(top=0.88,bottom=0.12,left=0.07,right=0.95,hspace=0.1,wspace=0)
# fig.set_dpi(150)
# fig.show()
fig.show()
fig.savefig('E:\\solar_car_race_strategy\\Report\\GradVel.pdf')

fig,ax = plt.subplots(2,1,sharex=True)

Road.data.loc[:, 'dD'] = Road.data.loc[:, 'Distance (km)'].diff() *1000
Road.data.loc[:, 'dA'] = Road.data.loc[:, 'Altitude (m)'].diff()
Road.data.loc[:, 'grad'] = Road.data['dA'] / Road.data['dD']
Road.data.fillna(0, inplace=True)

ax[0].plot(Road.data.loc[:,'Distance (km)'],Road.data.loc[:,'grad'])
ax[0].set_ylabel('Gradient (~)')
ax[1].plot(Road.data.loc[:,'Distance (km)'],Road.data.loc[:,'Altitude (m)'])
ax[1].set_ylabel('Altitude (m)')
ax[0].set_xlim([0,3030])
fig.show()
fig.savefig('E:\\solar_car_race_strategy\\Report\\GradAltitude.png')
