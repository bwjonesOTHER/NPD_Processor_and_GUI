import re
pma_area = "L110173C"
d = "AreaC"

pma_norm = re.sub(r'[^a-zA-Z0-9]', '', pma_area).lower()
d_norm = re.sub(r'[^a-zA-Z0-9]', '', d).lower()

match = pma_norm in d_norm

# Also check for "areaX" where X is the last char of pma_area
if not match and pma_norm:
    last_char = pma_norm[-1]
    if last_char.isalpha():
        expected_area = "area" + last_char
        if expected_area in d_norm:
            match = True
            
print("Match?", match)
