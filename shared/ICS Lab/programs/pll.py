import matplotlib.pyplot as plt
import numpy as np

## initial conditions
omega_in = 1E7
omega_out = 1E7
phi_in = 0

phi_out = 0

## gitter: [i, omega, phi]
gitter = [
    [500, 1.6E7, 1.8],
    [1500, 1.6E7, 1.8]
]

## circuit parameters
K_PD = 1E3
K_VCO = 1E3
omega_fr = 1E7

## simulation parameters
T_total = 2.5E-5
dt = 1E-8
t = 0
linspace = range(int(T_total/dt))

## loop parameters
V_in = np.sin(phi_in)
V_out = np.sin(phi_out)
V_err = 0
V_cont = 0

## graph parameters
V_in_list = []
V_out_list = []
V_err_list = []
omega_out_list = []

## simulation
for i in linspace:
    # PD
    phi_in += omega_in*dt
    phi_out += omega_out*dt
    V_err = K_PD*((phi_in - phi_out) - ((phi_in - phi_out)/2/np.pi)//1*np.pi*2)
    # V_err = K_PD*((phi_in - phi_out))
    V_err_list.append(V_err)

    # LPF
    V_cont = V_err

    # VCO
    omega_out = omega_fr + K_VCO*V_cont
    omega_out_list.append(omega_out)
    
    # Add Gitter
    for j in gitter:
        if j[0] == i:
            omega_in = j[1]
            phi_in = j[2]

    # Feedback
    V_in += omega_in*np.cos(omega_in*t)*dt
    V_out += omega_out*np.cos(omega_out*t)*dt
    V_in = max(min(V_in, 1), -1)
    V_out = max(min(V_out, 1), -1)
    V_in_list.append(V_in)
    V_out_list.append(V_out)
    t += dt


fig, ax = plt.subplots(2, 1)
ax[0].set_title("V-t")
ax[0].plot(linspace, V_in_list)
ax[0].plot(linspace, V_out_list)
# ax[1].set_title("V_err-t")
# ax[1].plot(linspace, V_err_list)
ax[1].set_title("omega-t")
# ax[1].plot(linspace, [omega_in]*int(T_total/dt))
ax[1].plot(linspace, omega_out_list)
plt.savefig('img.png')