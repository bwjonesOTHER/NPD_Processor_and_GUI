import sys
sys.path.append('.')
from backend.plot_generator import load_np_data

freq, noise = load_np_data('dummy_data/RunA/ambient/Tile01_NPD.csv', '')
print("Freq:", freq)
print("Noise:", noise)
