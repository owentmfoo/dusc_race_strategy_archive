import scipy.optimize as op
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def strat(irradiance,v_bar,c=1):
    residual = (irradiance - np.mean(irradiance))
    v = v_bar+c*residual/F
    return v

def strat_poly(irradiance,  v_bar, c,n=1):
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

def cal_e_dt(power,t):
    return np.trapz(power,x=t)

def cal_e_dx(power, velocity,x):
    return np.trapz(power / velocity,x=x)

def cal_drag_eout(velocity):
    return np.sum((velocity - np.mean(velocity)) ** 2)

N = 4
Estdfig, estdax = plt.subplots(1)
pt, ax = plt.subplots(1)

cmap = plt.cm.viridis(np.linspace(0,1,N))
cmapn = 0

m = 250
g = 9.81
Bat_R = 0.036
V_nom = 35*3.7
rho = 1.225
CdA = 0.107
v_bar = 70/3.6
# F = 0.5*rho*CdA*(v_bar)**2 # const drive force
dVel = 5/ 3.6
Crr = 0.008

L = 3000
npoint = 1000
x = np.linspace(0, L, num=npoint)

T = L/v_bar
# T=2
npoint = 1000
t = np.linspace(0, T, num=npoint)



grad_bar = 0.00
dgrad = 0
I_bar = 0.5*rho*CdA*v_bar**3 + Crr*m*g*v_bar + m*g*grad_bar*v_bar
di = 200

"""
Temporal Irradiance
"""

irradiance = np.piecewise(t, [t < T / 2, t >= T / 2], [lambda x: I_bar + di, lambda x: I_bar - di])

V = op.fsolve(lambda v: (0.5*rho*CdA*v**3 + Crr*m*g*v) + (0) - (irradiance),x0=v_bar+x*0)
print(np.unique(V*3.6))
dVel = np.max(V-v_bar) *1.5
time_estd = []
for j in range(1):
    j += 1
    for i in np.linspace(0, dVel, num=10):
        v = strat_poly_normalised(irradiance, i, v_bar, 1)
        P_drive = 0.5*rho*CdA*v**3 + Crr*m*g*v
        P_ird =   irradiance
        P_grad = 0
        P_net = P_drive + P_grad - P_ird
        P_loss = (Bat_R / V_nom ** 2) * (P_net ** 2)
        itr = [np.std(v),i,cal_e_dx(P_net,v,x),cal_e_dx(P_loss,v,x)]
        time_estd.append(itr)
        # ax.plot(x,P_loss)

df = pd.DataFrame(time_estd)
df = (df - df.iloc[0,:])  # make it delta to baseline

df.columns = ['Vstd','dVe','E_Net','E_loss']
# df.plot.scatter(y='E_Net',x="Vstd", ax=estdax,color = cmap[cmapn],marker='.')
# cmapn+=1
df.plot.scatter(y='E_loss',x="Vstd",  label="I2R", ax=estdax,color = cmap[cmapn],marker='.')
cmapn += 1

# df.plot.scatter(y='E',x="Vstd",  label="Tot", ax=estdax,color = cmap[cmapn],marker='.')
# cmapn += 1



# estdax.scatter(df['Vstd'],cumE,color=cmap[cmapn],marker='.',label='Total Loss')


Estdfig.set(dpi=300)
estdax.set(title='Gradient Energy loss',xlabel='Velocity standard deviation (m/s)', ylabel='Energy (J)')
Estdfig.show()
#
# ax.legend(range(10))
# pt.show()

