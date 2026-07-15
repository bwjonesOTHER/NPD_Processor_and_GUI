import re
test_str = '1P_Macallan_PMA Tile_EdgeSN0014_2600-4200MHz_NFDirect_65pts_Single Point_2026.03.26.11.16.37.csv'
sn_clean = '14'
pattern = r'(?<!\d)(?:SN|EM-)?0*' + re.escape(sn_clean) + r'(?!\d)'
print("Match:", bool(re.search(pattern, test_str, re.IGNORECASE)))
