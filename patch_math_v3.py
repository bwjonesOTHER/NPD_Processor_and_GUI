with open('backend/math_v3.py', 'r') as f:
    content = f.read()

old_search = """def search_files(root_dir, pattern):
    matched_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if fnmatch.fnmatch(file, pattern):
                matched_files.append(os.path.join(dirpath, file))
    return matched_files"""

new_search = """def search_files(root_dir, pattern):
    matched_files = []
    pattern_lower = pattern.lower()
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if fnmatch.fnmatch(file.lower(), pattern_lower):
                matched_files.append(os.path.join(dirpath, file))
    return matched_files"""

content = content.replace(old_search, new_search)

with open('backend/math_v3.py', 'w') as f:
    f.write(content)
