import re

with open('backend/app.py', 'r') as f:
    content = f.read()

target = """                    matches = [d for d in all_dirs if lmo_num.lower() in d.lower()]
                    
                    with open("debug_log.txt", "a") as f_dbg:"""

replace = """                    matches = [d for d in all_dirs if lmo_num.lower() in d.lower()]
                    
                    # Filter by SN if provided
                    if sn:
                        filtered_matches = []
                        for match in matches:
                            match_path = os.path.join(pma_path, match)
                            found_sn = False
                            for root, dirs, files in os.walk(match_path):
                                if any(sn in f for f in files) or any(sn in d for d in dirs):
                                    found_sn = True
                                    break
                            if found_sn:
                                filtered_matches.append(match)
                        
                        with open("debug_log.txt", "a") as f_dbg:
                            f_dbg.write(f"Original matches: {matches}\\n")
                            f_dbg.write(f"Filtered by SN '{sn}': {filtered_matches}\\n")
                        
                        # Only apply the filter if it found at least one match (to avoid breaking things if SN format was weird)
                        if len(filtered_matches) > 0:
                            matches = filtered_matches
                    
                    with open("debug_log.txt", "a") as f_dbg:"""

content = content.replace(target, replace)

with open('backend/app.py', 'w') as f:
    f.write(content)

