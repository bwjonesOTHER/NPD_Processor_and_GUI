import re

with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

content = content.replace(
    'raw_sparA = search_files(search_dirA, ".s2p", sn)',
    'raw_sparA = search_files(search_dirA, ".s2p", sn)\n        if not raw_sparA and sn: raw_sparA = search_files(search_dirA, ".s2p", "")'
)

content = content.replace(
    'raw_npdA = search_files(search_dirA, ".csv", sn)',
    'raw_npdA = search_files(search_dirA, ".csv", sn)\n        if not raw_npdA and sn: raw_npdA = search_files(search_dirA, ".csv", "")'
)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
