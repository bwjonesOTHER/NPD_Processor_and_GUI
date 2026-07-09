with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

# Replace the deletion glob
old_del = """    for old_png in glob.glob(os.path.join(folder_path, '*.png')):
        try: os.remove(old_png)
        except: pass"""

new_del = """    import fnmatch
    for file in os.listdir(folder_path):
        if fnmatch.fnmatch(file, '*.png'):
            try: os.remove(os.path.join(folder_path, file))
            except: pass"""

content = content.replace(old_del, new_del)

# Replace the return glob
old_ret = """    png_files = glob.glob(os.path.join(folder_path, '*.png'))
    return png_files"""

new_ret = """    png_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if fnmatch.fnmatch(f, '*.png')]
    return png_files"""

content = content.replace(old_ret, new_ret)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
