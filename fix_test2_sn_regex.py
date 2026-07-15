import re

with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

# Fix search_files exact SN matching
old_search = """                if serial_number:
                    import re
                    sn_clean = re.sub(r'^[SsnN0]+', '', serial_number)
                    if not sn_clean: sn_clean = serial_number
                    pattern = r'(?:SN|EM-)?0*' + re.escape(sn_clean) + r'(?!\d)'
                    if not re.search(pattern, file, re.IGNORECASE):
                        continue"""

new_search = """                if serial_number:
                    import re
                    sn_clean = re.sub(r'^[SsnN0]+', '', serial_number)
                    if not sn_clean: sn_clean = serial_number
                    # Negative lookbehind for digit, optional SN/EM- prefix, optional leading zeros, exact SN, negative lookahead for digit
                    pattern = r'(?<!\d)(?:SN|EM-)?0*' + re.escape(sn_clean) + r'(?!\d)'
                    if not re.search(pattern, file, re.IGNORECASE):
                        continue"""

content = content.replace(old_search, new_search)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
