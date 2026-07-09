with open('backend/math_v3.py', 'r') as f:
    content = f.read()

import re

old_label = """            serial = extract_serial(file)
            chain = extract_pri_red(file)
            label = f"{serial[-16:-8]} {chain}"
            if len(runs_data) > 1: label += f" ({run['name']})\""""

new_label = """            serial = extract_serial(file)
            chain = extract_pri_red(file)
            label = f"{serial[-16:-8]} {chain}"
            # Extract temp from filename
            f_lower = file.lower()
            if 'ambient' in f_lower or '25c' in f_lower:
                label += " (25C)"
            elif 'hot' in f_lower or '64c' in f_lower:
                label += " (64C)"
            elif 'cold' in f_lower or '38c' in f_lower:
                label += " (-38C)"
            if len(runs_data) > 1: label += f" ({run['name']})\""""

# We need to replace it in process_file_math and process_S21, wait, actually process_S21 has this too.
# Let's just do a generic replace.

content = content.replace(old_label, new_label)
with open('backend/math_v3.py', 'w') as f:
    f.write(content)
