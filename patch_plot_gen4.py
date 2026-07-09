with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

content = content.replace("                plt.ylim(0, 5)\n", "")
content = content.replace("                plt.ylim(0, 5)", "")

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)
