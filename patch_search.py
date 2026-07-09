import re

with open('backend/math_v3.py', 'r') as f:
    content = f.read()

new_search = """import fnmatch

def search_files(root_dir, pattern):
    matched_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if fnmatch.fnmatch(file, pattern):
                matched_files.append(os.path.join(dirpath, file))
    return matched_files"""

# Replace the glob import and search_files definition
content = content.replace("from glob import glob", "import fnmatch\nimport os")
# Find and replace the old search_files function
old_search = """def search_files(root_dir, pattern):
    return glob(os.path.join(root_dir, "**", pattern), recursive=True)"""
content = content.replace(old_search, new_search)

with open('backend/math_v3.py', 'w') as f:
    f.write(content)
