import sys
import re

with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

# Change NPDOverTempVSWR to VSWR
content = content.replace("'NPDOverTempVSWR'", "'VSWR'")
content = content.replace("'NPDOverTempVSWR_ambient'", "'VSWR_ambient'")
content = content.replace("'NPDOverTempVSWR_hot'", "'VSWR_hot'")
content = content.replace("'NPDOverTempVSWR_cold'", "'VSWR_cold'")

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)

