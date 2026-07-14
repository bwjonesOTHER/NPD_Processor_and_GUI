import re

with open('backend/app.py', 'r') as f:
    content = f.read()

target = """                try:
                    all_dirs = [d for d in os.listdir(pma_path) if os.path.isdir(os.path.join(pma_path, d))]
                    matches = [d for d in all_dirs if lmo_num in d]
                    
                    if len(matches) > 1:
                        return jsonify({"success": False, "requireLmoSelection": True, "options": matches})
                    elif len(matches) == 1:
                        lmo_num = matches[0]
                except Exception as e:
                    print("Error scanning for LMO folders:", e)"""

replace = """                try:
                    all_dirs = [d for d in os.listdir(pma_path) if os.path.isdir(os.path.join(pma_path, d))]
                    matches = [d for d in all_dirs if lmo_num.lower() in d.lower()]
                    
                    with open("debug_log.txt", "a") as f_dbg:
                        f_dbg.write(f"Search base: {base_path}\\n")
                        f_dbg.write(f"Search pma: {pma}\\n")
                        f_dbg.write(f"Search lmo_num: {lmo_num}\\n")
                        f_dbg.write(f"Search pma_path: {pma_path}\\n")
                        f_dbg.write(f"All dirs: {all_dirs}\\n")
                        f_dbg.write(f"Matches: {matches}\\n")

                    if len(matches) > 1:
                        return jsonify({"success": False, "requireLmoSelection": True, "options": matches})
                    elif len(matches) == 1:
                        lmo_num = matches[0]
                except Exception as e:
                    print("Error scanning for LMO folders:", e)
                    with open("debug_log.txt", "a") as f_dbg:
                        f_dbg.write(f"Search error: {e}\\n")
            else:
                with open("debug_log.txt", "a") as f_dbg:
                    f_dbg.write(f"Search pma_path DOES NOT EXIST: {pma_path}\\n")"""

content = content.replace(target, replace)
with open('backend/app.py', 'w') as f:
    f.write(content)
