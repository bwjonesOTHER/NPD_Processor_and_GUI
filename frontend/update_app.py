import re

with open('src/App.jsx', 'r') as f:
    content = f.read()

# 1. Remove Step 0 Access vs Upload buttons.
# We replace the Step 0 btn-group with a single "Next" button.
btn_group_pattern = r'<div className="btn-group" style={{ display: \'flex\', gap: \'1rem\', justifyContent: \'flex-end\', width: \'100%\' }}>.*?</div>'
replacement_btn_group = """<div className="btn-group" style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', width: '100%' }}>
                <button onClick={() => setCurrentStep(1)} disabled={!testType} className="primary">
                  Next <ChevronRight size={18} style={{ verticalAlign: 'middle' }} />
                </button>
              </div>"""
content = re.sub(btn_group_pattern, replacement_btn_group, content, count=1, flags=re.DOTALL)

# 2. We need to replace Step 1 contents.
# Step 1 starts at `{currentStep === 1 && (` and ends right before `{currentStep === 2 && (`
step1_pattern = r'\{currentStep === 1 && \(\s*<div className="step-card">.*?\{currentStep === 2 && \('

new_step1 = r"""{currentStep === 1 && (
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
                    <label>Calibration Files Folder (Optional)</label>
                    <input type="file" webkitdirectory="true" directory="true" multiple onChange={(e) => setTest2Files(prev => ({...prev, cal: e.target.files}))} />
                  </div>
                </>
              ) : (
                <>
                  <div className="form-group">
                    <label>Test Data Folder</label>
                    <input type="file" webkitdirectory="true" directory="true" multiple onChange={(e) => setGeneralFiles(e.target.files)} />
                  </div>
                  
                  {testType === 1 && (
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
                    </>
                  )}
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

          {currentStep === 2 && ("""

content = re.sub(step1_pattern, new_step1, content, count=1, flags=re.DOTALL)

with open('src/App.jsx', 'w') as f:
    f.write(content)
