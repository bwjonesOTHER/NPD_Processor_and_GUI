import re

tests = ['EdgeSN0014', 'Edge0014', '_SN0014']
sn_clean = '14'
pattern3 = r'(?:^|[^0-9a-zA-Z])(?:SN|EM-)?0*' + re.escape(sn_clean) + r'(?!\d)'
pattern4 = r'(?<!\d)(?:SN|EM-)?0*' + re.escape(sn_clean) + r'(?!\d)'

print("\Pattern 3:")
for t in tests:
    print(t, "->", bool(re.search(pattern3, t, re.IGNORECASE)))

print("\Pattern 4:")
for t in tests:
    print(t, "->", bool(re.search(pattern4, t, re.IGNORECASE)))

