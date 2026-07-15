import re

with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

old_func = """                # If a specific PMA Area was requested but we couldn't find its folder, 
                # return a dummy path so we don't accidentally scan ALL areas in the root folder!
                return os.path.join(base_d, "NON_EXISTENT_PMA_AREA_FALLBACK")"""

new_func = """                # If a specific PMA Area was requested but we couldn't find its folder, 
                # just return the base directory (e.g. OverTemp might not have Area subfolders)
                return base_d"""

content = content.replace(old_func, new_func)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
