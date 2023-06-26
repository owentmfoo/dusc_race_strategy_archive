import pandas as pd
import sys
sys.path.append('E:\solar_car_race_strategy\S5')
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


case = "Numerical"
NumericalTP = TP.TecplotData(f'E:\solar_car_race_strategy\\Numerical\\{case}_Input.dat')
df = NumericalTP.data
print(f'{case}_Input.dat Read in OK.')

fig, ax = plt.subplots(1)
# fig.set_size_inches(7*3.5/7, 6*3.5/7)
fig.set_size_inches(7*7.16/7, 3*7.16/7)


ax = df.plot(x='Distance (km)', y=['SpatialIrradiance',  'ClearSky', 'grad','CdA (m2)', 'HeadWind(m/s)'], subplots=True,
             ax=ax)
labellst = ['Spatial \nIrradiance \n(W/m2)', 'Temporal \nIrradiance \n(W/m2)', 'Gradient', 'CdA (m2)', 'Headwind \n(m/s)']
for axi,lbl in zip(ax,labellst):
    axi.legend().set_visible(False)
    axi.set_xlim([0, 3030])
    axi.set_ylabel(lbl)
for axi in ax[:-1]:
    axi.xaxis.set_visible(False)
# lgd = fig.legend(labellst, bbox_to_anchor=(0.5, 1), loc='upper center' ,ncol=2)

fig.tight_layout()
fig.subplots_adjust(hspace=0.05,right=0.99,left=0.1)
fig.show()
fig.savefig('E:\\solar_car_race_strategy\\Report\\NumericalInput.eps')

import scipy.stats,itertools
lst = ['SpatialIrradiance',  'ClearSky', 'grad','CdA (m2)', 'HeadWind(m/s)']
matrix = pd.DataFrame(columns=lst,index=lst)
for i,j in itertools.product(lst,lst):
    rho, pval = scipy.stats.pearsonr(df[i], df[j])
    matrix.loc[i,j] = pval

print(matrix)
matrix.to_clipboard()