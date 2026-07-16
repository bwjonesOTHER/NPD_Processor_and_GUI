import re

with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

# Add fallbacks for raw_sparA, raw_npdA, raw_sparB, raw_npdB in the else block
content = content.replace(
    'raw_sparA = search_files(search_dirA, ".s2p", sn)',
    'raw_sparA = search_files(search_dirA, ".s2p", sn)\n        if not raw_sparA and sn: raw_sparA = search_files(search_dirA, ".s2p", "")'
)

content = content.replace(
    'raw_npdA = search_files(search_dirA, ".csv", sn)',
    'raw_npdA = search_files(search_dirA, ".csv", sn)\n        if not raw_npdA and sn: raw_npdA = search_files(search_dirA, ".csv", "")'
)

content = content.replace(
    'raw_sparB = search_files(search_dirB, ".s2p", sn)',
    'raw_sparB = search_files(search_dirB, ".s2p", sn)\n        if not raw_sparB and sn: raw_sparB = search_files(search_dirB, ".s2p", "")'
)

content = content.replace(
    'raw_npdB = search_files(search_dirB, ".csv", sn)',
    'raw_npdB = search_files(search_dirB, ".csv", sn)\n        if not raw_npdB and sn: raw_npdB = search_files(search_dirB, ".csv", "")'
)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
