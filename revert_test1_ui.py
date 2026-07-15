import re

with open('frontend/src/App.jsx', 'r') as f:
    content = f.read()

# Revert Step 3 UI completely
old_step3 = """              {(testType === 1 || testType === 3) && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                  {uploadMode === 'access' ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      <p style={{ color: 'var(--text-muted)' }}>Select the local folders on your hard drive.</p>
                      
                      {/* Run A */}
                      <div className="form-group">
                        <label>Run A Directory</label>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <input type="text" readOnly value={runs[0] || ''} placeholder="Select Run A folder..." style={{ flex: 1 }} />
                          <button onClick={async () => {
                            try {
                              const res = await fetch(`${API_BASE}/choose_directory`);
                              const data = await res.json();
                              if (data.success && data.path) {
                                setRuns(prev => { const n = [...prev]; n[0] = data.path; return n; });
                                setRunNames(prev => { const n = [...prev]; n[0] = data.path.split(/[\\\\/]/).pop(); return n; });
                              }
                            } catch (err) { console.error(err); }
                          }} className="secondary">Browse</button>
                        </div>
                      </div>
                      
                      {/* Run B */}
                      <div className="form-group">
                        <label>Run B Directory</label>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <input type="text" readOnly value={runs[1] || ''} placeholder="Select Run B folder..." style={{ flex: 1 }} />
                          <button onClick={async () => {
                            try {
                              const res = await fetch(`${API_BASE}/choose_directory`);
                              const data = await res.json();
                              if (data.success && data.path) {
                                setRuns(prev => { const n = [...prev]; n[1] = data.path; return n; });
                                setRunNames(prev => { const n = [...prev]; n[1] = data.path.split(/[\\\\/]/).pop(); return n; });
                              }
                            } catch (err) { console.error(err); }
                          }} className="secondary">Browse</button>
                        </div>
                      </div>
                      
                    </div>
                  ) : (
                  <div 
                    style={{
                      border: '2px dashed var(--border-color)',"""

new_step3 = """              {(testType === 1 || testType === 3) && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                  <div 
                    style={{
                      border: '2px dashed var(--border-color)',"""

content = content.replace(old_step3, new_step3)

old_end_step3 = """                        if (test1RunsInputRef.current) test1RunsInputRef.current.value = "";
                        setUploadingRun(false);
                      }} 
                    />
                  </div>
                  )}"""

new_end_step3 = """                        if (test1RunsInputRef.current) test1RunsInputRef.current.value = "";
                        setUploadingRun(false);
                      }} 
                    />
                  </div>"""
content = content.replace(old_end_step3, new_end_step3)

with open('frontend/src/App.jsx', 'w') as f:
    f.write(content)
