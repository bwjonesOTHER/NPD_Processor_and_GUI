with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

bad_code = """        if pma and search_dirA == temp_dir: # only filter if we didn't successfully drill down into a PMA folder
            import os, re
            pma_norm = re.sub(r'[^a-zA-Z0-9]', '', pma).lower()"""

good_code = """        if pma and search_dirA == temp_dir: # only filter if we didn't successfully drill down into a PMA folder
            pma_norm = re.sub(r'[^a-zA-Z0-9]', '', pma).lower()"""

content = content.replace(bad_code, good_code)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)

