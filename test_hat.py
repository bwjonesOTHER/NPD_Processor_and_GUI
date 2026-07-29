import sys
sys.path.append('backend')
from plot_generator import find_cal_file

search_dirs = [
    r"C:\Users\thomas.moore\Redwire Space\LON-10095.1-Macallan - Documents\03 - Technical\06 - Test & Demonstrations\06 Flight Phase Test Data\PMA Tile\NPDoverTemp\Run 9 LMO1208-62\Cap_01",
    r"C:\Users\thomas.moore\Redwire Space\LON-10095.1-Macallan - Documents\03 - Technical\06 - Test & Demonstrations\06 Flight Phase Test Data\PMA Tile\NPDoverTemp\Run 9 LMO1208-62",
    r"C:\Users\thomas.moore\Redwire Space\LON-10095.1-Macallan - Documents\03 - Technical\06 - Test & Demonstrations\06 Flight Phase Test Data\PMA Tile\NPDoverTemp"
]

f = find_cal_file(search_dirs, "34", "Hat")
print("With 34:", f)

f = find_cal_file(search_dirs, None, "Hat")
print("With None:", f)
