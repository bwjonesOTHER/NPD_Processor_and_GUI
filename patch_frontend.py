import re

with open('frontend/src/App.jsx', 'r') as f:
    content = f.read()

# Hide basePath input in Step 1 if uploadMode === 'upload'
target_basepath = """              <div className="form-group">
                <label>{testType === 2 ? 'BenchNPD Root Directory' : 'Base Upload Path'}</label>"""
replace_basepath = """              {uploadMode === 'access' && (
              <div className="form-group">
                <label>{testType === 2 ? 'BenchNPD Root Directory' : 'Base Upload Path'}</label>"""

content = content.replace(target_basepath, replace_basepath)

target_end_basepath = """                  }} className="secondary">Browse</button>
                </div>
              </div>"""
replace_end_basepath = """                  }} className="secondary">Browse</button>
                </div>
              </div>
              )}"""

content = content.replace(target_end_basepath, replace_end_basepath)

with open('frontend/src/App.jsx', 'w') as f:
    f.write(content)
