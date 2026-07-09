with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

old_spar = """    spar_all = _collect_files(runs, '*VSWR*.s2p')
    spar_25C = _collect_files(runs, '*VSWR*ambient*.s2p')
    spar_64C = _collect_files(runs, '*VSWR*hot*.s2p')
    spar_n38C = _collect_files(runs, '*VSWR*cold*.s2p')"""

new_spar = """    spar_all = _collect_files(runs, '*VSWR*', '.s2p')
    spar_25C = _collect_files(runs, '*VSWR*ambient*', '.s2p')
    spar_64C = _collect_files(runs, '*VSWR*hot*', '.s2p')
    spar_n38C = _collect_files(runs, '*VSWR*cold*', '.s2p')"""

content = content.replace(old_spar, new_spar)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
