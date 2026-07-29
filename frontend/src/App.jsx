import React, { useState, useRef, useEffect } from 'react';
import { Upload, CheckCircle, Terminal, Play, Server, ChevronRight, ChevronLeft, Activity, Download, UploadCloud, XCircle, Save, Folder, X, Maximize2, Settings } from 'lucide-react';
import JSZip from 'jszip';
import './App.css';
import InteractivePlot from './InteractivePlot';

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
  const [test2Files, setTest2Files] = useState({
    bench: null,
    temp: null,
    cal: null,
    tempCal: null,
  });
  const [test3Files, setTest3Files] = useState({
    runA: null,
    runB: null,
    cal: null
  });
  const [generalFiles, setGeneralFiles] = useState(null);
  const [sessionData, setSessionData] = useState(null);
  const [isConnected, setIsConnected] = useState(true); // Always true now since we removed SharePoint
  const [isProcessing, setIsProcessing] = useState(false);
  const [isUploadingSource, setIsUploadingSource] = useState(false);
  const [isUploadingRefFile, setIsUploadingRefFile] = useState(false);
  const [images, setImages] = useState([]);
  const plotRefs = useRef([]);
  const [error, setError] = useState('');
  const [warnings, setWarnings] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(null);
  
  const [uploadMode, setUploadMode] = useState(null); // 'access' or 'upload'
  
  const [lmoOptions, setLmoOptions] = useState([]);
  const [showLmoModal, setShowLmoModal] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    basePath: '',
    calPath: '',
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
    n_avg: 20,
    u_bound_s21: 2,
    l_bound_s21: 2,
    u_bound_npd: 2,
    l_bound_npd: 2,
    y_upper_s21: 40,
    y_lower_s21: -40,
    y_upper_npd: -110,
    y_lower_npd: -170,
    average_data_path: "",
    apply_npd_cal: false,
    plot_s12: false,
  });

  useEffect(() => {
    if (testType === 1) {
      setPlotParams(prev => ({
        ...prev,
        freq_min: 2.7,
        freq_max: 4.1,
        u_bound_s21: 2,
        l_bound_s21: 2,
        u_bound_npd: 2,
        l_bound_npd: 2,
        average_data_path: "",
      }));
    } else {
      setPlotParams(prev => ({
        ...prev,
        freq_min: 2.7,
        freq_max: 4.1,
        u_bound_s21: 2,
        l_bound_s21: 2,
        u_bound_npd: 2,
        l_bound_npd: 2,
        average_data_path: "",
      }));
    }
  }, [testType]);

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

  useEffect(() => {
    if (selectedIndex === null) return;
    const onKeyDown = (e) => {
      if (e.key === 'Escape') setSelectedIndex(null);
      else if (e.key === 'ArrowRight') setSelectedIndex(i => (i + 1) % images.length);
      else if (e.key === 'ArrowLeft') setSelectedIndex(i => (i - 1 + images.length) % images.length);
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [selectedIndex, images.length]);






  const [isUploadingAdditionalCal, setIsUploadingAdditionalCal] = useState(false);
  const [additionalCalCount, setAdditionalCalCount] = useState(0);

  const handleUploadAdditionalCalFiles = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    setIsUploadingAdditionalCal(true);

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    try {
      const res = await fetch(`${API_BASE}/upload_additional_cal`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        setAdditionalCalCount(data.count || files.length);
        alert(`Successfully uploaded ${data.count || files.length} additional cal file(s).`);
      } else {
        alert("Failed to upload additional cal files: " + (data.error || 'Unknown error'));
      }
    } catch (err) {
      alert("Error uploading additional cal files: " + err.message);
    } finally {
      setIsUploadingAdditionalCal(false);
      e.target.value = null; // reset input
    }
  };

  const handleDeleteAdditionalCalFiles = async () => {
    try {
      const res = await fetch(`${API_BASE}/delete_additional_cal`, { method: 'POST' });
      if (res.ok) {
        setAdditionalCalCount(0);
      } else {
        const data = await res.json();
        alert("Failed to delete additional cal files: " + (data.error || 'Unknown error'));
      }
    } catch (err) {
      alert("Error deleting additional cal files: " + err.message);
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
      } else if (!data.success && data.error && data.error !== "No directory selected") {
        alert("Error selecting output directory: " + data.error);
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
  
  const handleReferenceFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsUploadingRefFile(true);
    try {
      const data = new FormData();
      data.append('file', file);
      const res = await fetch(`${API_BASE}/upload_reference_file`, { method: 'POST', body: data });
      const json = await res.json();
      if (json.success && json.path) {
        setPlotParams(prev => ({ ...prev, average_data_path: json.path }));
      } else {
        alert("Upload error: " + (json.error || 'Unknown error'));
      }
    } catch (err) {
      console.error(err);
      alert("Upload error: " + err.message);
    } finally {
      setIsUploadingRefFile(false);
      e.target.value = ''; // Reset input
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles(filterValidFiles(e.target.files));
    }
  };

  const handleDataUpload = async () => {
    setIsUploadingSource(true);
    try {
      const data = new FormData();
      data.append('test_type', testType);
      data.append('uploadMode', uploadMode);
      
      if (testType === 2) {
        if (!test2Files.bench || test2Files.bench.length === 0) {
          alert('Bench Data Folder is required for Test 2');
          setIsUploadingSource(false);
          return;
        }
        Array.from(test2Files.bench).forEach(f => data.append('bench_files', f, f.webkitRelativePath || f.name));
        if (test2Files.temp) Array.from(test2Files.temp).forEach(f => data.append('temp_files', f, f.webkitRelativePath || f.name));
        if (test2Files.cal) Array.from(test2Files.cal).forEach(f => data.append('cal_files', f, f.webkitRelativePath || f.name));
        if (test2Files.tempCal) Array.from(test2Files.tempCal).forEach(f => data.append('temp_cal_files', f, f.webkitRelativePath || f.name));
      } else if (testType === 3) {
        if (!test3Files.runA || !test3Files.runB || !test3Files.cal) {
          alert('Run 1, Run 2, and Calibration folders are required for Test 3');
          setIsUploadingSource(false);
          return;
        }
        Array.from(test3Files.runA).forEach(f => data.append('runA_files', f, f.webkitRelativePath || f.name));
        Array.from(test3Files.runB).forEach(f => data.append('runB_files', f, f.webkitRelativePath || f.name));
        Array.from(test3Files.cal).forEach(f => data.append('cal_files', f, f.webkitRelativePath || f.name));
      } else if (testType === 4) {
        if (!generalFiles || generalFiles.length === 0) {
          alert('Test Data Folder is required for Test 4');
          setIsUploadingSource(false);
          return;
        }
        Array.from(generalFiles).forEach(f => data.append('general_files', f, f.webkitRelativePath || f.name));
      } else if (testType === 1) {
        if (runs.filter(r => r !== '').length === 0) {
          alert('Please upload at least one run folder for Test 1');
          setIsUploadingSource(false);
          return;
        }
        // Test 1 files are already uploaded in chunks via the multi-run UI.
        // We just need to submit the file info.
      }

      if (testType === 2 || testType === 3 || testType === 4) {
        const res = await fetch(`${API_BASE}/upload_test_data`, {
          method: 'POST',
          body: data
        });
        
        const json = await res.json();
        if (!json.success) {
          alert(json.error || 'Failed to upload test data');
          setIsUploadingSource(false);
          return;
        }

        if (testType === 3 && (!json.paths || !json.paths.runs)) {
          alert(`CRITICAL ERROR: The server accepted the files but did not return the expected 'runs' paths.\nServer saw test_type: ${json.debug_test_type}\nServer form keys: ${JSON.stringify(json.debug_form_keys)}\nServer files keys: ${JSON.stringify(json.debug_files_keys)}`);
          setIsUploadingSource(false);
          return;
        }
        
        // Ensure sessionData includes the generated paths
        setSessionData(json);
      } else if (testType === 1) {
        // For Test 1, mimic the session data format so runs are preserved
        setSessionData({
          paths: { runs: runs.filter(r => r !== '') }
        });
      }
      
      const submitRes = await submitFileInfo();
      if (submitRes.success) {
        setCurrentStep(4);
      }
    } catch (err) {
      console.error(err);
      alert("Error uploading files: " + err.message);
    } finally {
      setIsUploadingSource(false);
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

  const startProcessing = async (overrideParams = null) => {
    setIsProcessing(true);
    setError('');
    setWarnings([]);
    setImages([]);

    try {
      // Prevent passing the React SyntheticEvent as overrideParams
      const isEvent = overrideParams && overrideParams.nativeEvent;
      const activeParams = (overrideParams && !isEvent) ? overrideParams : plotParams;
      
      const res = await fetch(`${API_BASE}/generate_plots?testType=${testType}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          ...activeParams, 
          outputFolder: "", 
          dataSource: sessionData?.paths?.general || formData.basePath, 
          calFolder: sessionData?.paths?.cal || formData.calPath,
          benchPath: sessionData?.paths?.bench,
          tempPath: sessionData?.paths?.temp,
          tempCalPath: sessionData?.paths?.tempCal,
          runs: sessionData?.paths?.runs || [],
          testType: testType,
          serial_number: formData.serialNumber,
          pmaArea: formData.pmaArea
        })
      });

      const data = await res.json();
      if (data.success) {
        setImages(data.plots_data || []);
        setWarnings(data.warnings || []);
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
    setCurrentStep(1);
  };

  const steps = [
    { id: 0, title: 'Test Type' },
    { id: 1, title: 'Data Source & Info' },
    { id: 4, title: 'Process' },
  ];

  return (
    <div className="container" style={{ maxWidth: 'min(1800px, 96vw)' }}>
      <header className="app-header">
        <h1 className="app-title">NPD Data Processor</h1>
        <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 500, marginTop: '-0.5rem', marginBottom: '0.5rem' }}>Version 0.8.0.0 Elk</div>
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
                <div className={`test-type-card ${testType === 4 ? 'selected' : ''}`} onClick={() => setTestType(4)}>
                  <Activity size={32} color="var(--accent)" style={{ marginBottom: '1rem' }} />
                  <h3>Over Temp Array</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Test 4</p>
                </div>
              </div>

              <div className="btn-group" style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', width: '100%' }}>
                <button onClick={() => setCurrentStep(1)} disabled={!testType} className="primary">
                  Next <ChevronRight size={18} style={{ verticalAlign: 'middle' }} />
                </button>
              </div>
            </div>
          )}

          
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
                                {runPath.split(/[\\/]/).pop() || runPath}
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
                  <label>Averaging (n_avg)</label>
                  <input type="number" step="1" min="1" name="n_avg" value={plotParams.n_avg} onChange={handlePlotParamChange} />
                </div>
                <div className="input-group">
                  <label>{testType === 4 ? 'Ambient NPD Reference Average File' : 'Average Data File'}</label>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <button
                      type="button"
                      className="secondary"
                      disabled={isUploadingRefFile}
                      onClick={() => document.getElementById('referenceFileInput').click()}
                      style={{ padding: '0.5rem 1rem', whiteSpace: 'nowrap' }}
                    >
                      {isUploadingRefFile ? 'Uploading...' : 'Upload File'}
                    </button>
                    <span style={{ fontSize: '0.8rem', color: plotParams.average_data_path ? 'var(--text-main)' : 'var(--text-muted)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {plotParams.average_data_path
                        ? plotParams.average_data_path.split(/[\\/]/).pop()
                        : (testType === 4 ? 'Optional — enables pass/fail on Ambient NPD' : 'No file selected')}
                    </span>
                  </div>
                  <input
                    type="file"
                    id="referenceFileInput"
                    accept=".xlsx,.xls,.csv"
                    style={{ display: 'none' }}
                    onChange={handleReferenceFileUpload}
                  />
                </div>
                {testType !== 4 && (
                  <>
                    <div className="input-group">
                      <label>S21 Upper Bound Offset</label>
                      <input type="number" step="0.1" name="u_bound_s21" value={plotParams.u_bound_s21} onChange={handlePlotParamChange} />
                    </div>
                    <div className="input-group">
                      <label>S21 Lower Bound Offset</label>
                      <input type="number" step="0.1" name="l_bound_s21" value={plotParams.l_bound_s21} onChange={handlePlotParamChange} />
                    </div>
                  </>
                )}
                <div className="input-group">
                  <label>NPD Upper Bound Offset</label>
                  <input type="number" step="0.1" name="u_bound_npd" value={plotParams.u_bound_npd} onChange={handlePlotParamChange} />
                </div>
                <div className="input-group">
                  <label>NPD Lower Bound Offset</label>
                  <input type="number" step="0.1" name="l_bound_npd" value={plotParams.l_bound_npd} onChange={handlePlotParamChange} />
                </div>
                {testType === 4 && (
                  <div className="toggle-row" style={{ gridColumn: '1 / -1' }}>
                    <label htmlFor="apply_npd_cal" className="toggle-row-label">
                      Apply cable-loss calibration to NPD
                      <span className="toggle-row-hint">Unchecked = raw data as measured. S21 is always calibrated.</span>
                    </label>
                    <span className="toggle-switch">
                      <input
                        type="checkbox"
                        id="apply_npd_cal"
                        checked={!!plotParams.apply_npd_cal}
                        onChange={(e) => setPlotParams(prev => ({ ...prev, apply_npd_cal: e.target.checked }))}
                      />
                      <span className="toggle-switch-track"></span>
                    </span>
                  </div>
                )}
                
                <div className="toggle-row" style={{ gridColumn: '1 / -1' }}>
                  <label htmlFor="plot_s12" className="toggle-row-label">
                    Use S12 of SpecAn Calibration
                    <span className="toggle-row-hint">Check to use the S12 parameter of the SpecAn calibration file instead of S21.</span>
                  </label>
                  <span className="toggle-switch">
                    <input
                      type="checkbox"
                      id="plot_s12"
                      checked={!!plotParams.plot_s12}
                      onChange={(e) => setPlotParams(prev => ({ ...prev, plot_s12: e.target.checked }))}
                    />
                    <span className="toggle-switch-track"></span>
                  </span>
                </div>
              </div>



              {error && <div style={{ color: 'var(--error)', marginBottom: '1rem', padding: '1rem', background: 'rgba(239,68,68,0.1)', borderRadius: '8px' }}>{error}</div>}

              {warnings.length > 0 && (
                <div style={{ color: '#f59e0b', marginBottom: '1rem', padding: '1rem', background: 'rgba(245,158,11,0.1)', borderRadius: '8px' }}>
                  {warnings.map((w, i) => <div key={i}>{w}</div>)}
                </div>
              )}

              <button className="btn-primary" onClick={startProcessing} disabled={isProcessing} style={{ marginTop: '2rem' }}>
                {isProcessing ? <Activity className="animate-spin" size={18} /> : <Play size={18} />}
                {isProcessing ? 'Generating Plots...' : 'Generate Plots'}
              </button>

              {images.length > 0 && (
                <div style={{ marginTop: '2rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '1rem' }}>
                    <div>
                      <h3 style={{ margin: 0, marginBottom: '0.5rem' }}>Generated Plots ({images.length})</h3>

                    </div>
                    <div style={{ display: 'flex', gap: '1rem' }}>
                      <input 
                        type="file" 
                        multiple 
                        id="additionalCalInput" 
                        style={{ display: 'none' }} 
                        onChange={handleUploadAdditionalCalFiles} 
                        accept=".s2p" 
                      />
                      <button 
                        onClick={() => document.getElementById('additionalCalInput').click()} 
                        className="btn-primary" 
                        style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', width: 'auto', fontSize: '0.9rem' }}
                        disabled={isUploadingAdditionalCal}
                      >
                        <UploadCloud size={16} />
                        {isUploadingAdditionalCal ? 'Uploading...' : 'Upload Additional Cal Files'}
                      </button>
                      {additionalCalCount > 0 && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span style={{ fontSize: '0.9rem', color: 'var(--success, #10b981)' }}>
                            Loaded {additionalCalCount} extra cal file(s)
                          </span>
                          <button 
                            onClick={handleDeleteAdditionalCalFiles}
                            style={{ background: 'transparent', border: 'none', color: 'var(--error, #ef4444)', cursor: 'pointer', padding: '0.2rem', display: 'flex', alignItems: 'center' }}
                            title="Delete additional cal files"
                          >
                            <XCircle size={16} />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.85rem' }}>
                    {images.map((img, idx) => (
                      <div key={idx} style={{ background: 'var(--panel-bg)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border)', display: 'flex', flexDirection: 'column' }}>
                        <div style={{ width: '100%', height: '300px', position: 'relative' }}>
                          <InteractivePlot ref={el => plotRefs.current[idx] = el} plotData={img} />
                          
                          <div 
                            style={{ position: 'absolute', top: 5, right: 35, cursor: 'pointer', background: 'rgba(0,0,0,0.5)', padding: '4px', borderRadius: '4px', zIndex: 10 }}
                            onClick={() => {
                              const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(img));
                              const downloadAnchorNode = document.createElement('a');
                              downloadAnchorNode.setAttribute("href", dataStr);
                              downloadAnchorNode.setAttribute("download", img.filename.replace('.png', '.json'));
                              document.body.appendChild(downloadAnchorNode);
                              downloadAnchorNode.click();
                              downloadAnchorNode.remove();
                            }}
                            title="Download Debug JSON"
                          >
                            <span style={{color: 'white', fontSize: '10px', fontWeight: 'bold'}}>JSON</span>
                          </div>

                          <div 
                            style={{ position: 'absolute', top: 5, right: 5, cursor: 'pointer', background: 'rgba(0,0,0,0.5)', padding: '4px', borderRadius: '4px', zIndex: 10 }}
                            onClick={() => setSelectedIndex(idx)}
                            title="Expand Plot"
                          >
                            <Maximize2 size={16} color="#fff" />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="btn-group" style={{ display: 'flex', gap: '1rem' }}>
                <button 
                  className="secondary" 
                  onClick={() => setCurrentStep(1)}
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

      {/* Full-size Plot Viewer Modal */}
      {selectedIndex !== null && images[selectedIndex] && (
        <div
          onClick={() => setSelectedIndex(null)}
          style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.85)', zIndex: 10000,
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            padding: '2rem', cursor: 'zoom-out'
          }}
        >
          <button
            onClick={() => setSelectedIndex(null)}
            aria-label="Close"
            style={{
              position: 'absolute', top: '1.5rem', right: '1.5rem',
              background: 'rgba(255,255,255,0.1)', border: 'none', borderRadius: '50%',
              width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: 'pointer', color: '#fff'
            }}
          >
            <X size={22} />
          </button>

          {images.length > 1 && (
            <button
              onClick={(e) => { e.stopPropagation(); setSelectedIndex(i => (i - 1 + images.length) % images.length); }}
              aria-label="Previous plot"
              style={{
                position: 'absolute', top: '50%', left: '1.5rem', transform: 'translateY(-50%)',
                background: 'rgba(255,255,255,0.1)', border: 'none', borderRadius: '50%',
                width: '48px', height: '48px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                cursor: 'pointer', color: '#fff'
              }}
            >
              <ChevronLeft size={28} />
            </button>
          )}
          {images.length > 1 && (
            <button
              onClick={(e) => { e.stopPropagation(); setSelectedIndex(i => (i + 1) % images.length); }}
              aria-label="Next plot"
              style={{
                position: 'absolute', top: '50%', right: '1.5rem', transform: 'translateY(-50%)',
                background: 'rgba(255,255,255,0.1)', border: 'none', borderRadius: '50%',
                width: '48px', height: '48px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                cursor: 'pointer', color: '#fff'
              }}
            >
              <ChevronRight size={28} />
            </button>
          )}

          <div onClick={(e) => e.stopPropagation()} style={{ width: '90vw', height: '80vh', background: 'var(--panel-bg)', borderRadius: '8px', overflow: 'hidden', position: 'relative' }}>
            <InteractivePlot plotData={images[selectedIndex]} height="100%" />
          </div>
          <div style={{ marginTop: '1rem', color: '#fff', fontSize: '1rem', textAlign: 'center' }}>
            {images[selectedIndex].filename} ({selectedIndex + 1} / {images.length})
          </div>
        </div>
      )}
    </div>
  );
}


export default App;
