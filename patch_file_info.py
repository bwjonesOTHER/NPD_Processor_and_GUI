import os
import sys

with open('backend/app.py', 'r') as f:
    content = f.read()

target = """    elif test == 2:
        pma = data.get('pmaArea', '').strip()
        sn = data.get('serialNumber', '').strip()
        lmo_num = data.get('lmoNumber', '').strip()
        write_txt("PMA_Area.txt", pma)
        write_txt("SN.txt", sn)
        write_txt("LMO_Number.txt", lmo_num)
        upload_path = base_path
        write_txt("upload_path.txt", upload_path)"""

replacement = """    elif test == 2:
        pma = data.get('pmaArea', '').strip()
        sn = data.get('serialNumber', '').strip()
        lmo_num = data.get('lmoNumber', '').strip()
        exact_lmo_folder = data.get('exactLmoFolder', '').strip()
        
        # If exactLmoFolder is provided, use it directly
        if exact_lmo_folder:
            lmo_num = exact_lmo_folder
        else:
            # Search for matching folders
            import glob
            pma_path = os.path.join(base_path, "BenchNPD", pma)
            if not os.path.exists(pma_path):
                # Fallback if BenchNPD isn't in the path explicitly
                pma_path = os.path.join(base_path, pma)
                
            if os.path.exists(pma_path):
                # Look for directories containing the LMO number
                try:
                    all_dirs = [d for d in os.listdir(pma_path) if os.path.isdir(os.path.join(pma_path, d))]
                    matches = [d for d in all_dirs if lmo_num in d]
                    
                    if len(matches) > 1:
                        return jsonify({"success": False, "requireLmoSelection": True, "options": matches})
                    elif len(matches) == 1:
                        lmo_num = matches[0]
                except Exception as e:
                    print("Error scanning for LMO folders:", e)
        
        write_txt("PMA_Area.txt", pma)
        write_txt("SN.txt", sn)
        write_txt("LMO_Number.txt", lmo_num)
        upload_path = base_path
        write_txt("upload_path.txt", upload_path)"""

if target in content:
    content = content.replace(target, replacement)
    with open('backend/app.py', 'w') as f:
        f.write(content)
    print("Patched app.py")
else:
    print("Could not find target block in app.py")
