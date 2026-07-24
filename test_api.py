import sys
sys.path.append('backend')
from backend.plot_generator import generate_plots

payload = {
    "testType": 1,
    "runs": [
        "uploads/Test1/Run_0",
        ""
    ],
    "freq_min": 2.7,
    "freq_max": 4.1
}

try:
    res = generate_plots(payload)
    print("Generated", len(res), "plots")
    if len(res) > 0:
        traces = res[0].get("traces", [])
        print("First plot has", len(traces), "traces")
        if len(traces) > 0:
            print("Trace 0 length x:", len(traces[0].get("x", [])))
            print("Trace 0 length y:", len(traces[0].get("y", [])))
            print("Trace 0 x sample:", traces[0].get("x", [])[:5])
            print("Trace 0 y sample:", traces[0].get("y", [])[:5])
except Exception as e:
    import traceback
    traceback.print_exc()
