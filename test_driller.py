import re

def normalize(s):
    return re.sub(r'[^a-zA-Z0-9]', '', s).lower()

pma_area = "L110173C"
d = "L110173_C"

print("pma_area normalized:", normalize(pma_area))
print("d normalized:", normalize(d))
print("Match?", normalize(pma_area) in normalize(d))
