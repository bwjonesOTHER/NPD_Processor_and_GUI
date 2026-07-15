content = open('backend/plot_generator.py', 'r').read()

old_s21_bounds = """    if test_type != 1:
        plt.ylim(0, 30)
        title = f'S21 Calibrated {title_suffix}, {status}'
    else:
        title = f'S21 {title_suffix}, {status}'"""
new_s21_bounds = """    if test_type != 1:
        plt.ylim(0, 30)
        title = f'S21 Calibrated {title_suffix}, {status}'
    else:
        plt.ylim(-40, 40)
        title = f'S21 {title_suffix}, {status}'"""

content = content.replace(old_s21_bounds, new_s21_bounds)
open('backend/plot_generator.py', 'w').write(content)
