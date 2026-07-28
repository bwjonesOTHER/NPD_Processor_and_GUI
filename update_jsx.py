import sys
import re

with open('frontend/src/App.jsx', 'r') as f:
    content = f.read()

# Replace the entire Step 1, 2, and 3 blocks.
start_step1 = content.find('{currentStep === 1 && (')
start_step4 = content.find('{currentStep === 4 && (')

if start_step1 == -1 or start_step4 == -1:
    print("Could not find step 1 or 4")
    sys.exit(1)

new_step1 = """
          {currentStep === 1 && (
            <div className="step-card">
              <h2>Data Source & Info</h2>
              <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Upload your test data and provide metadata.</p>

              {testType === 2 ? (
                <>
                  <div className="form-group">
                    <label>Bench Data Folder (Required)</label>
                    <input type="file" webkitdirectory="true" directory="true" multiple onChange={(e) => setTest2Files(prev => ({...prev, bench: e.target.files}))} />
                  </div>
                  <div className="form-group">
                    <label>Temp Data Folder (Optional)</label>
                    <input type="file" webkitdirectory="true" directory="true" multiple onChange={(e) => setTest2Files(prev => ({...prev, temp: e.target.files}))} />
                  </div>
                  <div className="form-group">
                    <label>Bench Calibration Files Folder (Optional)</label>
                    <input type="file" webkitdirectory="true" directory="true" multiple onChange={(e) => setTest2Files(prev => ({...prev, cal: e.target.files}))} />
                  </div>
                  <div className="form-group">
                    <label>Temp Calibration Files Folder (Optional)</label>
                    <input type="file" webkitdirectory="true" directory="true" multiple onChange={(e) => setTest2Files(prev => ({...prev, tempCal: e.target.files}))} />
                  </div>
                </>
              ) : testType === 3 ? (
                <>
                  <div className="form-group">
                    <label>Run 1 (Run A) Folder</label>
                    <input type="file" webkitdirectory="true" directory="true" multiple onChange={(e) => setTest3Files(prev => ({...prev, runA: e.target.files}))} />
                  </div>
                  <div className="form-group">
                    <label>Run 2 (Run B) Folder</label>
                    <input type="file" webkitdirectory="true" directory="true" multiple onChange={(e) => setTest3Files(prev => ({...prev, runB: e.target.files}))} />
                  </div>
                  <div className="form-group">
                    <label>Calibration (Cable Loss) Folder</label>
                    <input type="file" webkitdirectory="true" directory="true" multiple onChange={(e) => setTest3Files(prev => ({...prev, cal: e.target.files}))} />
                  </div>
                </>
              ) : testType === 4 ? (
                <>
                  <div className="form-group">
                    <label>Test Data Folder</label>
                    <input type="file" webkitdirectory="true" directory="true" multiple onChange={(e) => setGeneralFiles(e.target.files)} />
                  </div>
                </>
              ) : (
                <>
                  <div className="form-group">
                    <label>Run Number (#)</label>
                    <input type="text" name="runNumber" value={formData.runNumber} onChange={handleInputChange} />
                  </div>
                  <div className="form-group">
                    <label>Cap Number (##)</label>
                    <input type="text" name="capNumber" value={formData.capNumber} onChange={handleInputChange} />
                  </div>
                  <div className="form-group">
                    <label>LMO Number (####-##)</label>
                    <input type="text" name="lmoNumber" value={formData.lmoNumber} onChange={handleInputChange} />
                  </div>
                  
                  <div className="form-group" style={{ marginTop: '2rem' }}>
                    <label style={{ fontSize: '1.1rem', marginBottom: '1rem', display: 'block' }}>Upload Run Folders</label>
                    
                    <div 
                      style={{
                        border: '2px dashed var(--border-color)',
                        borderRadius: '12px',
                        padding: '2rem',
                        textAlign: 'center',
                        cursor: uploadingRun ? 'not-allowed' : 'pointer',
                        background: 'var(--panel-bg)',
                        transition: 'background 0.2s',
                        opacity: uploadingRun ? 0.7 : 1,
                        marginBottom: '1rem'
                      }}
                      onClick={() => {
                        !uploadingRun && test1RunsInputRef.current?.click();
                      }}
                    >
                      {uploadingRun ? (
                        <Activity size={30} className="spinner" color="var(--accent)" style={{marginBottom: '0.5rem'}} />
                      ) : (
                        <UploadCloud size={30} color="var(--accent)" style={{marginBottom: '0.5rem'}} />
                      )}
                      <div>
                        <strong style={{ fontSize: '1rem', color: 'var(--text-main)' }}>
                          {uploadingRun ? "Uploading..." : "Click to select and upload a run folder"}
                        </strong>
                        {!uploadingRun && <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                          (Click multiple times to add more runs!)
                        </p>}
                      </div>
                      <input 
                        type="file" 
                        webkitdirectory="true" 
                        directory="true"
                        multiple={true}
                        ref={test1RunsInputRef} 
                        style={{ display: 'none' }} 
                        onChange={async (e) => {
                            if (!e.target.files || e.target.files.length === 0) return;
                            setUploadingRun(true);
                            const filesArray = filterValidFiles(e.target.files);
                            
                            if (filesArray.length === 0) {
                              setUploadingRun(false);
                              alert("No valid data files (.csv, .xlsx, etc.) found in the selected folder.");
                              return;
                            }
                            
                            const validRuns = runs.filter(r => r !== '');
                            const runIndex = validRuns.length;
                            
                            try {
                              const CHUNK_SIZE = 50;
                              let finalUploadPath = '';
                              
                              for (let i = 0; i < filesArray.length; i += CHUNK_SIZE) {
                                const chunk = filesArray.slice(i, i + CHUNK_SIZE);
                                const data = new FormData();
                                
                                chunk.forEach(f => {
                                  data.append('files', f);
                                  data.append('paths', f.webkitRelativePath || f.name);
                                });
                                
                                data.append('run_index', runIndex);
                                const extractedFolderName = filesArray[0].webkitRelativePath ? filesArray[0].webkitRelativePath.split('/')[0] : '';
                                if (extractedFolderName) {
                                  data.append('folder_name', extractedFolderName);
                                }
                                data.append('chunk_index', i === 0 ? '0' : '1');
                                data.append('testType', testType);
                                
                                const res = await fetch(`${API_BASE}/upload_run`, { method: 'POST', body: data });
                                if (!res.ok) {
                                  const errText = await res.text();
                                  throw new Error(`HTTP ${res.status}: ${errText}`);
                                }
                                
                                const json = await res.json();
                                if (json.status !== 'success') {
                                  throw new Error(json.error || 'Upload failed');
                                }
                                finalUploadPath = json.upload_path;
                              }
                              
                              const folderName = filesArray[0].webkitRelativePath ? filesArray[0].webkitRelativePath.split('/')[0] : filesArray[0].name;
                              setRuns([...validRuns, finalUploadPath]);
                              setRunNames(prev => {
                                const newNames = [...prev];
                                newNames[runIndex] = folderName;
                                return newNames;
                              });
                            } catch (err) {
                              console.error(err);
                              alert("Upload error: " + err.message);
                            }
                            if (test1RunsInputRef.current) test1RunsInputRef.current.value = "";
                            setUploadingRun(false);
                          }} 
                        />
                    </div>

                    {runs.filter(r => r !== '').length > 0 && (
                      <div style={{ background: 'var(--panel-bg)', padding: '1rem', borderRadius: '8px' }}>
                        <h3 style={{ marginBottom: '0.75rem', fontSize: '1rem' }}>Added Folders ({runs.filter(r => r !== '').length})</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                          {runs.filter(r => r !== '').map((runPath, idx) => (
                            <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-main)', padding: '0.5rem 0.75rem', borderRadius: '6px' }}>
                              <span style={{ fontSize: '0.85rem', color: 'var(--text-main)', wordBreak: 'break-all' }}>
                                <strong>{runNames[idx] || `Run ${idx + 1}: `}</strong> 
                                {runPath.split(/[\\\\/]/).pop() || runPath}
                              </span>
                              <button 
                                className="icon-btn" 
                                onClick={() => {
                                  setRuns(prev => prev.filter(r => r !== '').filter((_, i) => i !== idx));
                                  setRunNames(prev => prev.filter((_, i) => i !== idx));
                                }}
                                style={{ color: '#ff6b6b', background: 'none', border: 'none', cursor: 'pointer', padding: '0.25rem' }}
                                title="Remove Run"
                              >
                                <XCircle size={16} />
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </>
              )}

              <div className="btn-group" style={{ display: 'flex', gap: '1rem', justifyContent: 'space-between', marginTop: '2rem' }}>
                <button onClick={() => setCurrentStep(0)} className="secondary">
                  <ChevronLeft size={18} style={{ verticalAlign: 'middle' }} /> Back
                </button>
                <button onClick={handleDataUpload} disabled={isUploadingSource} className="primary" style={{ background: 'var(--success)' }}>
                  {isUploadingSource ? 'Uploading...' : 'Upload & Proceed'} <ChevronRight size={18} style={{ verticalAlign: 'middle' }} />
                </button>
              </div>
            </div>
          )}
"""

content = content[:start_step1] + new_step1 + "\n" + content[start_step4:]

with open('frontend/src/App.jsx', 'w') as f:
    f.write(content)
