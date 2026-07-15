with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

bad_code = "if pma and search_dirA == temp_dir: # only filter if we didn't successfully drill down into a PMA folder"
good_code = "if pma and search_dirA == temp: # only filter if we didn't successfully drill down into a PMA folder"

content = content.replace(bad_code, good_code)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
