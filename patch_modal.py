import re

with open('frontend/src/App.jsx', 'r') as f:
    content = f.read()

modal_ui = """
      {/* LMO Selection Modal */}
      {showLmoModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 9999,
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <div style={{
            background: 'var(--surface)', padding: '2rem', borderRadius: '12px',
            width: '400px', maxWidth: '90%', boxShadow: '0 10px 30px rgba(0,0,0,0.3)'
          }}>
            <h3 style={{ marginTop: 0, color: 'var(--text-primary)' }}>Multiple LMO Folders Found</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
              We found multiple folders matching that LMO number. Please select the correct one:
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '300px', overflowY: 'auto' }}>
              {lmoOptions.map(opt => (
                <button 
                  key={opt}
                  className="secondary" 
                  style={{ textAlign: 'left', padding: '0.75rem', justifyContent: 'flex-start' }}
                  onClick={async () => {
                    const newFormData = { ...formData, exactLmoFolder: opt };
                    setFormData(newFormData);
                    setShowLmoModal(false);
                    
                    // Re-submit with the exact folder
                    try {
                      const res = await fetch(`${API_BASE}/file-info`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ testType, ...newFormData })
                      });
                      if (res.ok) {
                        const data = await res.json().catch(() => ({}));
                        if (!data.requireLmoSelection) {
                          setCurrentStep(4);
                        }
                      }
                    } catch(err) {
                      console.error(err);
                    }
                  }}
                >
                  <Folder size={16} style={{ marginRight: '0.5rem', verticalAlign: 'middle', color: 'var(--primary)' }} />
                  {opt}
                </button>
              ))}
            </div>
            <div style={{ marginTop: '1.5rem', textAlign: 'right' }}>
              <button className="secondary" onClick={() => setShowLmoModal(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
"""

content = content.replace("    </div>\n  );\n}", modal_ui)

with open('frontend/src/App.jsx', 'w') as f:
    f.write(content)
