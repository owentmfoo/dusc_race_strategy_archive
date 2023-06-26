import sys
import matplotlib.pyplot as plt
from shutil import copyfile as rename
import numpy as np
import os
import pandas as pd

sys.path.append('E:\solar_car_race_strategy\S5')
sys.path.append('/ddn/home/wqpq24')
import S5.Tecplot as TP
from S5.HPC.file_io import write_vel, read_history
from S5.HPC.SolarSim import file_sweep, read_file_sweep, file_sweep_par
from scipy.integrate import cumtrapz


def cal_e_dx(power, velocity, x):
    return np.trapz(power / velocity, x=x)


def cal_e_dt(power, t):
    return np.trapz(power, x=t)


def cal_hist_power(path):
    var = ['Solar/InputPower(W)', 'InclinePower(W)', 'RollingPower(W)',
           'AeroPower(W)', 'ControllerPowerIn(W)', 'BatteryPowerOut(W)']
    print(os.path.basename(path))
    TPDF = TP.TecplotData(path)
    print(TPDF.data.loc[:, var].apply(lambda g: np.trapz(g, x=TPDF.data.loc[:, 'DrivingTime(s)'])))
    return TPDF


H1path = 'E:\solar_car_race_strategy\SolarSim\Const-Vel\History_70.dat'
H2path = 'E:\solar_car_race_strategy\SolarSim\CVX\History_CVX2.1_1s.dat'
H1 = TP.TecplotData(H1path)
H2 = TP.TecplotData(H2path)

var = ['Solar/InputPower(W)', 'InclinePower(W)', 'RollingPower(W)',
       'AeroPower(W)', 'ControllerPowerIn(W)', 'BatteryPowerOut(W)']


fig, ax = plt.subplots(len(var) + 2, 1, sharex=True)
fig.set_size_inches(11.75, 8.25)
# TODO: colormap
cm = plt.cm.viridis(np.linspace(0, 1, 3))


i = 0
for v in ['CarVel(km/h)', 'Solar/InputPower(W)', 'RollingPower(W)',
          'AeroPower(W)', ]:
    H1.data.plot(x='DayAndTime(s)', y=v, ax=ax[i], color=cm[0], linewidth=1, legend=False)
    H2.data.plot(x='DayAndTime(s)', y=v, ax=ax[i], color=cm[1], linewidth=1, legend=False)
    ax[i].set_ylabel(v)
    if i % 2 == 1:
        ax[i].yaxis.tick_right()
        ax[i].yaxis.set_label_position("right")
    i += 1

for v in ['ControllerPowerIn(W)', 'InclinePower(W)', 'BatteryPowerOut(W)']:
    ax[i].plot(H1.data['DayAndTime(s)'].iloc[:-1], cumtrapz(H1.data[v], H1.data['DayAndTime(s)']), color=cm[0],
               linewidth=1)
    ax[i].plot(H2.data['DayAndTime(s)'].iloc[:-1], cumtrapz(H2.data[v], H2.data['DayAndTime(s)']), color=cm[1],
               linewidth=1)
    ax[i].set_ylabel('Integral of\n'+v)
    # ax[i].legend()
    if i % 2 == 1:
        ax[i].yaxis.tick_right()
        ax[i].yaxis.set_label_position("right")
    i += 1
#     H1.data.plot(x='DayAndTime(s)',y=v,ax=ax[i+1],label=os.path.basename(H1path),color=cm[0],linewidth=1)
#     H2.data.plot(x='DayAndTime(s)',y=v,ax=ax[i+1],label=os.path.basename(H2path),color=cm[1],linewidth=1)

i -= 1
ax2 = ax[i].twinx()
v = 'BatteryCharge(%)'
H1.data.plot(x='DayAndTime(s)', y=v, ax=ax2, color=cm[0], linewidth=1, linestyle='-.', legend=False)
H2.data.plot(x='DayAndTime(s)', y=v, ax=ax2, color=cm[1], linewidth=1, linestyle='-.', legend=False)
ax2.set_ylabel(v)

i+=1
v = 'CarVel(m/s)'
axtwin = ax[i]
axtwin.plot(H1.data['DayAndTime(s)'].iloc[:-1], cumtrapz(H1.data[v], H1.data['DayAndTime(s)'])/1000-H1.data['Distance(km)'].iloc[1:], color=cm[0],
           linewidth=1)
axtwin.plot(H2.data['DayAndTime(s)'].iloc[:-1], cumtrapz(H2.data[v], H2.data['DayAndTime(s)'])/1000-H2.data['Distance(km)'].iloc[1:], color=cm[1],
           linewidth=1)
axtwin.set_ylabel('Difference between \nDistance and integral of carvel')




fig.legend(['Constant Velocity', 'Optimised Strategy'])




def forward(x):  # TODO: make sure monotonically increasing
    return np.interp(x, H2.data['DayAndTime(s)'], H2.data['Distance(km)'])


def inverse(x):
    return np.interp(x, H2.data['Distance(km)'], H2.data['DayAndTime(s)'])


secax = ax[0].secondary_xaxis('top', functions=(forward, inverse))
secax.set_xticks(np.arange(0, 3000, 500), minor=False)
secax.set_xticks(np.arange(0, 3000, 100), minor=True)
# plt.setp(secax.get_xticklabels(), rotation=-30, ha="right",
#              rotation_mode="anchor")

fig.dpi = 300
plt.tight_layout()
fig.savefig('E:\solar_car_race_strategy\SolarSim\CVX\Auto_1s.pdf')
