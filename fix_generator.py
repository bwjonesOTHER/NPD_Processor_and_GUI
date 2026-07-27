import re

with open("backend/plot_generator.py", "r") as f:
    content = f.read()

# 1. Add colors to plotNPD
# Find traces.append in plotNPD for the main traces
plotnpd_trace_repl = """
        color_idx = len(traces) % 10
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
        traces.append({
            "x": sliced_freq.tolist(),
            "y": sliced_noise.tolist(),
            "type": "scatter",
            "mode": "lines",
            "name": serial[-21:-4:1],
            "line": {"color": colors[color_idx]}
        })
"""
content = re.sub(r'traces\.append\(\{\s*"x": sliced_freq\.tolist\(\),\s*"y": sliced_noise\.tolist\(\),\s*"type": "scatter",\s*"mode": "lines",\s*"name": serial\[-21:-4:1\]\s*\}\)', plotnpd_trace_repl.strip(), content)

# 2. Add colors to plotS21
plots21_trace_repl = """
            color_idx = len(traces) % 10
            colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
            traces.append({
                "x": ref_freq_full.tolist(),
                "y": s21.tolist(),
                "type": "scatter",
                "mode": "lines",
                "name": serial[-21:-4:1],
                "line": {"color": colors[color_idx]}
            })
"""
content = re.sub(r'traces\.append\(\{\s*"x": ref_freq_full\.tolist\(\),\s*"y": s21\.tolist\(\),\s*"type": "scatter",\s*"mode": "lines",\s*"name": serial\[-21:-4:1\]\s*\}\)', plots21_trace_repl.strip(), content)

# 3. Replace Freq Min and Freq Max traces with shapes in plotNPD and plotS21
content = re.sub(r'traces\.append\(\{\s*"x": \[freq_min, freq_min\],\s*"y": \[.*?name": "Freq Min".*?\}\)', '', content, flags=re.DOTALL)
content = re.sub(r'traces\.append\(\{\s*"x": \[freq_max, freq_max\],\s*"y": \[.*?name": "Freq Max".*?\}\)', '', content, flags=re.DOTALL)

# Add shapes to layout in plotNPD
npd_layout = """    layout = {
        "title": title,
        "xaxis": {"title": "Frequency (GHz)", "range": [freq_min, freq_max]},
        "yaxis": {"title": "NPD (dBm/Hz)" if plot_density else "NP (dBm)", "range": y_range},
        "showlegend": True,
        "legend": {"x": 1.05, "y": 1},
        "shapes": [
            {"type": "line", "x0": freq_min, "x1": freq_min, "y0": 0, "y1": 1, "yref": "paper", "line": {"color": "green", "width": 2}},
            {"type": "line", "x0": freq_max, "x1": freq_max, "y0": 0, "y1": 1, "yref": "paper", "line": {"color": "green", "width": 2}}
        ]
    }"""
content = re.sub(r'    layout = \{\s*"title": title,\s*"xaxis": \{"title": "Frequency \(GHz\)", "range": \[freq_min, freq_max\]\},\s*"yaxis": \{"title": "NPD \(dBm/Hz\)" if plot_density else "NP \(dBm\)", "range": y_range\},\s*"showlegend": True,\s*"legend": \{"x": 1\.05, "y": 1\}\s*\}', npd_layout, content)

# Add shapes to layout in plotS21
s21_layout = """    layout = {
        "title": title,
        "xaxis": {"title": "Frequency (GHz)", "range": [freq_min, freq_max]},
        "yaxis": {"title": "S21 (dB)", "range": y_range},
        "showlegend": True,
        "legend": {"x": 1.05, "y": 1},
        "shapes": [
            {"type": "line", "x0": freq_min, "x1": freq_min, "y0": 0, "y1": 1, "yref": "paper", "line": {"color": "green", "width": 2}},
            {"type": "line", "x0": freq_max, "x1": freq_max, "y0": 0, "y1": 1, "yref": "paper", "line": {"color": "green", "width": 2}}
        ]
    }"""
content = re.sub(r'    layout = \{\s*"title": title,\s*"xaxis": \{"title": "Frequency \(GHz\)", "range": \[freq_min, freq_max\]\},\s*"yaxis": \{"title": "S21 \(dB\)", "range": y_range\},\s*"showlegend": True,\s*"legend": \{"x": 1\.05, "y": 1\}\s*\}', s21_layout, content)

with open("backend/plot_generator.py", "w") as f:
    f.write(content)
