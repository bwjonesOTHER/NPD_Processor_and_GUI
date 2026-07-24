import sys, os
sys.path.insert(0, os.path.abspath('backend'))
import plot_generator
import numpy as np
import json
import math

import tempfile
d = tempfile.mkdtemp()
csv_file = os.path.join(d, "Tile01_Ambient_NP_EM-12345.csv")
with open(csv_file, "w") as f:
    for i in range(100):
        f.write(f"{2.7 + i*0.014}, -130, -130, 0, 0, 0, 0, 0, 0, 0\n")

# plot_temp_deltas needs ambient and extreme files
p = plot_generator.plot_temp_deltas(
    file_ambient=csv_file,
    file_extreme=csv_file,
    title="Test",
    freq_min=2.7,
    freq_max=4.1,
    y_lower_npd=-170,
    y_upper_npd=-110,
    plot_density=False,
    apply_cal=False,
    test_type=1,
    cal_folder_ambient="",
    cal_folder_extreme="",
    plot_s12=False
)

def sanitize_for_json(obj):
    if isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj

sanitized = sanitize_for_json(p)
with open("plotDeltas_dump.json", "w") as f:
    json.dump(sanitized, f, indent=2)
print("Dumped plotDeltas_dump.json")
