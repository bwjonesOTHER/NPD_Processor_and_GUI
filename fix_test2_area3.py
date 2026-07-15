with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

old_pma = """            def get_pma_folder(base_d, pma_area):
                if not pma_area or not os.path.exists(base_d): return None
                import re
                pma_norm = re.sub(r'[^a-zA-Z0-9]', '', pma_area).lower()
                for d in os.listdir(base_d):
                    d_norm = re.sub(r'[^a-zA-Z0-9]', '', d).lower()
                    if os.path.isdir(os.path.join(base_d, d)) and pma_norm in d_norm:
                        return os.path.join(base_d, d)
                # If a specific PMA Area was requested but we couldn't find its folder, 
                # just return the base directory (e.g. OverTemp might not have Area subfolders)
                return base_d"""

new_pma = """            def get_pma_folder(base_d, pma_area):
                if not pma_area or not os.path.exists(base_d): return None
                import re
                pma_norm = re.sub(r'[^a-zA-Z0-9]', '', pma_area).lower()
                for d in os.listdir(base_d):
                    if not os.path.isdir(os.path.join(base_d, d)): continue
                    d_norm = re.sub(r'[^a-zA-Z0-9]', '', d).lower()
                    match = pma_norm in d_norm
                    if not match and pma_norm:
                        last_char = pma_norm[-1]
                        if last_char.isalpha():
                            if f"area{last_char}" in d_norm:
                                match = True
                    if match:
                        return os.path.join(base_d, d)
                # If a specific PMA Area was requested but we couldn't find its folder, 
                # just return the base directory (e.g. OverTemp might not have Area subfolders)
                return base_d"""

content = content.replace(old_pma, new_pma)
with open('backend/plot_generator.py', 'w') as f:
    f.write(content)

