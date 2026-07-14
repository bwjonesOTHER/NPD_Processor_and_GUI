import skrf as rf
with open('empty.s2p', 'w') as f:
    f.write('! empty s2p file\n')
try:
    net = rf.Network('empty.s2p')
    print("Network loaded. s_db shape:", net.s_db.shape)
except Exception as e:
    print("Exception:", e)
