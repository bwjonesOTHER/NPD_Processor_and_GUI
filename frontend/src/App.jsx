import React, { useState, useRef, useEffect } from 'react';
import { Upload, CheckCircle, Terminal, Play, Server, ChevronRight, Activity, Download, UploadCloud, XCircle, Save, Folder } from 'lucide-react';
import JSZip from 'jszip';
import './App.css';

const API_BASE = window.location.port === '5173' ? `http://${window.location.hostname}:5001/api` : '/api';

const ALLOWED_EXTENSIONS = ['.csv', '.xlsx', '.xls', '.txt', '.tdms', '.json', '.log', '.s1p', '.s2p'];
const filterValidFiles = (files) => {
  return Array.from(files).filter(f => {
    const name = f.name.toLowerCase();
    return ALLOWED_EXTENSIONS.some(ext => name.endsWith(ext));
  });
};

function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [testType, setTestType] = useState(null);
  const [isConnected, setIsConnected] = useState(true); // Always true now since we removed SharePoint
  const [isProcessing, setIsProcessing] = useState(false);
  const [isUploadingSource, setIsUploadingSource] = useState(false);
  const [images, setImages] = useState([]);
  const [error, setError] = useState('');
  
  const [uploadMode, setUploadMode] = useState(null); // 'access' or 'upload'
  
  const [lmoOptions, setLmoOptions] = useState([]);
  const [showLmoModal, setShowLmoModal] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    basePath: '',
    lmoNumber: '',
    runNumber: '',
    capNumber: '',
    serialNumber: '',
    pmaArea: '',
    runEntry: '',
    exactLmoFolder: '',
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
  const [runs, setRuns] = useState(['', '', '']);
  const [runNames, setRunNames] = useState([]);
  const [runFiles, setRunFiles] = useState([[], [], []]);
  const [outputFolder, setOutputFolder] = useState('');
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
    const link = document.createElement("a");
    link.href = url;
    link.download = "NPD_Plots.zip";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleSavePlots = async () => {
    if (!outputFolder) {
      alert("Please select a Plot Output Destination folder on the previous page.");
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/save_plots`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ outputFolder, plots: images })
      });
      const data = await res.json();
      if (data.success) {
        alert(`Successfully saved ${data.saved.length} plots to ${outputFolder}`);
      } else {
        alert(`Error saving plots: ${data.error}`);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to save plots: " + err.message);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };



  const handlePlotParamChange = (e) => {
    const { name, value } = e.target;
    setPlotParams(prev => ({ ...prev, [name]: value }));
  };

  const handleSelectOutputFolder = async () => {
    try {
      const res = await fetch(`${API_BASE}/choose_directory`);
      const data = await res.json();
      if (data.success && data.path) {
        setOutputFolder(data.path);
      }
    } catch (err) {
      console.error(err);
      alert("Error selecting output directory: " + err.message);
    }
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
          uploadMode,
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
  };

  const handleFileDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      setFiles(filterValidFiles(e.dataTransfer.files));
    }
  };
  
  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles(filterValidFiles(e.target.files));
    }
  };

  const handleDataSourceUpload = async (e) => {
    const selectedFiles = filterValidFiles(e.target.files);
    if (selectedFiles.length === 0) return;
    
    setIsUploadingSource(true);
    
    try {
      const CHUNK_SIZE = 50;
      let finalUploadPath = '';
      
      for (let i = 0; i < selectedFiles.length; i += CHUNK_SIZE) {
        const chunk = selectedFiles.slice(i, i + CHUNK_SIZE);
        const data = new FormData();
        chunk.forEach(f => {
          data.append('files', f);
          data.append('paths', f.webkitRelativePath || f.name);
        });
        data.append('run_index', '0');
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

      if (finalUploadPath) {
        setFormData(prev => ({...prev, basePath: finalUploadPath}));
      } else {
        alert("Upload failed: No upload path returned.");
      }
    } catch (err) {
      console.error(err);
      alert("Upload error: " + err.message);
    } finally {
      setIsUploadingSource(false);
      e.target.value = ''; // Reset input
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
        setFiles([]);
        alert("Files uploaded successfully!");
      }
    } catch (err) {
      console.error(err);
      alert("Failed to upload files");
    }
  };

  // uploadFiles removed fetchFolders call and submitRuns removed fetchFolders call

  const submitRuns = async () => {
    // Safety check: ensure all required inputs are populated
    const numSlots = testType === 1 ? (runs.filter(r => r !== '').length > 0 ? runs.length : 1) : 3;
    
    // Validate that we have enough runs
    const validRuns = runs.filter(r => r !== '');
    if (testType === 3 && validRuns.length < 3) {
      alert("Please select and upload all 3 folders (Run A, Run B, and Calibration) before processing.");
      return { success: false };
    }
    
    if (testType === 1 && validRuns.length === 0) {
      alert("Please select and upload at least one run before processing.");
      return { success: false };
    }

    try {
      const payload = testType === 1 
        ? { runs: validRuns } 
        : { runA: validRuns[0] || '', runB: validRuns[1] || '', calPath: validRuns[2] || '' };

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
        body: JSON.stringify({ ...plotParams, outputFolder: "", dataSource: formData.basePath })
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

  const handleTestTypeNext = (mode) => {
    setUploadMode(mode);
    if (testType === 2) {
      setCurrentStep(1); // Test 2 now ALWAYS uses Step 1
      return;
    }
    
    if (mode === 'access') {
      setCurrentStep(3); // Test 1 and 3 skip to Select Runs
    } else {
      setCurrentStep(1); // Upload mode goes to Step 1
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
        <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 500, marginTop: '-0.5rem', marginBottom: '0.5rem' }}>Version 0.6.0.2 Dingo</div>
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

              <div className="btn-group" style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', width: '100%' }}>
                <button onClick={() => handleTestTypeNext('access')} disabled={!testType} className="primary">
                  Access
                </button>
                <button onClick={() => handleTestTypeNext('upload')} disabled={!testType} className="primary">
                  Upload <ChevronRight size={18} style={{ verticalAlign: 'middle' }} />
                </button>
              </div>
            </div>
          )}

          {currentStep === 1 && (
            <div className="step-card">
              <h2>Data Source & Info</h2>
              <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Provide the base path and metadata for the test files.</p>

              <div className="form-group">
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
              </div>

              <div className="form-group">
                <label>{testType === 2 ? 'LMO Number (e.g. 1234)' : 'LMO Number (####-##)'}</label>
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

              <div className="btn-group">
                <button className="secondary" onClick={() => setCurrentStep(0)}>Back</button>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  {testType === 2 ? (
                    <button onClick={async () => {
                      if (!formData.basePath) {
                        alert(`Please select the ${uploadMode === 'upload' ? 'Base Upload Directory' : 'BenchNPD Root Directory'} before continuing.`);
                        return;
                      }
                      
                      const result = await submitFileInfo();
                      
                      if (result && result.requireLmoSelection) return;
                      
                      if (result && result.success) {
                        if (uploadMode === 'access') {
                          setCurrentStep(4);
                        } else {
                          // For upload mode, directory is now created on the backend, proceed to upload files
                          setCurrentStep(2);
                        }
                      }
                    }} className="primary" style={{ background: 'var(--success)' }}>
                      {uploadMode === 'upload' ? 'Proceed to Upload' : 'Proceed to Configuration'} <ChevronRight size={18} style={{ verticalAlign: 'middle' }} />
                    </button>
                  ) : (
                    <>
                      <button onClick={async () => {
                        if (!formData.basePath) {
                          alert("Please select a Base Upload Path before continuing.");
                          return;
                        }
                        const result = await submitFileInfo();
                        if (result && result.success) setCurrentStep(2);
                      }} className="primary">Upload Files <Upload size={18} style={{ verticalAlign: 'middle' }} /></button>
                      <button onClick={async () => {
                        if (!formData.basePath) {
                          alert("Please select a Base Upload Path before continuing.");
                          return;
                        }
                        const result = await submitFileInfo();
                        if (result && result.success) setCurrentStep(3);
                      }} className="primary" style={{ background: 'var(--success)' }}>Process <ChevronRight size={18} style={{ verticalAlign: 'middle' }} /></button>
                    </>
                  )}
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
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <button onClick={uploadFiles} disabled={files.length === 0 || (testType === 2 && !formData.basePath)} className="primary">Upload Files</button>
                  {testType === 2 && (
                    <button onClick={() => setCurrentStep(4)} className="primary" style={{ background: 'var(--success)' }}>Proceed to Configuration <ChevronRight size={18} style={{ verticalAlign: 'middle' }} /></button>
                  )}
                </div>
              </div>
            </div>
          )}

          {currentStep === 3 && (testType === 1 || testType === 3) && (
            <div className="step-card">
              <h2>Select Runs</h2>
              <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Select runs to process.</p>

              {(testType === 1 || testType === 3) && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                  <div 
                    style={{
                      border: '2px dashed var(--border-color)',
                      borderRadius: '12px',
                      padding: '3rem 2rem',
                      textAlign: 'center',
                      cursor: uploadingRun ? 'not-allowed' : 'pointer',
                      background: 'var(--panel-bg)',
                      transition: 'background 0.2s',
                      opacity: uploadingRun ? 0.7 : 1
                    }}
                    onClick={() => {
                      if (testType === 3 && runs.filter(r => r !== '').length >= 3) {
                        alert("You have already uploaded all 3 required folders (Run A, Run B, Calibration).");
                        return;
                      }
                      !uploadingRun && test1RunsInputRef.current?.click();
                    }}
                  >
                    {uploadingRun ? (
                      <Activity size={40} className="spinner" color="var(--accent)" style={{marginBottom: '1rem'}} />
                    ) : (
                      <UploadCloud size={40} color="var(--accent)" style={{marginBottom: '1rem'}} />
                    )}
                    <div>
                      <strong style={{ fontSize: '1.1rem', color: 'var(--text-main)' }}>
                        {uploadingRun ? "Uploading..." : testType === 3 ? (
                          runs.filter(r => r !== '').length === 0 ? "Click to select Run A folder" :
                          runs.filter(r => r !== '').length === 1 ? "Click to select Run B folder" :
                          "Click to select Calibration (Cable Loss) folder"
                        ) : "Click to select and upload a run folder"}
                      </strong>
                      {!uploadingRun && <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                        {testType === 3 ? "(Upload folders in order: Run A, then Run B, then Calibration)" : "(Click multiple times to add more runs!)"}
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
                            if (testType === 3 && runIndex === 2) {
                              data.append('folder_name', 'Cable Loss');
                            } else if (extractedFolderName) {
                              data.append('folder_name', extractedFolderName);
                            }
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
                    <div style={{ background: 'var(--panel-bg)', padding: '1.5rem', borderRadius: '12px' }}>
                      <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>Added Folders ({runs.filter(r => r !== '').length})</h3>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {runs.filter(r => r !== '').map((runPath, idx) => (
                          <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-main)', padding: '0.75rem 1rem', borderRadius: '8px' }}>
                            <span style={{ fontSize: '0.9rem', color: 'var(--text-main)', wordBreak: 'break-all' }}>
                              <strong>
                                {testType === 3 
                                  ? (idx === 0 ? 'Run A: ' : idx === 1 ? 'Run B: ' : 'Calibration: ') 
                                  : (runNames[idx] || `Run ${idx + 1}: `)}
                              </strong> 
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
                              <XCircle size={20} />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
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

              <div style={{ marginTop: '1.5rem', marginBottom: '1.5rem', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', border: '1px solid var(--border)' }}>
                <h4 style={{ marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>Plot Output Destination</h4>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <button onClick={handleSelectOutputFolder} className="btn-primary" style={{ padding: '0.5rem 1rem', width: 'auto', fontSize: '0.9rem' }}>
                    Select Output Folder
                  </button>
                  <span style={{ fontSize: '0.875rem', color: outputFolder ? 'var(--text-main)' : 'var(--text-muted)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {outputFolder || 'Plots will NOT be saved automatically. Click Save Plots after generation.'}
                  </span>
                </div>
              </div>

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
                  <input type="number" step="1" min="1" name="n_avg" value={plotParams.n_avg} onChange={handlePlotParamChange} />
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
                    <div style={{ display: 'flex', gap: '1rem' }}>
                      <button onClick={handleSavePlots} className="btn-primary" style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', width: 'auto', fontSize: '0.9rem', background: 'var(--success)' }}>
                        <Save size={16} />
                        Save Plots to Destination
                      </button>
                      <button onClick={handleExportPlots} className="btn-primary" style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', width: 'auto', fontSize: '0.9rem' }}>
                        <Download size={16} />
                        Export All Plots (.zip)
                      </button>
                    </div>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
                    {images.map((img, idx) => (
                      <div key={idx} style={{ background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border)' }}>
                        <img src={img.data} alt={img.filename} className={img.status === 'passed' ? 'plot-pass' : img.status === 'failed' ? 'plot-fail' : ''} style={{ width: '100%', height: 'auto', borderRadius: '4px' }} />
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

      {/* LMO Selection Modal */}
      {showLmoModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 9999,
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <div style={{
            background: 'var(--panel-bg)', padding: '2rem', borderRadius: '12px',
            width: '400px', maxWidth: '90%', boxShadow: '0 10px 30px rgba(0,0,0,0.3)'
          }}>
            <h3 style={{ marginTop: 0, color: 'var(--text-main)' }}>Multiple LMO Folders Found</h3>
            <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
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
                  <Folder size={16} style={{ marginRight: '0.5rem', verticalAlign: 'middle', color: 'var(--accent)' }} />
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


export default App;
