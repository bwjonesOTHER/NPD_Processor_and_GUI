import React, { useState, useRef, useEffect } from 'react';
import { Upload, CheckCircle, Terminal, Play, Server, ChevronRight, Activity, Download, UploadCloud, XCircle } from 'lucide-react';
import JSZip from 'jszip';
import './App.css';

const API_BASE = window.location.port === '5173' ? 'http://127.0.0.1:5001/api' : '/api';

function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [testType, setTestType] = useState(null);
  const [isConnected, setIsConnected] = useState(true); // Always true now since we removed SharePoint
  const [isProcessing, setIsProcessing] = useState(false);
  const [images, setImages] = useState([]);
  const [error, setError] = useState('');
  
  // Form state
  const [formData, setFormData] = useState({
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
  const [runs, setRuns] = useState(['', '']);
  const [runFiles, setRunFiles] = useState([[], []]);
  const [numRuns, setNumRuns] = useState(2);
  const [numRunsInput, setNumRunsInput] = useState('2');
  const [uploadingRun, setUploadingRun] = useState(false);
  const test1RunsInputRef = useRef(null);





  const handleExportPlots = async () => {
    if (images.length === 0) return;
    const zip = new JSZip();
    
    images.forEach((img) => {
      const base64Data = img.data.replace(/^data:image\/(png|jpg|jpeg);base64,/, "");
      zip.file(img.filename, base64Data, { base64: true });
    });
    
    const content = await zip.generateAsync({ type: "blob" });
    const url = URL.createObjectURL(content);
    const a = document.createElement("a");
    a.href = url;
    a.download = "NPD_Plots.zip";
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const uploadRun = async (idx) => {
    let files = runFiles[idx];
    if (!files || files.length === 0) return;
    
    const allowedExtensions = ['.csv', '.xlsx', '.xls', '.txt', '.tdms', '.json', '.log', '.s1p', '.s2p'];
    files = files.filter(f => {
      const name = f.name.toLowerCase();
      return allowedExtensions.some(ext => name.endsWith(ext));
    });
    
    if (files.length === 0) {
      alert("No valid data files found for this run.");
      return;
    }
    
    try {
      const CHUNK_SIZE = 50;
      let finalUploadPath = '';
      
      for (let i = 0; i < files.length; i += CHUNK_SIZE) {
        const chunk = files.slice(i, i + CHUNK_SIZE);
        const data = new FormData();
        chunk.forEach(f => {
          data.append('files', f);
          data.append('paths', f.webkitRelativePath || f.name);
        });
        data.append('run_index', idx);
        data.append('chunk_index', i === 0 ? '0' : '1');
        
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
      
      setRuns(prev => {
        const newRuns = [...prev];
        newRuns[idx] = finalUploadPath;
        return newRuns;
      });
    } catch (err) {
      console.error(err);
      alert("Upload error: " + err.message);
    }
  };

  const handlePlotParamChange = (e) => {
    const { name, value } = e.target;
    setPlotParams(prev => ({ ...prev, [name]: value }));
  };

  const handleBrowseRun = async (index) => {
    try {
      const res = await fetch(`${API_BASE}/choose_directory`);
      const data = await res.json();
      if (data.success && data.path) {
        setRuns(prev => {
          const newRuns = [...prev];
          newRuns[index] = data.path;
          return newRuns;
        });
      } else if (!data.success && data.error && data.error !== "No directory selected") {
        alert("Error opening directory picker: " + data.error);
      }
    } catch (err) {
      console.error("Failed to choose directory:", err);
      alert("Network error opening directory picker: " + err.message);
    }
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

  // uploadFiles removed fetchFolders call and submitRuns removed fetchFolders call

  const submitRuns = async () => {
    try {
      const payload = testType === 1 
        ? { runs } 
        : { runA: runs[0] || '', runB: runs[1] || '' };

      const res = await fetch(`${API_BASE}/select-runs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
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
        <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 500, marginTop: '-0.5rem', marginBottom: '0.5rem' }}>Version 0.4.7.9 Cardinal</div>
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
                  <button onClick={async () => {
                    await submitFileInfo();
                    if (testType === 2) {
                      setCurrentStep(4);
                    } else {
                      setCurrentStep(3);
                    }
                  }} className="primary">Access</button>
                  <button onClick={async () => {
                    await submitFileInfo();
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
              <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Select runs to process.</p>

              {testType === 1 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                  <div 
                    style={{
                      border: '2px dashed var(--border-color)',
                      borderRadius: '12px',
                      padding: '3rem 2rem',
                      textAlign: 'center',
                      cursor: uploadingRun ? 'not-allowed' : 'pointer',
                      background: 'var(--surface)',
                      transition: 'background 0.2s',
                      opacity: uploadingRun ? 0.7 : 1
                    }}
                    onClick={() => !uploadingRun && test1RunsInputRef.current?.click()}
                  >
                    {uploadingRun ? (
                      <Activity size={40} className="spinner" color="var(--accent)" style={{marginBottom: '1rem'}} />
                    ) : (
                      <UploadCloud size={40} color="var(--accent)" style={{marginBottom: '1rem'}} />
                    )}
                    <div>
                      <strong style={{ fontSize: '1.1rem', color: 'var(--text-main)' }}>
                        {uploadingRun ? "Uploading..." : "Click to select and upload a run folder"}
                      </strong>
                      {!uploadingRun && <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>(Click multiple times to add more runs!)</p>}
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
                        const allowedExtensions = ['.csv', '.xlsx', '.xls', '.txt', '.tdms', '.json', '.log', '.s1p', '.s2p'];
                        const filesArray = Array.from(e.target.files).filter(f => {
                          const name = f.name.toLowerCase();
                          return allowedExtensions.some(ext => name.endsWith(ext));
                        });
                        
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
                            data.append('chunk_index', i === 0 ? '0' : '1');
                            
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
                          
                          setRuns([...validRuns, finalUploadPath]);
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
                    <div style={{ background: 'var(--surface)', padding: '1.5rem', borderRadius: '12px' }}>
                      <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>Added Runs ({runs.filter(r => r !== '').length})</h3>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {runs.filter(r => r !== '').map((runPath, idx) => (
                          <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-main)', padding: '0.75rem 1rem', borderRadius: '8px' }}>
                            <span style={{ fontSize: '0.9rem', color: 'var(--text-main)', wordBreak: 'break-all' }}><strong>Run {idx + 1}:</strong> {runPath.split(/[\\\\/]/).pop() || runPath}</span>
                            <button 
                              className="icon-btn" 
                              onClick={() => {
                                setRuns(prev => prev.filter(r => r !== '').filter((_, i) => i !== idx));
                              }}
                              style={{ color: '#ff6b6b', background: 'none', border: 'none', cursor: 'pointer', padding: '0.25rem' }}
                              title="Remove Run"
                            >
                              <XCircle size={20} />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {testType === 3 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {[0, 1].map((idx) => (
                    <div key={idx} className="form-group">
                      <label>Run {idx === 0 ? 'A' : 'B'}</label>
                      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        <input 
                          type="file" 
                          webkitdirectory="true"
                          directory="true"
                          multiple
                          onChange={e => {
                            const newFiles = [...runFiles];
                            newFiles[idx] = Array.from(e.target.files);
                            setRunFiles(newFiles);
                            const newRuns = [...runs];
                            newRuns[idx] = '';
                            setRuns(newRuns);
                          }}
                          style={{ flex: 1 }}
                        />
                        <button 
                          type="button" 
                          onClick={() => uploadRun(idx)} 
                          className="secondary" 
                          style={{ whiteSpace: 'nowrap' }}
                          disabled={!runFiles[idx] || runFiles[idx].length === 0}
                        >
                          Upload
                        </button>
                      </div>
                      {runs[idx] && <p style={{ color: 'var(--success)', fontSize: '0.85rem', marginTop: '0.5rem' }}>Uploaded to server successfully.</p>}
                    </div>
                  ))}
                </div>
              )}

              <div className="btn-group" style={{ marginTop: '2rem' }}>
                <button className="secondary" onClick={() => setCurrentStep(2)}>Back</button>
                <button onClick={submitRuns}>Continue</button>
              </div>
            </div>
          )}

          {currentStep === 4 && (
            <div className="step-card glass" style={{ border: 'none', padding: '2rem' }}>
              <h2>Plot Configuration</h2>
              <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Configure parameters for generating plots.</p>

              <div className="form-grid">
                <div className="input-group">
                  <label>Min Frequency (GHz)</label>
                  <input type="number" step="0.1" name="freq_min" value={plotParams.freq_min} onChange={handlePlotParamChange} />
                </div>
                <div className="input-group">
                  <label>Max Frequency (GHz)</label>
                  <input type="number" step="0.1" name="freq_max" value={plotParams.freq_max} onChange={handlePlotParamChange} />
                </div>
                <div className="input-group">
                  <label>reqS21Val</label>
                  <input type="number" step="1" name="reqS21Val" value={plotParams.reqS21Val} onChange={handlePlotParamChange} />
                </div>
                <div className="input-group">
                  <label>Averaging (n_avg)</label>
                  <input type="number" step="2" name="n_avg" value={plotParams.n_avg} onChange={handlePlotParamChange} />
                </div>
                <div className="input-group">
                  <label>S21 Upper Bound Offset</label>
                  <input type="number" step="0.1" name="u_bound_s21" value={plotParams.u_bound_s21} onChange={handlePlotParamChange} />
                </div>
                <div className="input-group">
                  <label>S21 Lower Bound Offset</label>
                  <input type="number" step="0.1" name="l_bound_s21" value={plotParams.l_bound_s21} onChange={handlePlotParamChange} />
                </div>
                <div className="input-group">
                  <label>NPD Upper Bound Offset</label>
                  <input type="number" step="0.1" name="u_bound_npd" value={plotParams.u_bound_npd} onChange={handlePlotParamChange} />
                </div>
                <div className="input-group">
                  <label>NPD Lower Bound Offset</label>
                  <input type="number" step="0.1" name="l_bound_npd" value={plotParams.l_bound_npd} onChange={handlePlotParamChange} />

                </div>
              </div>

              {error && <div style={{ color: 'var(--error)', marginBottom: '1rem', padding: '1rem', background: 'rgba(239,68,68,0.1)', borderRadius: '8px' }}>{error}</div>}

              <button className="btn-primary" onClick={startProcessing} disabled={isProcessing} style={{ marginTop: '2rem' }}>
                {isProcessing ? <Activity className="animate-spin" size={18} /> : <Play size={18} />}
                {isProcessing ? 'Generating Plots...' : 'Generate Plots'}
              </button>

              {images.length > 0 && (
                <div style={{ marginTop: '2rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h3 style={{ margin: 0 }}>Generated Plots ({images.length})</h3>
                    <button onClick={handleExportPlots} className="btn-primary" style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', width: 'auto', fontSize: '0.9rem' }}>
                      <Download size={16} />
                      Export All Plots (.zip)
                    </button>
                  </div>
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

              <div className="btn-group" style={{ display: 'flex', gap: '1rem' }}>
                <button 
                  className="secondary" 
                  onClick={() => setCurrentStep(testType === 2 ? 2 : 3)}
                >
                  Back
                </button>
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
