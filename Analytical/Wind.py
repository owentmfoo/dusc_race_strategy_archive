import numpy as np
import matplotlib.pyplot as plt
import pandas as pd



def cal_e_dt(power,t):
    return np.trapz(power,x=t)

def cal_e_dx(power, velocity,x):
    return np.trapz(power / velocity,x=x)
def strat_poly_normalised(irradiance, c, v_bar, n=1):
    # c: scalar proportion
    residual = (irradiance - np.mean(irradiance))
    residual = abs(residual ** n) * np.sign(residual)
    adj = (residual / max(residual)) * c
    vel = v_bar - np.mean(adj) + adj
    return vel


npoint = 300
L = 3000
v_bar = 70/3.6
T = L/v_bar
# T=2
t = np.linspace(0, T, num=npoint)
x = np.linspace(0, L, num=npoint)

cda_bar = 0.086
dcda = 0.003
cda = np.piecewise(x, [x < L / 2, x >= L / 2], [lambda x: cda_bar+dcda, lambda x: cda_bar-dcda])
V = cda
R = x*0

Estdfig, estdax = plt.subplots(1)
pt, ax = plt.subplots(1)

N=3
cmap = plt.cm.viridis(np.linspace(0,1,N))
cmapn = 0

m = 250
g = 9.81
Bat_R = 0.036
V_nom = 35*3.7
rho = 1.225
CdA = 0.107

# F = 0.5*rho*CdA*(v_bar)**2 # const drive force
Crr = 0.008

print(f'opitimal v\': {v_bar/cda_bar*dcda}')

maxi = 0.4/V.std()
yaw_estd = []

c_prime = v_bar/np.mean(cda)
j=1
for i in np.linspace(-1, 1, num=40):
    v = (V-V.mean())*i+v_bar # to preserve the mean velocity
    # if np.min(v) < 0:
    #     continue
    vel = strat_poly_normalised(cda, i, v_bar, j)
    P_drive = 0.5 * rho * cda * vel ** 3
    P_net = P_drive - 0
    P_loss = Bat_R / V_nom ** 2 * P_net ** 2
    itr = [cal_e_dx(P_net + P_loss,vel, x), np.std(vel),i,cal_e_dt(P_net + P_loss,t)]
    yaw_estd.append(itr)

df = pd.DataFrame(yaw_estd)
df.columns = ['E', 'Vstd','c','dt']
df.loc[:, 'E'] = -(df['E'] - df['E'].iloc[0])  # make it delta to baseline
df.loc[:, 'dt'] = -(df['dt'] - df['dt'].iloc[0])
df.loc[:, 'E_aero'] = df['E']
ax = df.plot.scatter(y="E", x="Vstd", label="Wind Yaw Angle Gain" , color=cmap[cmapn], marker='.')
df.plot.scatter(y="dt", x="Vstd", label="int dt" , color=cmap[cmapn+1], marker='.',ax=ax)
cmapn += 1
plt.show()


