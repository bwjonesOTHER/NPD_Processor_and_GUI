import sys
import json
import numpy as np
import os
import math
sys.path.append('.')
from backend.plot_generator import generate_plots

params = {
    "testType": 1,
    "runs": ["dummy_data/RunA", ""],
    "outputFolder": "dummy_data/output",
    "freq_min": 2.7,
    "freq_max": 4.1
}

os.system("mkdir -p dummy_data/RunA/ambient/Cable\ Loss")
result = generate_plots(params)

def sanitize_for_json(obj):
    if isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, float) or isinstance(obj, np.floating):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return float(obj)
    return obj

with open('test_dummy_output.json', 'w') as f:
    json.dump(sanitize_for_json(result), f, indent=2)

print("Plots generated:", len(result))
