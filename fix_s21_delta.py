content = open('backend/plot_generator.py', 'r').read()

old_delta_bounds = """    # ax3: S21 delta (0 to 5)
    ax3.set_xlabel('Frequency (GHz)')
    ax3.set_ylabel('S21 Delta (dB)')
    ax3.grid(True)
    ax3.set_ylim(0, 5)"""

new_delta_bounds = """    # ax3: S21 delta (-40 to 40)
    ax3.set_xlabel('Frequency (GHz)')
    ax3.set_ylabel('S21 Delta (dB)')
    ax3.grid(True)
    ax3.set_ylim(-40, 40)"""

content = content.replace(old_delta_bounds, new_delta_bounds)
open('backend/plot_generator.py', 'w').write(content)
