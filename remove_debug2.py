content = open('backend/plot_generator.py', 'r').readlines()
new_content = [line for line in content if 'DEBUG' not in line]
open('backend/plot_generator.py', 'w').writelines(new_content)
