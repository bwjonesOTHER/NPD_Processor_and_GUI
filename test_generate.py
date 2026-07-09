import sys
sys.path.insert(0, 'backend')
import plot_generator
import traceback
import glob

params = {
    'runs': ['Normal_Run', 'Problem_Child_Run'],
    'folder_path': '/Users/tj/Documents/Redwire/NPD_Processor_and_GUI/PMA_NPDoverTemp',
    'freq_min': 2.6,
    'freq_max': 4.1,
    'n_avg': 51
}

try:
    pngs = plot_generator.generate_plots(params)
    print("Returned PNGs:", pngs)
    
    actual_pngs = glob.glob('/Users/tj/Documents/Redwire/NPD_Processor_and_GUI/PMA_NPDoverTemp/*.png')
    print("Actual PNGs in folder:", actual_pngs)
except Exception as e:
    print("Error during plot generation:")
    traceback.print_exc()

