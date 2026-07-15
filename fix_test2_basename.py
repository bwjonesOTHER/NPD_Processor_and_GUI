import re

content = open('backend/plot_generator.py', 'r').read()

old_filter = """        def filter_benchtop(files):
            return [f for f in files if "npdovertemp" not in f.lower()]"""

new_filter = """        def filter_benchtop(files):
            import os
            # Only check the filename and immediate parent directory, not the entire path which might coincidentally contain 'npdovertemp'
            return [f for f in files if "npdovertemp" not in os.path.basename(f).lower()]"""

content = content.replace(old_filter, new_filter)

open('backend/plot_generator.py', 'w').write(content)
