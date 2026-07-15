import re

with open('frontend/src/App.jsx', 'r') as f:
    content = f.read()

# Fix basePath input visibility
old_input = """              {uploadMode !== 'upload' && (
                <div className="form-group">
                  <label>{testType === 2 ? 'BenchNPD Root Directory' : 'Base Source Path'}</label>"""

new_input = """              {uploadMode !== 'upload' && testType !== 1 && (
                <div className="form-group">
                  <label>{testType === 2 ? 'BenchNPD Root Directory' : 'Base Source Path'}</label>"""

content = content.replace(old_input, new_input)


# Fix validation for Test 1/3 buttons
old_val13 = """                    <>
                      <button onClick={async () => {
                        if (uploadMode !== 'upload' && !formData.basePath) {"""

new_val13 = """                    <>
                      <button onClick={async () => {
                        if (uploadMode !== 'upload' && testType !== 1 && !formData.basePath) {"""

content = content.replace(old_val13, new_val13)

old_val13b = """                      <button onClick={async () => {
                        if (uploadMode !== 'upload' && !formData.basePath) {"""

new_val13b = """                      <button onClick={async () => {
                        if (uploadMode !== 'upload' && testType !== 1 && !formData.basePath) {"""

content = content.replace(old_val13b, new_val13b)

with open('frontend/src/App.jsx', 'w') as f:
    f.write(content)
