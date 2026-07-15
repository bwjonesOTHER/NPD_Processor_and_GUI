content = open('backend/plot_generator.py', 'r').read()

old_folders = """    folderA = resolved_runs[0] if len(resolved_runs) > 0 else ""
    folderB = resolved_runs[1] if len(resolved_runs) > 1 else ""
"""

new_folders = """    folderA = resolved_runs[0] if len(resolved_runs) > 0 else ""
    folderB = resolved_runs[1] if len(resolved_runs) > 1 else folderA
"""

content = content.replace(old_folders, new_folders)
open('backend/plot_generator.py', 'w').write(content)
