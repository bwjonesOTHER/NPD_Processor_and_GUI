import re

with open('src/App.jsx', 'r') as f:
    content = f.read()

# 1. Remove "Plot Output Destination" block in Step 2.
output_dest_pattern = r'<div style=\{\{ marginTop: \'1\.5rem\', marginBottom: \'1\.5rem\', padding: \'1rem\', background: \'rgba\(0,0,0,0\.2\)\', borderRadius: \'8px\', border: \'1px solid var\(--border\)\' \}\}>.*?</div>\s*</div>'
content = re.sub(output_dest_pattern, '', content, flags=re.DOTALL)

# 2. Remove "Save Plots to Destination" button
save_btn_pattern = r'<button onClick=\{handleSavePlots\}.*?</button>'
content = re.sub(save_btn_pattern, '', content, flags=re.DOTALL)

with open('src/App.jsx', 'w') as f:
    f.write(content)
