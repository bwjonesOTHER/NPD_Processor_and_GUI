import re
with open("backend/plot_generator.py", "r") as f:
    content = f.read()

plots21_trace_repl = """
        color_idx = len(traces) % 10
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
        traces.append({
            "x": sliced_freq.tolist(),
            "y": sliced_s21.tolist(),
            "type": "scatter",
            "mode": "lines",
            "name": serial[-21:-4:1],
            "line": {"color": colors[color_idx]}
        })
"""
content = re.sub(r'traces\.append\(\{\s*"x": sliced_freq\.tolist\(\),\s*"y": sliced_s21\.tolist\(\),\s*"type": "scatter",\s*"mode": "lines",\s*"name": serial\[-21:-4:1\]\s*\}\)', plots21_trace_repl.strip(), content)

with open("backend/plot_generator.py", "w") as f:
    f.write(content)
