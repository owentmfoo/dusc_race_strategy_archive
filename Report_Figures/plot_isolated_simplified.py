import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'serif',
    'text.usetex': False,
    'pgf.rcfonts': False,
    'font.size':8,
})

plt.rcParams.update({'font.serif':'Times New Roman'})

IdealWeather = pd.read_csv('E:\\solar_car_race_strategy\\Numerical\\Simplified_Ideal_Weather_Sweep_Results.csv')
FullWeather = pd.read_csv('E:\\solar_car_race_strategy\\Numerical\\Simplified_Full_Weather_Sweep_Results.csv')

cm = plt.cm.get_cmap("tab10").colors
Cell_Wh = 12.5
BattE = Cell_Wh * 12 * 35 * 3600

idealparams={"ls":'--',"lw":1}
fullparams={"ls":'-',"lw":1}

IdealWeather.set_index(IdealWeather.columns[0],inplace = True)
FullWeather.set_index(FullWeather.columns[0],inplace = True)
IdealWeather.interpolate(inplace=True)
FullWeather.interpolate(inplace=True)
IdealWeather = IdealWeather.apply(lambda x: -(x-x[0])/BattE)
FullWeather = FullWeather.apply(lambda x: -(x-x[0])/BattE)
IdealWeather = IdealWeather[-2:2]
FullWeather = FullWeather[-2:2]
fig,ax = plt.subplots(5,sharex=True)

for i,colname in enumerate(['Spatial Irradiance', 'Temporal Irradiance', 'Gradient', 'Yaw Angle', 'Headwind']):
    ax[i].plot(IdealWeather.index,IdealWeather.loc[:,colname],c=cm[i],**idealparams)
    ax[i].plot(FullWeather.index,FullWeather.loc[:,colname], c=cm[i],label = colname,**fullparams)
    # ax[i].legend()
    ax[i].axhline(0,lw=1,c="0.3")
    ax[i].set_ylabel(colname.replace(' ','\n'))
    ax[i].set_xlim([FullWeather.index.min(),FullWeather.index.max()])
    ax[i].set_ylim([-0.2,0.15])
    ax[i].xaxis.set_visible(False)

ax[-1].xaxis.set_visible(True)
ax[-1].set_xlabel('68th percentile of v')
lgd = fig.legend((ax[0].get_children())[0:2],["Ideal","All"],ncol=2,
                 loc="upper left",bbox_to_anchor=(0.22, 0.995))
fig.set_size_inches(3.5,3.5)
fig.tight_layout()
fig.supylabel("Gain in battery SoC compared to constant velocity (%)")
fig.subplots_adjust(top=0.90,hspace=0.1,right=0.98,left=0.22)
fig.show()
fig.savefig('E:\\solar_car_race_strategy\\Report\\SimplifiedIsolated.eps')
