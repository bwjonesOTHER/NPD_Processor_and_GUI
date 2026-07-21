import pandas as pd
import numpy as np
import os
from backend.plot_generator import load_excel_average

# Create a dummy excel file
df1 = pd.DataFrame({"Freq": [1, 2, 3], "Amb": [10, 20, 30], "Hot": [11, 21, 31], "Cold": [9, 19, 29]})
with pd.ExcelWriter('dummy.xlsx') as writer:
    df1.to_excel(writer, sheet_name='Sheet1', index=False, header=False)
    df1.to_excel(writer, sheet_name='Sheet2', index=False, header=False)
    df1.to_excel(writer, sheet_name='Sheet3', index=False, header=False)
    df1.to_excel(writer, sheet_name='Sheet4', index=False, header=False)

f, v = load_excel_average('dummy.xlsx', 'Tile NPD', 'Ambient')
print(f"Tile NPD Ambient: {f}, {v}")

