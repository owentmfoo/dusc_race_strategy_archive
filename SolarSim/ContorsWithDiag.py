"""
Post simulation analysis tool
Script to plot the car through time and space overlayed on top of the weather contours.
"""
import sys
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
sys.path.append('E:\solar_car_race_strategy\S5')
sys.path.append('/ddn/home/wqpq24')
import S5.Tecplot as TP
from scipy.integrate import cumtrapz
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


H1path='E:\solar_car_race_strategy\SolarSim\Const-Vel\History_73.dat'
H2path='E:\solar_car_race_strategy\SolarSim\CVX\History-SingleStratComb.dat'
H3path='E:\solar_car_race_strategy\SolarSim\CombStrat\History_CombStratIdeal.dat'
START_DATE = '20191013'
Weather = TP.SSWeather('E:\solar_car_race_strategy\SolCastHistoric\Weather-SolCast-N200-20220322.dat')


Hpathlst = [H1path,H2path,H3path]
H0path = H1path
H1 = TP.SSHistory(H1path)
H2 = TP.SSHistory(H2path)
H3 = TP.SSHistory(H3path)
Hlst = [H1,H2,H3]
H0 = H1

for H in Hlst:
    H.add_timestamp(START_DATE)

Weather.addtimestamp(startday=START_DATE)

direct = Weather.data.loc[:,['DirectSun (W/m2)']].to_numpy()
diffuse = Weather.data.loc[:,['DiffuseSun (W/m2)']].to_numpy()
WindVel = Weather.data.loc[:,['WindVel (m/s)']].to_numpy()
AirTemp = Weather.data.loc[:,['AirTemp (degC)']].to_numpy()
AirPress = Weather.data.loc[:,['AirPress (Pa)']].to_numpy()

def plotdiag(cont,diag=True,VarName = '',cmap = 'viridis',outname=None):
    """not self contained function, in script use only.
    :param cont: contour variable
    :param diag: bool Ture to plot diag loc of car in spacetime

    :returns: None (display a fig)
    """
    Dist = np.unique(Weather.data.loc[:,['Distance (km)']].to_numpy())
    DateTime = np.unique(Weather.data.loc[:,['DateTime']].to_numpy())
    import matplotlib.dates as dates
    DateTimenum,Dist = np.meshgrid(Dist,dates.date2num(DateTime))
    plotvel = np.reshape(cont,np.shape(Dist)[::-1]).transpose()
    fig, ax = plt.subplots()

    # plot the contour
    c = ax.pcolormesh(Dist,DateTimenum,plotvel,cmap=cmap)
    cbar = fig.colorbar(c, ax=ax)
    cbar.set_label(VarName, rotation=270,labelpad=10)
    xticks = dates.num2date(ax.get_xticks())
    xticks = [out.strftime("%d-%m-%Y\n%H:%M ") for out in xticks]
    ax.set_xticklabels(xticks)

    # Plot diagonal trace of the car through time and space
    if diag:
        cm=plt.get_cmap('Set1')
        ax.plot(H1.data['DateTime'],H1.data['Distance(km)'],c=cm.colors[0],lw=2)
        ax.plot(H2.data['DateTime'],H2.data['Distance(km)'],c=cm.colors[1],lw=2)
        ax.legend(['Constant Velocity', 'Optimised'])

    # Format the figure
    ax.set_ylim([0,3030])
    ax.set_ylabel("Distance (km)")
    ax.set_xlim([dates.date2num(H1.data['DateTime'].min())-1/24,dates.date2num(H1.data['DateTime'].max())+1/24])
    ax.set_xlabel("Time")
    fig.set_size_inches(8,3)
    fig.subplots_adjust(top=0.98,bottom=0.12,left=0.07,right=1.05,hspace=0,wspace=0)
    fig.set_dpi(150)
    fig.show()

    if outname is None:
        fig.savefig(f'E:\\solar_car_race_strategy\\Report\\{VarName}.pdf')
    else:
        outname = outname.rstrip(".pdf").rstrip(".png")
        fig.savefig(f'E:\\solar_car_race_strategy\\Report\\{outname}.pdf')
        fig.savefig(f'E:\\solar_car_race_strategy\\Report\\{outname}.png')

plotdiag(direct,diag=True,VarName = 'Direct Irradiation (W/m²)',cmap = 'inferno',outname="directContor")
plotdiag(diffuse,diag=True,VarName = 'Diffuse Irradiation (W/m²)',cmap = 'inferno',outname="diffuseContor")
plotdiag(WindVel,diag=True,VarName = 'Wind Velocity (m/s)',cmap = 'viridis',outname="windContor")
plotdiag(AirTemp,diag=True,VarName = 'Air Temperature (°C)',cmap = 'coolwarm',outname="tempContor")
plotdiag(AirPress,diag=True,VarName = 'Air Pressure (Pa)',cmap = 'coolwarm',outname="pressContor")