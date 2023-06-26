"""Try to solve this by posing it as an optimisation problem minimising the energy consumption."""

import sys

import cvxpy as cp
import matplotlib.pyplot as plt

sys.path.append('E:\solar_car_race_strategy\S5')
print(sys.path)
import S5.Tecplot as TP

m = 250
g = 9.81
Bat_R = 0.036
V_nom = 35 * 3.7
rho = 1.225
CdA = 0.107
v_bar = 70 / 3.6
# F = 0.5*rho*CdA*(v_bar)**2 # const drive force
Crr = 0.008

### Real data
RoadTP = TP.TecplotData('E:\solar_car_race_strategy\SolarSim\Baseline\RoadFile-LatLon-2021.dat')
RoadTP.data.loc[:, 'dD'] = RoadTP.data.loc[:, 'Distance (km)'].diff() * 1000
RoadTP.data.loc[:, 'dA'] = RoadTP.data.loc[:, 'Altitude (m)'].diff()
RoadTP.data.loc[:, 'grad'] = RoadTP.data['dA'] / RoadTP.data['dD']
RoadTP.data.fillna(0, inplace=True)

# downsample to around 10000
downsample_factor = int(RoadTP.data.shape[0] / 10000)
print(f'Down sampling to 1 every {downsample_factor} samples.')

RoadTP.data = RoadTP.data.iloc[::downsample_factor, :]

# extract the distance and gradient as numpy arrays
x = RoadTP.data['Distance (km)'].to_numpy() * 1000
grad = RoadTP.data['grad'].to_numpy()
print('Read in OK.')

### Idealised
# L = 3000
# x = np.linspace(0, L, 4000)
# grad_bar = 0.00
# dgrad = 0.0016
# grad = np.linspace(-dgrad, dgrad, 4000)


n = len(x)
v = cp.Variable(n)  # the vector of velocities to drive at each segment of the route
prob = cp.Problem(cp.Minimize(cp.sum(0.5 * rho * CdA * cp.power(v, 3) + m * g * Crr * v + m * g * cp.diag(
    v) @ grad - 0.5 * rho * CdA * v_bar - m * g * Crr * v_bar)),
                  [cp.sum(v) / n - v_bar == 0,
                   v >= 0])
prob.solve()

print(prob.value)
print(v.value)

fig, (ax0, ax1) = plt.subplots(2, 1)
ax0.plot(x, v.value)
ax1.plot(x, grad)
plt.show()
