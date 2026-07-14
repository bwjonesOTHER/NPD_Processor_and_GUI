import re

with open('frontend/src/App.jsx', 'r') as f:
    content = f.read()

# 1. Add state variables
state_target = """  const [uploadMode, setUploadMode] = useState(null); // 'access' or 'upload'"""
state_replace = """  const [uploadMode, setUploadMode] = useState(null); // 'access' or 'upload'
  
  const [lmoOptions, setLmoOptions] = useState([]);
  const [showLmoModal, setShowLmoModal] = useState(false);"""
content = content.replace(state_target, state_replace)

# 2. Add exactLmoFolder to formData
form_target = """    pmaArea: '',
    runEntry: '',
  });"""
form_replace = """    pmaArea: '',
    runEntry: '',
    exactLmoFolder: '',
  });"""
content = content.replace(form_target, form_replace)

# 3. Update submitFileInfo
submit_target = """  const submitFileInfo = async () => {
    try {
      const res = await fetch(`${API_BASE}/file-info`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          testType,
          ...formData
        })
      });
      if (res.ok) {
        // Validation passed in backend, now we decide where to go (Upload or Access, handled by the button click directly)
      }
    } catch (err) {
      console.error(err);
      alert("Failed to submit file info");
    }
  };"""

submit_replace = """  const submitFileInfo = async () => {
    try {
      const res = await fetch(`${API_BASE}/file-info`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          testType,
          ...formData
        })
      });
      if (res.ok) {
        const data = await res.json().catch(() => ({}));
        if (data.requireLmoSelection) {
          setLmoOptions(data.options || []);
          setShowLmoModal(true);
          return { success: false, requireLmoSelection: true };
        }
        return { success: true };
      }
      return { success: false };
    } catch (err) {
      console.error(err);
      alert("Failed to submit file info");
      return { success: false };
    }
  };"""
content = content.replace(submit_target, submit_replace)

# 4. Update the onClick for testType === 2
onclick_target = """                    <button onClick={async () => {
                      if (!formData.basePath) {
                        alert("Please select the BenchNPD Root Directory before continuing.");
                        return;
                      }
                      await submitFileInfo();
                      setCurrentStep(4);
                    }} className="primary" style={{ background: 'var(--success)' }}>Proceed to Configuration <ChevronRight size={18} style={{ verticalAlign: 'middle' }} /></button>"""

onclick_replace = """                    <button onClick={async () => {
                      if (!formData.basePath) {
                        alert("Please select the BenchNPD Root Directory before continuing.");
                        return;
                      }
                      const result = await submitFileInfo();
                      if (result && result.requireLmoSelection) return;
                      if (result && result.success) setCurrentStep(4);
                    }} className="primary" style={{ background: 'var(--success)' }}>Proceed to Configuration <ChevronRight size={18} style={{ verticalAlign: 'middle' }} /></button>"""
content = content.replace(onclick_target, onclick_replace)

# 5. Update the onClick for testType === 1
onclick_t1_target = """                      <button onClick={async () => {
                        if (!formData.basePath) {
                          alert("Please select a Base Upload Path before continuing.");
                          return;
                        }
                        await submitFileInfo();
                        setCurrentStep(2);
                      }} className="primary">Upload Files <Upload size={18} style={{ verticalAlign: 'middle' }} /></button>"""

onclick_t1_replace = """                      <button onClick={async () => {
                        if (!formData.basePath) {
                          alert("Please select a Base Upload Path before continuing.");
                          return;
                        }
                        const result = await submitFileInfo();
                        if (result && result.success) setCurrentStep(2);
                      }} className="primary">Upload Files <Upload size={18} style={{ verticalAlign: 'middle' }} /></button>"""
content = content.replace(onclick_t1_target, onclick_t1_replace)

with open('frontend/src/App.jsx', 'w') as f:
    f.write(content)
