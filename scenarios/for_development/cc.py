import numpy as np
import matplotlib.pyplot as plt

data = np.array([
    [-0.00000000e+00, -0.00000000e+00, -0.00000000e+00, -0.00000000e+00, -0.00000000e+00, -0.00000000e+00, -0.00000000e+00, -0.00000000e+00, -0.00000000e+00, -0.00000000e+00],
    [ 1.41421356e+01,  1.41421356e+01,  1.41421356e+01,  1.41421356e+01,  1.41421356e+01,  1.41421356e+01,  1.41421356e+01,  1.41421356e+01,  1.41421356e+01,  1.41421356e+01],
    [ 7.07106781e+00, -1.47825570e+00, -9.46293579e+00, -1.38330960e+01, -1.29194838e+01, -7.07106781e+00,  1.47825570e+00,  9.46293579e+00,  1.38330960e+01,  1.29194838e+01],
    [ 7.07106781e+00,  1.29194838e+01,  1.38330960e+01,  9.46293579e+00,  1.47825570e+00, -7.07106781e+00, -1.29194838e+01, -1.38330960e+01, -9.46293579e+00, -1.47825570e+00],
    [-1.41421356e+01, -1.14412281e+01, -4.37016024e+00,  4.37016024e+00,  1.14412281e+01,  1.41421356e+01,  1.14412281e+01,  4.37016024e+00, -4.37016024e+00, -1.14412281e+01],
    [-5.23598776e-02,  1.04719755e-02,  7.33038286e-02,  1.36135682e-01,  1.98967535e-01,  2.61799388e-01,  3.24631241e-01,  3.87463094e-01,  4.50294947e-01,  5.13126800e-01]
])

x_data = data[5, :]

fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(x_data, data[0, :], color='black', linestyle='--', label=r'$I_d$', linewidth=1.5)
ax.plot(x_data, data[1, :], color='black', linestyle='-', label=r'$I_q$', linewidth=1.5)

ax.plot(x_data, data[2, :], color='#B22222', label='Phase A', linewidth=2.0)
ax.plot(x_data, data[3, :], color='#1F4E79', label='Phase B', linewidth=2.0)
ax.plot(x_data, data[4, :], color='#595959', label='Phase C', linewidth=2.0)

ax.set_xlabel('Rotor Position (rad)', fontsize=11)
ax.set_ylabel('Current (A)', fontsize=11)
ax.legend(frameon=True, loc='best', ncol=2, fontsize=10)
ax.grid(True, linestyle='-', linewidth=0.5)
ax.margins(x=0)

plt.tight_layout()
plt.show()