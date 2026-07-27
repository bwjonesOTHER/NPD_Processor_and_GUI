#!/usr/bin/env python3
"""Diagnose broken.json vs working.json to find what causes blank Plotly renders."""
import json
import sys

def analyze_plot_json(filepath):
    print(f"\n{'='*60}")
    print(f"Analyzing: {filepath}")
    print(f"{'='*60}")
    
    with open(filepath) as f:
        data = json.load(f)
    
    print(f"Top-level keys: {list(data.keys())}")
    print(f"Status: {data.get('status')}")
    print(f"Filename: {data.get('filename')}")
    
    # Layout analysis
    layout = data.get('layout', {})
    print(f"\nLayout keys: {list(layout.keys())}")
    print(f"  title: {layout.get('title')}")
    print(f"  xaxis: {layout.get('xaxis')}")
    print(f"  yaxis: {layout.get('yaxis')}")
    if 'yaxis2' in layout:
        print(f"  yaxis2: {layout.get('yaxis2')}")
    if 'shapes' in layout:
        print(f"  shapes: {layout.get('shapes')}")
    
    # Trace analysis
    traces = data.get('traces', [])
    print(f"\nNumber of traces: {len(traces)}")
    
    total_points = 0
    for i, t in enumerate(traces):
        x = t.get('x', [])
        y = t.get('y', [])
        xlen = len(x) if isinstance(x, list) else 'NOT A LIST'
        ylen = len(y) if isinstance(y, list) else 'NOT A LIST'
        total_points += (xlen if isinstance(xlen, int) else 0) + (ylen if isinstance(ylen, int) else 0)
        
        # Check for problematic values
        null_count = sum(1 for v in y if v is None) if isinstance(y, list) else 0
        nan_count = 0
        inf_count = 0
        non_numeric = 0
        for v in (y if isinstance(y, list) else []):
            if v is None:
                continue
            if not isinstance(v, (int, float)):
                non_numeric += 1
            elif isinstance(v, float):
                import math
                if math.isnan(v):
                    nan_count += 1
                if math.isinf(v):
                    inf_count += 1
        
        # X range
        x_range = ""
        if isinstance(x, list) and len(x) > 0:
            x_min = min(v for v in x if v is not None and isinstance(v, (int, float)))
            x_max = max(v for v in x if v is not None and isinstance(v, (int, float)))
            x_range = f"[{x_min:.4f}, {x_max:.4f}]"
        
        # Y range
        y_range = ""
        if isinstance(y, list) and len(y) > 0:
            numeric_y = [v for v in y if v is not None and isinstance(v, (int, float))]
            if numeric_y:
                y_range = f"[{min(numeric_y):.4f}, {max(numeric_y):.4f}]"
        
        issues = []
        if null_count > 0: issues.append(f"{null_count} nulls")
        if nan_count > 0: issues.append(f"{nan_count} NaNs")
        if inf_count > 0: issues.append(f"{inf_count} Infs")
        if non_numeric > 0: issues.append(f"{non_numeric} non-numeric")
        if isinstance(xlen, int) and isinstance(ylen, int) and xlen != ylen:
            issues.append(f"X/Y LENGTH MISMATCH ({xlen} vs {ylen})")
        
        issue_str = f" ⚠️  {', '.join(issues)}" if issues else ""
        print(f"  [{i:2d}] name={t.get('name','?'):25s} type={t.get('type','?'):10s} mode={t.get('mode','?'):15s} x={xlen:>5} y={ylen:>5} x_range={x_range:25s} y_range={y_range:25s}{issue_str}")
    
    print(f"\n  Total data points: {total_points:,}")
    
    # Check for extra keys in traces that Plotly might choke on
    print(f"\n  Trace keys present across all traces:")
    all_keys = set()
    for t in traces:
        all_keys.update(t.keys())
    print(f"    {sorted(all_keys)}")
    
    # Check freq/avg arrays
    if 'freq' in data:
        freq = data['freq']
        if freq is not None:
            print(f"\n  Extra 'freq' array: len={len(freq)}, range=[{min(freq):.4f}, {max(freq):.4f}]")
        else:
            print(f"\n  Extra 'freq' array: None")
    if 'avg' in data:
        avg = data['avg']
        if avg is not None:
            null_in_avg = sum(1 for v in avg if v is None)
            print(f"  Extra 'avg' array: len={len(avg)}, nulls={null_in_avg}")
        else:
            print(f"  Extra 'avg' array: None")

for f in ['broken.json', 'working.json']:
    try:
        analyze_plot_json(f)
    except Exception as e:
        print(f"ERROR analyzing {f}: {e}")
