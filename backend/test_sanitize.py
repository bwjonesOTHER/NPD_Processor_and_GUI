import math
import numpy as np

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

print(sanitize_for_json({"data": [np.float64(np.nan)]}))
