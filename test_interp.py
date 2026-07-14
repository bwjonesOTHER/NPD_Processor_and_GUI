import skrf as rf
import numpy as np

# create a dummy network with 10 points
freq = rf.Frequency(1, 10, 10, 'ghz')
s = np.random.rand(10, 2, 2)
net = rf.Network(frequency=freq, s=s)

print("net.f shape:", net.f.shape)
print("net.f in GHz:", net.f / 1e9)

# now let's interpolate to 20 points
target_freq = np.linspace(1, 10, 20)
s21 = net.s_db[:, 1, 0]
interp_s21 = np.interp(target_freq, net.f / 1e9, s21)
print("interp shape:", interp_s21.shape)

