import re

with open('frontend/src/App.jsx', 'r') as f:
    content = f.read()

# Fix the JSX for basePath input
old_input = """              <div className="form-group">
                <label>{testType === 2 ? 'BenchNPD Root Directory' : 'Base Upload Path'}</label>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <input type="text" name="basePath" value={formData.basePath} onChange={handleInputChange} placeholder={testType === 2 && uploadMode === 'upload' ? 'Select the root project folder (e.g. PMA Tile)...' : testType === 2 ? 'Select BenchNPD root folder...' : 'Select a directory to upload files into...'} style={{ flex: 1 }} />
                  <button onClick={async () => {
                    try {
                      const res = await fetch(`${API_BASE}/choose_directory`);
                      const data = await res.json();
                      if (data.success && data.path) {
                        setFormData(prev => ({...prev, basePath: data.path}));
                      }
                    } catch (err) {
                      console.error("Failed to choose directory:", err);
                    }
                  }} className="secondary">Browse</button>
                </div>
              </div>"""

new_input = """              {uploadMode !== 'upload' && (
                <div className="form-group">
                  <label>{testType === 2 ? 'BenchNPD Root Directory' : 'Base Source Path'}</label>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <input type="text" name="basePath" value={formData.basePath} onChange={handleInputChange} placeholder={testType === 2 ? 'Select BenchNPD root folder...' : 'Select a directory to read files from...'} style={{ flex: 1 }} />
                    <button onClick={async () => {
                      try {
                        const res = await fetch(`${API_BASE}/choose_directory`);
                        const data = await res.json();
                        if (data.success && data.path) {
                          setFormData(prev => ({...prev, basePath: data.path}));
                        }
                      } catch (err) {
                        console.error("Failed to choose directory:", err);
                      }
                    }} className="secondary">Browse</button>
                  </div>
                </div>
              )}"""
content = content.replace(old_input, new_input)

# Fix validation for Test 2
old_val2 = """                    <button onClick={async () => {
                      if (!formData.basePath) {
                        alert(`Please select the ${uploadMode === 'upload' ? 'Base Upload Directory' : 'BenchNPD Root Directory'} before continuing.`);
                        return;
                      }"""

new_val2 = """                    <button onClick={async () => {
                      if (uploadMode !== 'upload' && !formData.basePath) {
                        alert(`Please select the BenchNPD Root Directory before continuing.`);
                        return;
                      }"""
content = content.replace(old_val2, new_val2)

# Fix validation for Test 1/3
old_val13 = """                    <>
                      <button onClick={async () => {
                        if (!formData.basePath) {
                          alert("Please select a Base Upload Path before continuing.");
                          return;
                        }"""

new_val13 = """                    <>
                      <button onClick={async () => {
                        if (uploadMode !== 'upload' && !formData.basePath) {
                          alert("Please select a Base Source Path before continuing.");
                          return;
                        }"""
content = content.replace(old_val13, new_val13)

old_val13b = """                      <button onClick={async () => {
                        if (!formData.basePath) {
                          alert("Please select a Base Upload Path before continuing.");
                          return;
                        }"""
new_val13b = """                      <button onClick={async () => {
                        if (uploadMode !== 'upload' && !formData.basePath) {
                          alert("Please select a Base Source Path before continuing.");
                          return;
                        }"""
content = content.replace(old_val13b, new_val13b)

# Fix validation for Upload files button
old_upload_btn = """<button onClick={uploadFiles} disabled={files.length === 0 || (testType === 2 && !formData.basePath)} className="primary">Upload Files</button>"""
new_upload_btn = """<button onClick={uploadFiles} disabled={files.length === 0 || (testType === 2 && uploadMode !== 'upload' && !formData.basePath)} className="primary">Upload Files</button>"""
content = content.replace(old_upload_btn, new_upload_btn)

with open('frontend/src/App.jsx', 'w') as f:
    f.write(content)

