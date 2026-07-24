import json
import numpy as np

freq = np.linspace(2.7, 4.1, 100)
noise = np.random.normal(-130, 5, 100)
avg = np.random.normal(-130, 2, 100)
lower = avg - 3
upper = avg + 3

traces = []
traces.append({
    "x": freq.tolist(),
    "y": noise.tolist(),
    "type": "scatter",
    "mode": "lines",
    "name": "Data"
})
traces.append({
    "x": freq.tolist(),
    "y": lower.tolist(),
    "type": "scatter",
    "mode": "lines+markers",
    "name": "Lower bound",
    "marker": {"color": "red", "symbol": "circle", "size": 4},
    "line": {"color": "red"}
})
traces.append({
    "x": [2.7, 2.7],
    "y": [-170, -110],
    "type": "scatter",
    "mode": "lines",
    "name": "Limit",
    "line": {"color": "orange", "dash": "dash"}
})

layout = {
    "title": "Test Plot",
    "xaxis": {"title": "Frequency (GHz)"},
    "yaxis": {"title": "NPD (dBm/Hz)"}
}

plot_data = {
    "traces": traces,
    "layout": layout
}

with open("dummy_plot.json", "w") as f:
    json.dump(plot_data, f, indent=2)

html_content = """
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
</head>
<body>
  <div id="plot" style="width:600px; height:400px; border:1px solid red;"></div>
  <script>
    fetch('dummy_plot.json')
      .then(res => res.json())
      .then(data => {
        Plotly.newPlot('plot', data.traces, data.layout);
      });
  </script>
</body>
</html>
"""

with open("dummy_plot.html", "w") as f:
    f.write(html_content)

print("Generated dummy_plot.html and dummy_plot.json")
