import re

tests = ['SN0014', 'SN114', 'SN214', '14', '0014', 'EM-14', 'SN00145', 'SN14', 'SN00014_hot']

sn_clean = '14'
pattern1 = r'(?:SN|EM-)?0*' + re.escape(sn_clean) + r'(?!\d)'
pattern2 = r'(?<!\d)(?:SN|EM-)?0*' + re.escape(sn_clean) + r'(?!\d)'
pattern3 = r'(?:^|[^0-9a-zA-Z])(?:SN|EM-)?0*' + re.escape(sn_clean) + r'(?!\d)'

print("Pattern 1 (Old):", pattern1)
for t in tests:
    print(t, "->", bool(re.search(pattern1, t, re.IGNORECASE)))

print("\Pattern 3 (New):", pattern3)
for t in tests:
    print(t, "->", bool(re.search(pattern3, t, re.IGNORECASE)))

