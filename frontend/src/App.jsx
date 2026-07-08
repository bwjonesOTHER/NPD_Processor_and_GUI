import React, { useState, useRef, useEffect } from 'react';
import { Upload, CheckCircle, Terminal, Play, Server, ChevronRight, Activity } from 'lucide-react';
import './App.css';

const API_BASE = 'http://127.0.0.1:5000/api';

function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [testType, setTestType] = useState(null);
  const [isConnected, setIsConnected] = useState(true); // Always true now since we removed SharePoint
  const [isProcessing, setIsProcessing] = useState(false);
  const [images, setImages] = useState([]);
  const [error, setError] = useState('');
  
  // Form state
  const [formData, setFormData] = useState({
    basePath: '',
    lmoNumber: '',
    runNumber: '',
    capNumber: '',
    serialNumber: '',
    pmaArea: '',
    runEntry: '',
  });

  const [plotParams, setPlotParams] = useState({
    freq_min: 2.7,
    freq_max: 4.1,
    reqS11Val: -10,
    reqS21Val: -14,
    n_avg: 20,
    u_bound_s21: 2,
    l_bound_s21: 2,
    u_bound_npd: 2,
    l_bound_npd: 2,
  });

  const [files, setFiles] = useState([]);
  const [folders, setFolders] = useState([]);
  const [runA, setRunA] = useState('');
  const [runB, setRunB] = useState('');





  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handlePlotParamChange = (e) => {
    const { name, value } = e.target;
    setPlotParams(prev => ({ ...prev, [name]: value }));
  };





  const submitFileInfo = async () => {
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
  };

  const handleFileDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      setFiles(Array.from(e.dataTransfer.files));
    }
  };
  
  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;
    const data = new FormData();
    files.forEach(f => data.append('files', f));
    
    try {
      const res = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: data
      });
      if (res.ok) {
        if (testType === 1 || testType === 3) {
          fetchFolders();
          setCurrentStep(3);
        } else {
          setCurrentStep(4);
        }
      }
    } catch (err) {
      console.error(err);
      alert("Failed to upload files");
    }
  };

  const fetchFolders = async () => {
    try {
      const res = await fetch(`${API_BASE}/folders`);
      const data = await res.json();
      setFolders(data.folders || []);
    } catch (err) {
      console.error(err);
    }
  };

  const submitRuns = async () => {
    try {
      const res = await fetch(`${API_BASE}/select-runs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ runA, runB })
      });
      if (res.ok) {
        setCurrentStep(4);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to submit runs");
    }
  };

  const startProcessing = async () => {
    setIsProcessing(true);
    setError('');
    setImages([]);
    
    try {
      const res = await fetch(`${API_BASE}/generate_plots?testType=${testType}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(plotParams)
      });
      
      const data = await res.json();
      if (data.success) {
        setImages(data.images || []);
      } else {
        setError(data.error || 'Failed to generate plots');
      }
    } catch (err) {
      console.error(err);
      setError('Connection to server failed.');
    } finally {
      setIsProcessing(false);
    }
  };

  const steps = [
    { id: 0, title: 'Test Type' },
    { id: 1, title: 'Data Source & Info' },
    { id: 2, title: 'Upload Files' },
    ...(testType === 1 || testType === 3 ? [{ id: 3, title: 'Select Runs' }] : []),
    { id: 4, title: 'Process' },
  ];

  return (
    <div className="container">
      <header className="app-header">
        <h1 className="app-title">NPD Data Processor</h1>
        <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 500, marginTop: '-0.5rem', marginBottom: '0.5rem' }}>Version 0.2.4 Alpaca</div>
        <div className="app-subtitle">Upload and process NPD test data seamlessly</div>
      </header>

      <div className="wizard-container">
        {/* Sidebar */}
        <div className="wizard-sidebar">
          {steps.map((step) => (
            <div 
              key={step.id} 
              className={`wizard-step-indicator ${currentStep === step.id ? 'active' : ''} ${currentStep > step.id ? 'completed' : ''}`}
            >
              <div className="step-number">
                {currentStep > step.id ? <CheckCircle size={16} /> : step.id}
              </div>
              <div>{step.title}</div>
            </div>
          ))}
        </div>

        {/* Content */}
        <div className="wizard-content card">
          {currentStep === 0 && (
            <div className="step-card">
              <h2>Select Test Type</h2>
              <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Choose the type of test data you are processing.</p>
              
              <div className="test-type-cards">
                <div className={`test-type-card ${testType === 1 ? 'selected' : ''}`} onClick={() => setTestType(1)}>
                  <Activity size={32} color="var(--accent)" style={{ marginBottom: '1rem' }} />
                  <h3>Over Temp</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Test 1</p>
                </div>
                <div className={`test-type-card ${testType === 2 ? 'selected' : ''}`} onClick={() => setTestType(2)}>
                  <Server size={32} color="var(--accent)" style={{ marginBottom: '1rem' }} />
                  <h3>Single Tile Bench NPD</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Test 2</p>
                </div>
                <div className={`test-type-card ${testType === 3 ? 'selected' : ''}`} onClick={() => setTestType(3)}>
                  <Server size={32} color="var(--accent)" style={{ marginBottom: '1rem' }} />
                  <h3>Full PMA Array Bench NPD</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Test 3</p>
                </div>
              </div>

              <div className="btn-group">
                <button onClick={() => setCurrentStep(1)} disabled={!testType}>
                  Continue <ChevronRight size={18} style={{ verticalAlign: 'middle' }} />
                </button>
              </div>
            </div>
          )}

          {currentStep === 1 && (
            <div className="step-card">
              <h2>Data Source & Info</h2>
              <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Provide the base path and metadata for the test files.</p>

              <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                <label>Base Path (for inputs)</label>
                <input type="text" name="basePath" value={formData.basePath} onChange={handleInputChange} placeholder="e.g. C:\Data\NPD" style={{ width: '100%' }} />
              </div>

              <div className="form-group">
                <label>LMO Number (####-##)</label>
                <input type="text" name="lmoNumber" value={formData.lmoNumber} onChange={handleInputChange} />
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
                </>
              )}

              {testType === 2 && (
                <>
                  <div className="form-group">
                    <label>Serial Number (####)</label>
                    <input type="text" name="serialNumber" value={formData.serialNumber} onChange={handleInputChange} />
                  </div>
                  <div className="form-group">
                    <label>PMA Area (L110173C or L110172E)</label>
                    <input type="text" name="pmaArea" value={formData.pmaArea} onChange={handleInputChange} />
                  </div>
                </>
              )}

              {testType === 3 && (
                <>
                  <div className="form-group">
                    <label>Serial Number (####)</label>
                    <input type="text" name="serialNumber" value={formData.serialNumber} onChange={handleInputChange} />
                  </div>
                  <div className="form-group">
                    <label>Run Entry (Run_#_#.###A)</label>
                    <input type="text" name="runEntry" value={formData.runEntry} onChange={handleInputChange} />
                  </div>
                </>
              )}

              <div className="btn-group" style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                <button className="secondary" onClick={() => setCurrentStep(0)}>Back</button>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button onClick={() => {
                    submitFileInfo();
                    if (testType === 2) {
                      setCurrentStep(4);
                    } else {
                      fetchFolders();
                      setCurrentStep(3);
                    }
                  }} className="primary">Access</button>
                  <button onClick={() => {
                    submitFileInfo();
                    setCurrentStep(2);
                  }} className="primary">Upload</button>
                </div>
              </div>
            </div>
          )}

          {currentStep === 2 && (
            <div className="step-card">
              <h2>Upload Data Files</h2>
              <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Select all relevant data files (.csv + .s2p).</p>

              <div 
                className="file-upload-zone"
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleFileDrop}
                onClick={() => document.getElementById('fileInput').click()}
              >
                <Upload className="file-upload-icon" />
                <p>Drag & drop files here, or click to select</p>
                <input 
                  type="file" 
                  id="fileInput" 
                  multiple 
                  style={{ display: 'none' }} 
                  onChange={handleFileChange}
                />
              </div>

              {files.length > 0 && (
                <div style={{ marginTop: '1rem', background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '8px' }}>
                  <h4 style={{ margin: '0 0 0.5rem 0' }}>Selected Files ({files.length})</h4>
                  <ul style={{ margin: 0, paddingLeft: '1.5rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    {files.slice(0, 5).map((f, i) => <li key={i}>{f.name}</li>)}
                    {files.length > 5 && <li>...and {files.length - 5} more</li>}
                  </ul>
                </div>
              )}

              <div className="btn-group">
                <button className="secondary" onClick={() => setCurrentStep(1)}>Back</button>
                <button onClick={uploadFiles} disabled={files.length === 0}>Upload Files</button>
              </div>
            </div>
          )}

          {currentStep === 3 && (testType === 1 || testType === 3) && (
            <div className="step-card">
              <h2>Select Runs</h2>
              <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Select Run A and Run B folders to process.</p>

              <div className="form-group">
                <label>Run A</label>
                <select value={runA} onChange={e => setRunA(e.target.value)}>
                  <option value="">Select a folder...</option>
                  {folders.map(f => <option key={f} value={f}>{f}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label>Run B</label>
                <select value={runB} onChange={e => setRunB(e.target.value)}>
                  <option value="">Select a folder...</option>
                  {folders.map(f => <option key={f} value={f}>{f}</option>)}
                </select>
              </div>

              <div className="btn-group">
                <button className="secondary" onClick={() => setCurrentStep(2)}>Back</button>
                <button onClick={submitRuns}>Continue</button>
              </div>
            </div>
          )}

          {currentStep === 4 && (
            <div className="step-card">
              <h2>Plot Configuration</h2>
              <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Configure parameters for generating plots.</p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '2rem' }}>
                <div className="form-group">
                  <label>Min Frequency (GHz)</label>
                  <input type="number" step="0.1" name="freq_min" value={plotParams.freq_min} onChange={handlePlotParamChange} />
                </div>
                <div className="form-group">
                  <label>Max Frequency (GHz)</label>
                  <input type="number" step="0.1" name="freq_max" value={plotParams.freq_max} onChange={handlePlotParamChange} />
                </div>
                <div className="form-group">
                  <label>reqS11Val</label>
                  <input type="number" step="1" name="reqS11Val" value={plotParams.reqS11Val} onChange={handlePlotParamChange} />
                </div>
                <div className="form-group">
                  <label>reqS21Val</label>
                  <input type="number" step="1" name="reqS21Val" value={plotParams.reqS21Val} onChange={handlePlotParamChange} />
                </div>
                <div className="form-group">
                  <label>Averaging (n_avg)</label>
                  <input type="number" step="2" name="n_avg" value={plotParams.n_avg} onChange={handlePlotParamChange} />
                </div>
                <div className="form-group">
                  <label>S21 Upper Bound Offset</label>
                  <input type="number" step="0.1" name="u_bound_s21" value={plotParams.u_bound_s21} onChange={handlePlotParamChange} />
                </div>
                <div className="form-group">
                  <label>S21 Lower Bound Offset</label>
                  <input type="number" step="0.1" name="l_bound_s21" value={plotParams.l_bound_s21} onChange={handlePlotParamChange} />
                </div>
                <div className="form-group">
                  <label>NPD Upper Bound Offset</label>
                  <input type="number" step="0.1" name="u_bound_npd" value={plotParams.u_bound_npd} onChange={handlePlotParamChange} />
                </div>
                <div className="form-group">
                  <label>NPD Lower Bound Offset</label>
                  <input type="number" step="0.1" name="l_bound_npd" value={plotParams.l_bound_npd} onChange={handlePlotParamChange} />
                </div>
              </div>

              {error && <div style={{ color: 'var(--error)', marginBottom: '1rem', padding: '1rem', background: 'rgba(239,68,68,0.1)', borderRadius: '8px' }}>{error}</div>}

              <button onClick={startProcessing} disabled={isProcessing} style={{ width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem', marginBottom: '2rem' }}>
                {isProcessing ? <Activity className="animate-spin" size={18} /> : <Play size={18} />}
                {isProcessing ? 'Generating Plots...' : 'Generate Plots'}
              </button>

              {images.length > 0 && (
                <div style={{ marginTop: '2rem' }}>
                  <h3 style={{ marginBottom: '1rem' }}>Generated Plots ({images.length})</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
                    {images.map((img, idx) => (
                      <div key={idx} style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border)' }}>
                        <img src={img.data} alt={img.filename} style={{ width: '100%', height: 'auto', borderRadius: '4px' }} />
                        <div style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: 'var(--text-muted)', textAlign: 'center' }}>
                          {img.filename}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="btn-group">
                <button className="secondary" onClick={() => setCurrentStep(0)}>Start Over</button>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

export default App;
