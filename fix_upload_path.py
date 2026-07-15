with open('backend/app.py', 'r') as f:
    content = f.read()

# Fix upload_run base path logic to never use path.txt (which points to user hard drive from access mode)
old_upload_run = """    base_path = read_txt("upload_path.txt")
    if not base_path:
        base_path = read_txt("path.txt")
    if not base_path:
        base_path = os.path.join(os.getcwd(), 'uploads')"""

new_upload_run = """    base_path = read_txt("upload_path.txt")
    if not base_path:
        # Fallback strictly to local uploads folder so we don't accidentally write to the user's root directory from a previous test
        base_path = os.path.join(os.getcwd(), 'uploads')"""

content = content.replace(old_upload_run, new_upload_run)

with open('backend/app.py', 'w') as f:
    f.write(content)
