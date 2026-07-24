import re

file_path = "/Users/tj/Documents/Redwire/NPD_Processor_and_GUI/backend/plot_generator.py"

with open(file_path, "r") as f:
    content = f.read()

# I want to replace things like `freq.tolist()` with `(freq.tolist() if hasattr(freq, 'tolist') else list(freq))`
# A simple regex for variables followed by `.tolist()`
# E.g. `([a-zA-Z_0-9\[\]]+)\.tolist\(\)` -> `(\1.tolist() if hasattr(\1, 'tolist') else list(\1))`

# However, some might be properties of expressions, like `np.abs(a_v - h_v).tolist()`.
# So it's easier to just write a simple wrapper function at the top of the file and replace `.tolist()` with that, but wait, `tolist()` is a method on an object.

# Instead of regex, I can define `def to_list(arr): return arr.tolist() if hasattr(arr, 'tolist') else list(arr)` at the top, and then find where it's crashing.
# But wait, why is it crashing? Let's check `plot_generator.py` line 694. 
# Oh! `a_f`, `a_v` from `data_dict["Ambient"]`.
# Let's check where `data_dict` comes from.
# It comes from `generate_plots` (Test 3).
