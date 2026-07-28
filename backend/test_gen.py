import sys, os
sys.path.append('.')
import plot_generator

# print files in Run_0
print("Run_0:", os.listdir('uploads/Test3/Run_0') if os.path.exists('uploads/Test3/Run_0') else "Not found")
print("Run_1:", os.listdir('uploads/Test3/Run_1') if os.path.exists('uploads/Test3/Run_1') else "Not found")

# mock search_files
orig_search = plot_generator.search_files
def mock_search(base, k1, k2=None):
    res = orig_search(base, k1, k2)
    print(f"SEARCH: base={base}, k1={k1}, k2={k2} -> {res}")
    return res

plot_generator.search_files = mock_search

params = {'testType': 3, 'runs': [os.path.join(os.getcwd(), 'uploads/Test3/Run_0'), os.path.join(os.getcwd(), 'uploads/Test3/Run_1'), os.path.join(os.getcwd(), 'uploads/Test3/Run_2')], 'serial_number': ''}
print("PARAMS:", params)
try:
    res = plot_generator.generate_plots(params)
    print("RES length:", len(res))
except Exception as e:
    import traceback
    traceback.print_exc()
