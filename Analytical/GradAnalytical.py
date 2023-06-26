import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.optimize as op
from tqdm import tqdm

sys.path.append('E:\solar_car_race_strategy\S5')
print(sys.path)
import S5.Tecplot as TP


def strat(irradiance, v_bar, c=1):
    residual = (irradiance - np.mean(irradiance))
    v = v_bar + c * residual / F
    return v


def strat_poly(irradiance, v_bar, c, n=1):
    # c: scalar proportion
    residual = (irradiance - np.mean(irradiance))
    residual = abs(residual ** n) * np.sign(residual)
    adj = (residual) * c
    vel = v_bar - np.mean(adj) + adj
    return vel


def strat_poly_normalised(irradiance, c, v_bar, n=1):
    # c: scalar proportion
    residual = (irradiance - np.mean(irradiance))
    residual = abs(residual ** n) * np.sign(residual)
    adj = (residual / max(residual)) * c
    vel = v_bar - np.mean(adj) + adj
    return vel


def strat_exp(irradiance, c, v_bar, n=1):
    residual = (irradiance ** n - np.mean(irradiance ** n))
    adj = np.exp(residual / max(residual))
    adj = adj - np.mean(adj)
    adj = (adj) / min(adj) * -c
    vel = v_bar + adj
    return vel


def cal_e_dt(power, t):
    return np.trapz(power, x=t)


def cal_e_dx(power, velocity, x):
    return np.trapz(power / velocity, x=x)


def cal_drag_eout(velocity):
    return np.sum((velocity - np.mean(velocity)) ** 2)


N = 4
Estdfig, estdax = plt.subplots(1)
pt, ax = plt.subplots(1)

cmap = plt.cm.viridis(np.linspace(0, 1, N))
cmapn = 0

m = 250
g = 9.81
Bat_R = 0.036
V_nom = 35 * 3.7
rho = 1.225
CdA = 0.107
v_bar = 70 / 3.6
# F = 0.5*rho*CdA*(v_bar)**2 # const drive force
Crr = 0.008

L = 3000000
npoint = 1000
x = np.linspace(0, L, num=npoint)

T = L / v_bar
npoint = 1000
t = np.linspace(0, T, num=npoint)

grad_bar = 0.00
dgrad = 0.0016

"""
Gradient
"""

### Real data
RoadTP = TP.TecplotData('E:\solar_car_race_strategy\SolarSim\Baseline\RoadFile-LatLon-2021.dat')
RoadTP.data.loc[:, 'dD'] = RoadTP.data.loc[:, 'Distance (km)'].diff() * 1000
RoadTP.data.loc[:, 'dA'] = RoadTP.data.loc[:, 'Altitude (m)'].diff()
RoadTP.data.loc[:, 'grad'] = RoadTP.data['dA'] / RoadTP.data['dD']
RoadTP.data.fillna(0, inplace=True)
x = RoadTP.data['Distance (km)'].to_numpy() * 1000
grad = RoadTP.data['grad'].to_numpy()
print('Read in OK.')

### Idealised
# x = np.linspace(0, L, num=npoint)
# grad = np.piecewise(x, [x < L / 2, x >= L / 2], [lambda x: grad_bar + dgrad, lambda x: grad_bar - dgrad])
# grad = np.linspace(-0.04, 0.04, num=len(x))
V = x * 0
R = x * 0


for n, gi in enumerate(tqdm(grad, desc='Computing Gradient Strategy')):
    root = op.root_scalar(lambda v:
                          0.5 * rho * CdA * v ** 3 + Crr * m * g * v + m * g * gi * v - 0.5 * rho * CdA * v_bar ** 3 - Crr * m * g * v_bar,
                          x0=v_bar, fprime=lambda v: 3 * 0.5 * rho * CdA * v ** 2 + Crr * m * g + m * g * gi)
    V[n] = root.root
    if not root.converged:
        print('non convergence')

maxi = 0.4 / V.std()
grad_estd = []
for j in range(1):
    j += 1
    for i in np.linspace(0, 1, num=40):
        v = (V - V.mean()) * i + v_bar  # to preserve the mean velocity
        # if np.min(v) < 0:
        #     continue
        P_drive = 0.5 * rho * CdA * v ** 3 + Crr * m * g * v
        P_ird = 0.5 * rho * CdA * v_bar ** 3 + Crr * m * g * v_bar
        P_grad = m * g * grad * v
        P_net = P_drive + P_grad - P_ird
        P_loss = (Bat_R / V_nom ** 2) * (P_net ** 2)
        itr = [v.std(), i, cal_e_dx(P_net, v, x), cal_e_dx(P_loss, v, x), i]
        grad_estd.append(itr)
        # ax.plot(x,P_loss)

df = pd.DataFrame(grad_estd)
df = (df - df.iloc[0, :])  # make it delta to baseline

df.columns = ['Vstd', 'dVe', 'E_Net', 'E_loss', 'i']
df.plot.scatter(y='E_Net',x="Vstd", ax=estdax,color = cmap[cmapn],marker='.')
cmapn += 1

df.plot.scatter(y='E_loss', x="Vstd", label="I2R", ax=estdax, color=cmap[cmapn], marker='.')
cmapn += 1

# df.plot.scatter(y='E',x="Vstd",  label="Tot", ax=estdax,color = cmap[cmapn],marker='.')
# cmapn += 1

# estdax.scatter(df['Vstd'],cumE,color=cmap[cmapn],marker='.',label='Total Loss')


Estdfig.set(dpi=300)
estdax.set(title='Gradient Energy loss', xlabel='Velocity standard deviation (m/s)', ylabel='Energy (J)')

#
# ax.legend(range(10))
# pt.show()

vgrad = plt.scatter(V, grad)
vgrad.axes.set(xlabel='v (m/s)', ylabel='grad')
plt.tight_layout()

Estdfig.show()
plt.figure()
vgrad.figure.show()
