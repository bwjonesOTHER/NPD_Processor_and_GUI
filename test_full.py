import sys
import os
import glob
sys.path.insert(0, 'backend')
import plot_generator
import math_v3

runs = [
    '/Users/tj/Documents/Redwire/NPD_Processor_and_GUI/PMA_NPDoverTemp/Normal_Run',
    '/Users/tj/Documents/Redwire/NPD_Processor_and_GUI/PMA_NPDoverTemp/Problem_Child_Run'
]
folder_path = runs[0]

params = {
    'runs': runs,
    'folder_path': folder_path,
    'freq_min': 2.6,
    'freq_max': 4.1,
    'n_avg': 51
}

# Create dummy files for test
for run in runs:
    os.makedirs(os.path.join(run, 'Cap_01'), exist_ok=True)
    with open(os.path.join(run, 'EM-1234_NPDOverTempNPD.csv'), 'w') as f:
        f.write("freq,power,density\n1.0,-100,-100\n2.0,-100,-100\n3.0,-100,-100\n")
    with open(os.path.join(run, 'EM-1234_VSWR.s2p'), 'w') as f:
        f.write("! 2 1\n1.0 -10 0\n2.0 -10 0\n")
    with open(os.path.join(run, 'Cap_01', 'Base.s2p'), 'w') as f:
        f.write("! 2 1\n1.0 -10 0\n2.0 -10 0\n")
    with open(os.path.join(run, 'Cap_01', 'Bulkhead.s2p'), 'w') as f:
        f.write("! 2 1\n1.0 -10 0\n2.0 -10 0\n")

print("Files collected by _collect_files for NPDOverTempNPD:")
for run in runs:
    print(math_v3.search_files(run, "*NPDOverTempNPD*"))

try:
    pngs = plot_generator.generate_plots(params)
    print("Returned PNGs:", pngs)
except Exception as e:
    import traceback
    traceback.print_exc()
