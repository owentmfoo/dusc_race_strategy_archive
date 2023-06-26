import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import variation
import matplotlib

matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'serif',
    'text.usetex': False,
    'pgf.rcfonts': False,
    'font.size': 8,
})

plt.rcParams.update({'font.serif': 'Times New Roman'})


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


N = 6
num = 40
Estdfig, estdax = plt.subplots(1)
Eaerofig, eaeroax = plt.subplots(1)

cmap = plt.get_cmap("tab10").colors
cmapn = 0

Bat_R = 0.036
V_nom = 35 * 4
rho = 1.225
CdA = 0.089
v_bar = 70 / 3.6
F = 0.5 * rho * CdA * (v_bar) ** 2  # const drive force
dVel = 20 / 3.6
Crr = 0.008
m = 250
g = 9.81
Cell_Wh = 12.5
Batt_E = Cell_Wh * 12 * 35 * 3600

L = 3000000
npoint = 1000
x = np.linspace(0, L, num=npoint)

T = L / v_bar
# T=2
npoint = 1000
t = np.linspace(0, T, num=npoint)

grad_bar = 0.0016
dgrad = 0.01
I_bar = 0.5 * rho * CdA * v_bar ** 2 + Crr * m * g * v_bar
di = 100
cda_bar = 0.079
dcda = 0.01

kwargs = {
    "legend": False,
    # "marker":".",
    # "s": 14,
}

"""
Aero
"""

irradiance = np.piecewise(x, [x < L / 2, x >= L / 2], [lambda x: I_bar + di, lambda x: I_bar - di])

aero_estd = []
for j in range(1):
    j += 1
    for i in np.linspace(0, dVel, num=40):
        vel = strat_poly_normalised(irradiance, i, v_bar, j)
        P_drag = 0.5 * rho * CdA * vel ** 3
        itr = [cal_e_dx(P_drag, vel, x), np.std(vel)]
        aero_estd.append(itr)

df = pd.DataFrame(aero_estd)
df.columns = ['E', 'Vstd']
df.loc[:, 'E'] = (df['E'] - df['E'].iloc[0])  # make it delta to baseline
df.plot.scatter(y="E", x="Vstd", label="Drag Loss", ax=estdax, color=cmap[cmapn], **kwargs)
# cmapn+=1

Aero = df['E']

"""
Spatial Irradiance
"""

irradiance = np.piecewise(x, [x < L / 2, x >= L / 2], [lambda x: I_bar + di, lambda x: I_bar - di])
spatial_ird = irradiance

spaird_estd = []
for j in range(1):
    j += 1
    for i in np.linspace(0, -dVel, num=40):
        vel = strat_poly_normalised(irradiance, i, v_bar, j)
        P_drive = 0.5 * rho * CdA * v_bar ** 3 + Crr * m * g * vel
        P_net = P_drive - irradiance
        P_loss = Bat_R / V_nom ** 2 * P_net ** 2
        itr = [cal_e_dx(P_net + P_loss, vel, x), np.std(vel)]
        spaird_estd.append(itr)

df = pd.DataFrame(spaird_estd)
df.columns = ['E', 'Vstd']
df.loc[:, 'E'] = -(df['E'] - df['E'].iloc[0])  # make it delta to baseline
df.loc[:, 'E_aero'] = df['E'] - Aero
df.plot.scatter(y="E", x="Vstd", label="Spatial Irradiance Gain", ax=estdax, color=cmap[cmapn], **kwargs)
df.plot(y="E_aero", x="Vstd", label="Spatial Irradiance", ax=eaeroax, color=cmap[cmapn], **kwargs)

cmapn += 1

"""
Temporal Irradiance
"""

irradiance = np.piecewise(t, [t < T / 2, t >= T / 2], [lambda x: I_bar + di, lambda x: I_bar - di])
temporal_ird = irradiance

time_estd = []
for j in range(1):
    j += 1
    for i in np.linspace(0, dVel, num=40):
        v = strat_poly_normalised(irradiance, i, v_bar, 1)
        P_drive = 0.5 * rho * CdA * v ** 3 + Crr * m * g * v
        P_ird = irradiance
        P_grad = 0
        P_net = P_drive + P_grad - P_ird
        P_loss = (Bat_R / V_nom ** 2) * (P_net ** 2)
        itr = [cal_e_dt(P_loss, t), np.std(v), variation(v)]
        time_estd.append(itr)

df = pd.DataFrame(time_estd)
df.columns = ['E', 'Vstd', 'CV']
df.loc[:, 'E'] = -(df['E'] - df['E'].iloc[0])  # make it delta to baseline
df.loc[:, 'E_aero'] = df['E'] - Aero
df.plot.scatter(y="E", x="Vstd", label="Temporal Irradiance Gain", ax=estdax, color=cmap[cmapn], **kwargs)
df.plot(y="E_aero", x="Vstd", label="Temporal Irradiance", ax=eaeroax, color=cmap[cmapn], **kwargs)

cmapn += 1

"""
Gradient
"""

grad = np.piecewise(x, [x < L / 2, x >= L / 2], [lambda x: grad_bar + dgrad, lambda x: grad_bar - dgrad])
# grad = np.linspace(-0.06,0.06,num=len(x))
V = x * 0
R = x * 0
from tqdm import tqdm
import scipy.optimize as op

for n, gi in enumerate(tqdm(grad, desc='Computing Gradient Strategy')):
    root = op.root_scalar(lambda v:
                          0.5 * rho * CdA * v ** 3 + Crr * m * g * v + m * g * gi * v - 0.5 * rho * CdA * v_bar ** 3 - Crr * m * g * v_bar,
                          x0=v_bar, fprime=lambda v: 3 * 0.5 * rho * CdA * v ** 2 + Crr * m * g + m * g * gi)
    V[n] = root.root
    if not root.converged:
        print('non convergence')

maxi = df.Vstd.max() / V.std()
grad_estd = []
for j in range(1):
    j += 1
    for i in np.linspace(0, maxi, num=40):
        v = (V - V.mean()) * i + v_bar  # to preserve the mean velocity
        # if np.min(v) < 0:
        #     continue
        P_drive = 0.5 * rho * CdA * v ** 3 + Crr * m * g * v
        P_ird = 0.5 * rho * CdA * v_bar ** 3 + Crr * m * g * v_bar
        P_grad = m * g * grad * v
        P_net = P_drive + P_grad - P_ird
        P_loss = (Bat_R / V_nom ** 2) * (P_net ** 2)
        itr = [v.std(), i, cal_e_dx(P_net, v, x), cal_e_dx(P_loss, v, x), i, variation(v)]
        grad_estd.append(itr)
        # ax.plot(x,P_loss)

df = pd.DataFrame(grad_estd)
df.columns = ['Vstd', 'dVe', 'E_Net', 'E_loss', 'i', 'CV']
df.loc[:, 'E_loss'] = -(df['E_loss'] - df['E_loss'].iloc[0])
df.loc[:, 'E_aero'] = df['E_loss'] - Aero

# df.plot.scatter(y='E_Net',x="Vstd", ax=estdax,color = cmap[cmapn],marker='.')
# cmapn+=1
df.plot.scatter(y='E_loss', x="Vstd", label="Gradient I2R Gain", ax=estdax, color=cmap[cmapn], **kwargs)
df.plot(y="E_aero", x="Vstd", label="Gradient", ax=eaeroax, color=cmap[cmapn], **kwargs)

cmapn += 1

"""
Yaw
"""

cda = np.piecewise(x, [x < L / 2, x >= L / 2], [lambda x: cda_bar + dcda, lambda x: cda_bar - dcda])

yaw_estd = []
for j in range(1):
    j += 1
    for i in np.linspace(0, -dVel, num=40):
        vel = strat_poly_normalised(cda, i, v_bar, j)
        P_drive = 0.5 * rho * cda * vel ** 3
        P_net = P_drive - 0.5 * rho * CdA * v_bar ** 3 + Crr * m * g * v_bar
        P_loss = Bat_R / V_nom ** 2 * P_net ** 2
        itr = [cal_e_dt(P_net + P_loss, t), np.std(vel)]
        yaw_estd.append(itr)

df = pd.DataFrame(yaw_estd)
df.columns = ['E', 'Vstd']
df.loc[:, 'E'] = -(df['E'] - df['E'].iloc[0])  # make it delta to baseline
df.loc[:, 'E_aero'] = df['E']
df.plot.scatter(y="E", x="Vstd", label="Wind Yaw Angle Gain", ax=estdax, color=cmap[cmapn], **kwargs)
df.plot(y="E_aero", x="Vstd", label="Wind Yaw Angle", ax=eaeroax, color=cmap[cmapn], **kwargs)

cmapn += 1

"""
Headwind Velocity
"""
Vwcost = np.piecewise(x, [x < L / 2, x >= L / 2], [lambda x: -0.5 / 3.6, lambda x: 0.5 / 3.6])

Vw_estd = []
for j in range(1):
    j += 1
    for i in np.linspace(0, dVel, num=40):
        vel = strat_poly_normalised(Vwcost, i, v_bar, j)
        P_drive = 0.5 * rho * cda * abs(vel - Vwcost) ** 3
        P_net = P_drive - 0.5 * rho * CdA * v_bar ** 3 + Crr * m * g * v_bar
        P_loss = Bat_R / V_nom ** 2 * P_net ** 2
        itr = [cal_e_dt(P_net + P_loss, t), np.std(vel)]
        Vw_estd.append(itr)

df = pd.DataFrame(Vw_estd)
df.columns = ['E', 'Vstd']
df.loc[:, 'E'] = -(df['E'] - df['E'].iloc[0])  # make it delta to baseline
df.loc[:, 'E_aero'] = df['E']
df.plot.scatter(y="E", x="Vstd", label="Wind Velocity Gain", ax=estdax, color=cmap[cmapn], **kwargs)
df.plot(y="E_aero", x="Vstd", label="Wind Velocity", ax=eaeroax, color=cmap[cmapn], **kwargs)

cmapn += 1

# estdax.scatter(df['Vstd'],cumE,color=cmap[cmapn],marker='.',label='Total Loss')

# estdax.legend()
# Estdfig.set(dpi=300)
estdax.set(xlabel='Velocity standard deviation (m/s)', ylabel='Energy (J)')
estdax.axhline(y=0, color='k', lw=0.7)
plt.tight_layout()

# eaeroax.legend()
# Eaerofig.set(dpi=300)
eaeroax.set(xlabel='Velocity standard deviation (m/s)')
eaeroax.axhline(y=0, color='k', lw=0.7)
eaeroax.set_ylim([-Batt_E * 0.3, Batt_E * 0.1])
eaeroax.set_xlim([0, 5.2])
eaeroax.set_yticks(np.linspace(-Batt_E * 0.3, Batt_E * 0.1, 9))
eaeroax.set_yticklabels(eaeroax.get_yticks() / Batt_E * 100)
eaeroax.set_ylabel('Percentage of Nominal Battery Capacity (%)')

plt.tight_layout()

Estdfig.show()
plt.figure()
lgdlst = ['Spatial Irradiance', 'Temporal Irradiance', 'Gradient', 'Wind Yaw', 'Wind Velocity']
lgd = Eaerofig.legend(lgdlst, bbox_to_anchor=(0.5, 0.98), loc='upper center', ncol=3)
Eaerofig.set_size_inches(3.5, 2.8)
Eaerofig.subplots_adjust(top=0.8, bottom=0.15, left=0.15)
Eaerofig.show()
Eaerofig.savefig('E:\\solar_car_race_strategy\\Report\\Analytical.eps')
