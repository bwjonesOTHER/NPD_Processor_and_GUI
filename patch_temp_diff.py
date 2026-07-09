with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

old_temp_diff = """    def render_temp_diff(d25, d64, dn38, title):
        if d25 and d64 and dn38:
            try:
                import matplotlib.pyplot as plt
                freq = d25['freq_ref']
                diff1 = np.abs(d25['avg_trace'] - d64['avg_trace'])
                diff2 = np.abs(d25['avg_trace'] - dn38['avg_trace'])
                diff3 = np.abs(d64['avg_trace'] - dn38['avg_trace'])"""

new_temp_diff = """    def render_temp_diff(d25, d64, dn38, title):
        if d25 and d64 and dn38:
            try:
                import matplotlib.pyplot as plt
                import numpy as np
                freq = d25['freq_ref']
                # Interpolate to ensure same shapes
                trace_64 = np.interp(freq, d64['freq_ref'], d64['avg_trace'])
                trace_n38 = np.interp(freq, dn38['freq_ref'], dn38['avg_trace'])
                diff1 = np.abs(d25['avg_trace'] - trace_64)
                diff2 = np.abs(d25['avg_trace'] - trace_n38)
                diff3 = np.abs(trace_64 - trace_n38)"""

content = content.replace(old_temp_diff, new_temp_diff)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
