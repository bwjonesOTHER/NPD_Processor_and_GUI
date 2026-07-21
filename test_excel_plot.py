import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from backend.plot_generator import load_excel_average, _ota_plot_s21, _ota_plot_noise

# Create a dummy excel file
freqs = np.linspace(17.7, 21.2, 100)
amb_vals = np.linspace(-10, -10, 100)
df1 = pd.DataFrame({"Freq": freqs, "Amb": amb_vals, "Hot": amb_vals+2, "Cold": amb_vals-2})
with pd.ExcelWriter('dummy.xlsx') as writer:
    df1.to_excel(writer, sheet_name='Sheet1', index=False, header=False)
    df1.to_excel(writer, sheet_name='Sheet2', index=False, header=False)
    df1.to_excel(writer, sheet_name='Sheet3', index=False, header=False)
    df1.to_excel(writer, sheet_name='Sheet4', index=False, header=False)

# Test Array S21
avg_freq, avg_vals = load_excel_average('dummy.xlsx', 'Array S21', 'Ambient')
print("Loaded avg_freq length:", len(avg_freq) if avg_freq is not None else 0)

cal_mock = {"base": (None, None), "hat": (None, None), "specan": (None, None)}

res = _ota_plot_s21([], 'Ambient', 17.7, 21.2, 1, cal_mock, '.', avg_ref=(avg_freq, avg_vals), u_bound=None, l_bound=None)
print("Result of _ota_plot_s21:", res)
