import sys
import matplotlib.pyplot as plt
from shutil import copyfile as rename
import numpy as np
import os
import pandas as pd
sys.path.append('E:\solar_car_race_strategy\S5')
sys.path.append('/ddn/home/wqpq24')
import S5.Tecplot as TP
from S5.HPC.file_io import write_vel,read_history
from S5.HPC.SolarSim import file_sweep,read_file_sweep,file_sweep_par
from scipy.integrate import cumtrapz
import matplotlib.dates as dates
import pytz
import matplotlib

matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'serif',
    'text.usetex': False,
    'pgf.rcfonts': False,
    'font.size':8,
})

plt.rcParams.update({'font.serif':'Times New Roman'})

def cal_e_dx(power, velocity, x):
    return np.trapz(power / velocity, x=x)
def cal_e_dt(power,t):
    return np.trapz(power, x=t)
def cal_hist_power(path):
    var = ['Solar/InputPower(W)', 'InclinePower(W)', 'RollingPower(W)',
       'AeroPower(W)', 'ControllerPowerIn(W)', 'BatteryPowerOut(W)']
    print(os.path.basename(path))
    TPDF = TP.TecplotData(path)
    print(TPDF.data.loc[:,var].apply(lambda g: np.trapz(g, x=TPDF.data.loc[:,'DrivingTime(s)'])))
    return TPDF
def add_timestamp(HistTP,startday):
    HistTP.data.loc[:, 'Day'] = HistTP.data['DDHHMMSS'].astype(int).astype(str).str.pad(8, fillchar='0').str[
                                0:2].astype(int)
    startday = pd.to_datetime(startday)
    HistTP.data.loc[:, 'DateTime'] = pd.to_datetime(
        HistTP.data['DDHHMMSS'].astype(int).astype(str).str.pad(8, fillchar='0').str[2:8], format='%H%M%S')
    HistTP.data.loc[:, 'DateTime'] = pd.to_datetime(
        startday.strftime('%Y%m%d') + HistTP.data['DateTime'].dt.strftime('%H%M%S'))
    HistTP.data.loc[:, 'DateTime'] = HistTP.data['DateTime'] + pd.to_timedelta(HistTP.data['Day'] - 1, unit='D')
    return HistTP

H1path='E:\solar_car_race_strategy\SolarSim\CVX\History-SingleStratComb.dat'
Hpathlst = [H1path]
H1 = TP.TecplotData(H1path)
Hlst = [H1]
for H in Hlst:
    add_timestamp(H,'20191014')
H1.data.set_index("DateTime")
H1.data.set_index("DateTime",inplace=True)
H1.data.tz_localize('Australia/Darwin')
H1.data.reset_index(inplace=True)

var = ['Solar/InputPower(W)', 'InclinePower(W)', 'AeroPower(W)', 'ControllerPowerIn(W)', 'BatteryCharge(%)']

fig, ax = plt.subplots(2, 1)
fig.set_size_inches(8, 3)
tab10=plt.get_cmap('tab10').colors
cm = (tab10[1],tab10[4])

H1.data.plot(x='Distance(km)', y='BatteryCharge(%)', ax=ax[0], color=tab10[0], linewidth=2, legend=False)
axtwin = ax[0].twinx()
ax[0].set_ylabel("Battery SoC (%)",c=tab10[0])
ax[0].tick_params(axis='y', colors=tab10[0])
ax[0].xaxis.set_visible(False)
H1.data.plot(x='Distance(km)', y='CarVel(km/h)', ax=axtwin, color=tab10[3], linewidth=1, legend=False)
axtwin.set_ylim([65,80])
axtwin.set_ylabel("Car Velocity (km/h)",c=tab10[3])
axtwin.tick_params(axis='y', colors=tab10[3])

for i,v in enumerate(['Solar/InputPower(W)', 'AeroPower(W)']):
    H1.data.plot(x='Distance(km)', y=v, ax=ax[1], color=cm[i], linewidth=1, legend=False)
ax[1].set_ylim([0,1000])
ax[1].set_label("Power (W)")
ax[1].legend(["Irradiance Power (W)","Aero Power (W)"])

def inverse(x):  # TODO: make sure monotonically increasing
    return np.interp(x, dates.date2num(H1.data['DateTime']), H1.data['Distance(km)'].to_numpy())


def forward(x):
    return np.interp(x, H1.data['Distance(km)'].to_numpy(), dates.date2num(H1.data['DateTime']))

ax[-1].set_xlim([0,3021])
ax[0].set_xlim([0,3021])
ax[-1].set_xticks(np.arange(0, 3000, 500), minor=False)
ax[-1].set_xticks(np.arange(0, 3000, 100), minor=True)
plt.setp(ax[-1].get_xticklabels(), rotation=0, ha="right",
             rotation_mode="anchor")

secax = ax[0].secondary_xaxis('top', functions=(forward, inverse))
xticks = dates.num2date(secax.get_xticks(),tz = pytz.timezone('Australia/Darwin'))
xtickstabel = [out.strftime("%d-%m-%Y\n%H:%M ") for out in xticks]
secax.set_xticklabels(xtickstabel,rotation=0)

fig.subplots_adjust(top=0.88,bottom=0.12,left=0.07,right=0.95,hspace=0.1,wspace=0)
fig.set_dpi(150)
fig.show()
# fig.savefig('E:\\solar_car_race_strategy\\Report\\Trace.eps')