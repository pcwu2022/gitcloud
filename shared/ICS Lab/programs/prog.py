import numpy as np
import matplotlib.pyplot as plt

def comp(vip, vin, noise):
    vnoise = noise * np.random.randn(1, 1)  # because the parameter "noise" is STD, we change it to a voltage
    vip = vip + vnoise

    if (vip - vin < 0):
        out = 0
    else:
        out = 1

    return out



def para_cap(vi):
    Vcm = 1
    cdif = 0.3
    cmax = 1
    Ccommon = 4

    vi = 2 - vi
    if vi > Vcm:
        a = -((vi - 1.5 * Vcm) ** 2 - (0.5 * Vcm) ** 2) / ((0.5 * Vcm) ** 2)
    else:
        a = +((vi - 0.5 * Vcm) ** 2 - (0.5 * Vcm) ** 2) / ((0.5 * Vcm) ** 2)
    
    cap = +a * cdif + (vi * cmax) / 2 + Ccommon
    return cap

def Mono_10bit(vip, vin, Cp, Cn, noise):
    code = np.zeros((10, 1))  # 10-bit output code, generate 10*1 all-zero matrix
    Vref = 2
    Vcm = Vref / 2
    Cup = 0
    Cup_new = 0
    Cdown = 0
    Cdown_new = 0

    # mono
    for n in range(10):
        Vdiff = comp(vip, vin, noise)
        if Vdiff > 0:
            code[n, 0] = 1
            k = para_cap(vip)
            vip = (vip * np.sum(Cp) - Cp[n] * Vref + vip * k) / (np.sum(Cp) + para_cap(vip))
            for p in range(5):
                j = para_cap(vip)
                vip = vip * (np.sum(Cp) + k) / (np.sum(Cp) + j)
                k = j
        else:
            code[n, 0] = 0
            k = para_cap(vin)
            vin = (vin * np.sum(Cn) - Cn[n] * Vref + vin * k) / (np.sum(Cn) + para_cap(vin))
            for p in range(5):
                j = para_cap(vin)
                vin = vin * (np.sum(Cn) + k) / (np.sum(Cn) + j)
                k = j

    return code

N = 10  # resolution
Number = 2**13  # 2^13, power of 2 for FFT calculation

Cp = np.array([256, 128, 64, 32, 16, 8, 4, 2, 1, 1])  # DACp
Cn = np.array([256, 128, 64, 32, 16, 8, 4, 2, 1, 1])  # DACn
CodeWeighting = np.array([512, 256, 128, 64, 32, 16, 8, 4, 2, 1])  # Weighting
noise = 0

# Static performance
INL = np.zeros(2**10)
DNL = np.zeros(2**10)

Output_static = np.zeros(2 * Number + 1)  # -2^13~2^13

for n in range(-Number, Number + 1):
    vip = n / Number + 1
    vin = -n / Number + 1  # vin & vip ramp wave, common mode = 1

    Code_static = Mono_10bit(vip, vin, Cp, Cn, noise)  # SAR ADC

    k = n + Number  # MATLAB indexing starts from 1

    for u in range(N):
        Output_static[k] += Code_static[u] * CodeWeighting[u]  # binary to decimal

Output_static = np.round(Output_static)  # each element to the nearest integer
NumCode = len(Output_static)
NumCode_use = 0
code_count = np.zeros(2**10)

for i in range(NumCode):
    if Output_static[i] != 0 and Output_static[i] != 2**10 - 1:
        NumCode_use += 1
        code_count[int(Output_static[i])] += 1  # from 1, count occurrences of each number

idealCodeWidth = NumCode_use / (2**10 - 2)  # excluding 0 and 1023
DNL = (code_count - idealCodeWidth) / idealCodeWidth
DNL[0] = 0
DNL[2**10 - 1] = 0

for i in range(1, 2**10):
    INL[i] = INL[i - 1] + DNL[i]

i = np.arange(2**10)

plt.figure(1)
plt.plot(i, DNL)
plt.xlabel('DNL ')
plt.ylabel('Code (LSB)')
plt.xlim([0, 2**10 - 1])
plt.savefig("dnl.png")

plt.figure(2)
plt.plot(i, INL)
plt.xlabel('INL')
plt.ylabel('Code (LSB)')
plt.xlim([0, 2**10 - 1])
plt.savefig("inl.png")

OSR = 1  # over sample ratio
fs = 50 * 10**6  # 50MHz

Ne = 16384 * 8  # how to choose this value?
Me = 12233  # how to choose this value?
fi = (fs / Ne) * Me  # 4.66652
BW = fs / (2 * OSR)
Meg = (2**10 - 1) / (2**10)
Output_fft = np.zeros(Ne)

for n in range(Ne):
    vip = Meg * np.sin(2 * np.pi * fi * (n + 1) * 2 * 10**(-8)) + 1  # vin & vip sine wave, common mode = 1
    vin = -Meg * np.sin(2 * np.pi * fi * (n + 1) * 2 * 10**(-8)) + 1

    Code_fft = Mono_10bit(vip, vin, Cp, Cn, noise)  # SAR ADC

    for u in range(N):
        Output_fft[n] += Code_fft[u] * CodeWeighting[u]  # Weighting

plt.plot(Output_fft)
plt.savefig("fft.png")

yb = Output_fft

yk1 = np.fft.fft(yb)
yk = np.abs(yk1)
f = fs * np.arange(Ne) / Ne
Pyy = yk * np.conj(yk)

Pyy += 1e-9

Pyy10 = 10 * np.log10(Pyy)

Pyy_ktk = Pyy10
v, pts_in = np.max(Pyy_ktk[1:Ne]), np.argmax(Pyy_ktk[1:Ne]) + 1
plt.figure(3)
max_tone = 10 * np.log10(Pyy[pts_in])
plt.plot(f[1:Ne//2] / 1e6, 10 * np.log10(Pyy[1:Ne//2]) - max_tone, '-rx')
plt.xlabel('Frequency (MHz)')
plt.ylabel('Y[k](dB)')
plt.title('Output')
plt.ylim([-120, 0])
plt.grid()
plt.savefig("output.png")

pts_bw = Ne // 2 + 1

pwr_inp = np.sum(Pyy[pts_in - 1:pts_in + 2])  # signal power
pwr_inb_nh = (np.sum(Pyy[1:pts_in - 2]) + np.sum(Pyy[pts_in + 2:pts_bw]))  # noise power
snrdbw = 10 * np.log10(pwr_inp) - 10 * np.log10(pwr_inb_nh)  # SNDR
ENOB = (snrdbw - 1.76) / 6.02  # ENOB


