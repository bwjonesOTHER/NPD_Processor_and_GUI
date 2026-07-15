import re

with open('frontend/src/App.jsx', 'r') as f:
    content = f.read()

# 1. Revert UI text back to "Upload folders in order..." for Test 3 only
content = content.replace(
    '{(testType === 3 || testType === 1) ? "(Upload folders in order: Run A, then Run B, then CalibrationFiles (Optional))" : "(Click multiple times to add more runs!)"}',
    '{testType === 3 ? "(Upload folders in order: Run A, then Run B, then Calibration)" : "(Click multiple times to add more runs!)"}'
)

content = content.replace(
    """                          runs.filter(r => r !== '').length === 0 ? "Click to select Run A folder" :
                          runs.filter(r => r !== '').length === 1 ? "Click to select Run B folder" :
                          "Click to select Calibration (Optional) folder"
                        ) : "Click to select and upload a run folder"}""",
    """                          runs.filter(r => r !== '').length === 0 ? "Click to select Run A folder" :
                          runs.filter(r => r !== '').length === 1 ? "Click to select Run B folder" :
                          "Click to select Calibration (Cable Loss) folder"
                        ) : "Click to select and upload a run folder"}"""
)

content = content.replace(
    """                                {(testType === 3 || testType === 1)
                                  ? (idx === 0 ? 'Run A: ' : idx === 1 ? 'Run B: ' : 'Calibration: ') 
                                  : (runNames[idx] || `Run ${idx + 1}: `)}""",
    """                                {testType === 3 
                                  ? (idx === 0 ? 'Run A: ' : idx === 1 ? 'Run B: ' : 'Calibration: ') 
                                  : (runNames[idx] || `Run ${idx + 1}: `)}"""
)

# 2. Remove the 3rd Browse button for Test 1 Access mode
old_browse = """                      {/* Calibration Files */}
                      <div className="form-group">
                        <label>CalibrationFiles Directory (Optional)</label>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <input type="text" readOnly value={runs[2] || ''} placeholder="Select CalibrationFiles folder (Optional)..." style={{ flex: 1 }} />
                          <button onClick={async () => {
                            try {
                              const res = await fetch(`${API_BASE}/choose_directory`);
                              const data = await res.json();
                              if (data.success && data.path) {
                                setRuns(prev => { const n = [...prev]; n[2] = data.path; return n; });
                                setRunNames(prev => { const n = [...prev]; n[2] = data.path.split(/[\\\\/]/).pop(); return n; });
                              }
                            } catch (err) { console.error(err); }
                          }} className="secondary">Browse</button>
                        </div>
                      </div>"""

content = content.replace(old_browse, "")

with open('frontend/src/App.jsx', 'w') as f:
    f.write(content)
