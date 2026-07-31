import React, { useState, useRef, useEffect } from 'react';
import { UploadCloud, XCircle, Activity, Play, Download } from 'lucide-react';
import JSZip from 'jszip';
import InteractivePlot from './InteractivePlot';

export default function GenericPlotter({ API_BASE, onBack }) {
  const [dataFiles, setDataFiles] = useState([]);
  const [calFiles, setCalFiles] = useState([]);
  
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  
  const [imagesCSV, setImagesCSV] = useState([]);
  const [imagesS2P, setImagesS2P] = useState([]);
  
  const [activeTab, setActiveTab] = useState('csv'); // 'csv' or 's2p'
  
  const [isUploadingRefFile, setIsUploadingRefFile] = useState(false);
  
  const [plotParams, setPlotParams] = useState({
    freq_min: '',
    freq_max: '',
    plot_s12: false,
    plot_density: false,
    n_avg: 1,
    y_upper_npd: '',
    y_lower_npd: '',
    u_bound_npd: '',
    l_bound_npd: '',
    y_upper_s21: '',
    y_lower_s21: '',
    u_bound_s21: '',
    l_bound_s21: '',
    average_data_path: '',
    plot_trace_s2p: 'S21'
  });

  const dataPlotRefs = useRef([]);
  const s2pPlotRefs = useRef([]);

  const handleDataUpload = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    
    setIsUploading(true);
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) formData.append('files', files[i]);
    formData.append('type', 'data');
    
    try {
      const res = await fetch(`${API_BASE}/upload_generic`, { method: 'POST', body: formData });
      if (res.ok) {
        const data = await res.json();
        setDataFiles(data.files || []);
      } else {
        alert("Upload failed.");
      }
    } catch (err) {
      alert("Error uploading: " + err.message);
    } finally {
      setIsUploading(false);
      e.target.value = null;
    }
  };

  const handleCalUpload = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    
    setIsUploading(true);
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) formData.append('files', files[i]);
    formData.append('type', 'cal');
    
    try {
      const res = await fetch(`${API_BASE}/upload_generic`, { method: 'POST', body: formData });
      if (res.ok) {
        const data = await res.json();
        setCalFiles(data.files || []);
      } else {
        alert("Upload failed.");
      }
    } catch (err) {
      alert("Error uploading: " + err.message);
    } finally {
      setIsUploading(false);
      e.target.value = null;
    }
  };

  const handleClear = async (type) => {
    try {
      await fetch(`${API_BASE}/clear_generic?type=${type}`, { method: 'POST' });
      if (type === 'data') setDataFiles([]);
      if (type === 'cal') setCalFiles([]);
    } catch (err) {
      console.error(err);
    }
  };

  const [isDraggingData, setIsDraggingData] = useState(false);
  const [isDraggingCal, setIsDraggingCal] = useState(false);

  const handleDragOver = (e, setDragging) => {
    e.preventDefault();
    setDragging(true);
  };
  
  const handleDragLeave = (e, setDragging) => {
    e.preventDefault();
    setDragging(false);
  };
  
  const handleDropData = (e) => {
    e.preventDefault();
    setIsDraggingData(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleDataUpload({ target: { files: e.dataTransfer.files } });
    }
  };
  
  const handleDropCal = (e) => {
    e.preventDefault();
    setIsDraggingCal(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleCalUpload({ target: { files: e.dataTransfer.files } });
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
        alert('Upload error: ' + (json.error || 'Unknown error'));
      }
    } catch (err) {
      alert('Upload error: ' + err.message);
    } finally {
      setIsUploadingRefFile(false);
      e.target.value = '';
    }
  };

  const generatePlots = async () => {
    if (dataFiles.length === 0) {
      setError("Please upload at least one File (CSV or S2P).");
      return;
    }
    setError(null);
    setIsProcessing(true);
    
    try {
      const res = await fetch(`${API_BASE}/generate_plots?testType=5`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...plotParams })
      });
      const data = await res.json();
      if (res.ok) {
        setImagesCSV(data.plots_csv || []);
        setImagesS2P(data.plots_s21 || []);
        if (data.n_avg_used !== undefined && data.n_avg_used !== null) {
          setPlotParams(prev => ({ ...prev, n_avg: data.n_avg_used }));
        }
        if ((data.plots_csv || []).length === 0 && (data.plots_s21 || []).length > 0) {
          setActiveTab('s2p');
        } else {
          setActiveTab('csv');
        }
      } else {
        setError(data.error || 'Failed to generate plots');
      }
    } catch (err) {
      setError("Connection to server failed.");
    } finally {
      setIsProcessing(false);
    }
  };

  const exportZip = async () => {
    const images = activeTab === 'csv' ? imagesCSV : imagesS2P;
    const refs = activeTab === 'csv' ? dataPlotRefs : s2pPlotRefs;
    if (images.length === 0) return;
    
    try {
      const zip = new JSZip();
      for (let i = 0; i < images.length; i++) {
        if (refs.current[i]) {
          const imgData = await refs.current[i].toImage();
          if (imgData) {
            const base64Data = imgData.data.split(',')[1];
            zip.file(imgData.filename, base64Data, { base64: true });
          }
        }
      }
      const content = await zip.generateAsync({ type: 'blob' });
      const url = window.URL.createObjectURL(content);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Generic_Plots_${activeTab}.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert("Export failed: " + err.message);
    }
  };

  const currentImages = activeTab === 'csv' ? imagesCSV : imagesS2P;
  const currentRefs = activeTab === 'csv' ? dataPlotRefs : s2pPlotRefs;

  const hasS2P = dataFiles.some(f => typeof f === 'string' && f.toLowerCase().endsWith('.s2p'));

  return (
    <div style={{ display: 'flex', gap: '2rem', marginTop: '1rem' }}>
      {/* Sidebar */}
      <div style={{ width: '300px', flexShrink: 0, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <button onClick={onBack} className="btn-secondary" style={{ marginBottom: '1rem' }}>
          &larr; Back to Test Selection
        </button>
        
        <div style={{ background: 'var(--panel-bg)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border)' }}>
          <h3 style={{ marginTop: 0 }}>Upload Files</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Upload CSV or S2P files for plotting.</p>
          <input type="file" multiple id="genericDataUpload" style={{ display: 'none' }} onChange={handleDataUpload} />
          <div 
            onClick={() => document.getElementById('genericDataUpload').click()}
            onDragOver={(e) => handleDragOver(e, setIsDraggingData)}
            onDragLeave={(e) => handleDragLeave(e, setIsDraggingData)}
            onDrop={handleDropData}
            style={{ 
              border: `2px dashed ${isDraggingData ? 'var(--accent)' : 'var(--border)'}`, 
              padding: '2rem 1rem', 
              textAlign: 'center', 
              borderRadius: '8px', 
              cursor: 'pointer', 
              background: isDraggingData ? 'rgba(var(--accent-rgb), 0.1)' : 'rgba(0,0,0,0.2)', 
              marginBottom: '1rem',
              transition: 'all 0.2s ease'
            }}
          >
            <UploadCloud size={32} color={isDraggingData ? "var(--text)" : "var(--accent)"} style={{ marginBottom: '0.5rem' }} />
            <div>{isDraggingData ? "Drop Files Here" : "Click or Drag Files here"}</div>
          </div>
          {dataFiles.length > 0 && (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.9rem' }}>
              <span style={{ color: 'var(--success)' }}>{dataFiles.length} file(s) loaded</span>
              <button onClick={() => handleClear('data')} style={{ background: 'none', border: 'none', color: 'var(--error)', cursor: 'pointer' }}><XCircle size={16} /></button>
            </div>
          )}
        </div>
        
        <div style={{ background: 'var(--panel-bg)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border)' }}>
          <h3 style={{ marginTop: 0 }}>Upload Calibration Files</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Optional .s2p calibration files to apply to Data plots.</p>
          <input type="file" multiple id="genericCalUpload" style={{ display: 'none' }} onChange={handleCalUpload} accept=".s2p" />
          <div 
            onClick={() => document.getElementById('genericCalUpload').click()}
            onDragOver={(e) => handleDragOver(e, setIsDraggingCal)}
            onDragLeave={(e) => handleDragLeave(e, setIsDraggingCal)}
            onDrop={handleDropCal}
            style={{ 
              border: `2px dashed ${isDraggingCal ? 'var(--accent)' : 'var(--border)'}`, 
              padding: '2rem 1rem', 
              textAlign: 'center', 
              borderRadius: '8px', 
              cursor: 'pointer', 
              background: isDraggingCal ? 'rgba(var(--accent-rgb), 0.1)' : 'rgba(0,0,0,0.2)', 
              marginBottom: '1rem',
              transition: 'all 0.2s ease'
            }}
          >
            <UploadCloud size={32} color={isDraggingCal ? "var(--text)" : "var(--accent)"} style={{ marginBottom: '0.5rem' }} />
            <div>{isDraggingCal ? "Drop Cal Files Here" : "Click or Drag Cal files here"}</div>
          </div>
          {calFiles.length > 0 && (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.9rem' }}>
              <span style={{ color: 'var(--success)' }}>{calFiles.length} file(s) loaded</span>
              <button onClick={() => handleClear('cal')} style={{ background: 'none', border: 'none', color: 'var(--error)', cursor: 'pointer' }}><XCircle size={16} /></button>
            </div>
          )}
        </div>
      </div>
      
      {/* Main Content */}
      <div style={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>

        <div style={{ background: 'var(--panel-bg)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border)', marginBottom: '1rem' }}>
          <div className="form-grid">
            <div className="input-group">
              <label>Min Frequency (GHz)</label>
              <input type="number" step="0.1" value={plotParams.freq_min} onChange={e => setPlotParams({...plotParams, freq_min: e.target.value})} placeholder="Auto" />
            </div>
            <div className="input-group">
              <label>Max Frequency (GHz)</label>
              <input type="number" step="0.1" value={plotParams.freq_max} onChange={e => setPlotParams({...plotParams, freq_max: e.target.value})} placeholder="Auto" />
            </div>
            <div className="input-group">
              <label>Averaging (n_avg)</label>
              <input type="number" step="1" min="1" value={plotParams.n_avg} onChange={e => setPlotParams({...plotParams, n_avg: e.target.value})} placeholder="1" />
            </div>
            <div className="input-group">
              <label>Average Data File</label>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <button
                  type="button"
                  className="secondary"
                  disabled={isUploadingRefFile}
                  onClick={() => document.getElementById('genericRefFileInput').click()}
                  style={{ padding: '0.5rem 1rem', whiteSpace: 'nowrap' }}
                >
                  {isUploadingRefFile ? 'Uploading...' : 'Upload File'}
                </button>
                <span style={{ fontSize: '0.8rem', color: plotParams.average_data_path ? 'var(--text-main)' : 'var(--text-muted)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {plotParams.average_data_path
                    ? plotParams.average_data_path.split(/[/\\]/).pop()
                    : 'No file selected'}
                </span>
              </div>
              <input
                type="file"
                id="genericRefFileInput"
                accept=".xlsx,.xls,.csv"
                style={{ display: 'none' }}
                onChange={handleReferenceFileUpload}
              />
            </div>
            <div className="input-group">
              <label>S21 Upper Bound Offset</label>
              <input type="number" step="0.1" value={plotParams.u_bound_s21} onChange={e => setPlotParams({...plotParams, u_bound_s21: e.target.value})} placeholder="2" />
            </div>
            <div className="input-group">
              <label>S21 Lower Bound Offset</label>
              <input type="number" step="0.1" value={plotParams.l_bound_s21} onChange={e => setPlotParams({...plotParams, l_bound_s21: e.target.value})} placeholder="2" />
            </div>
            <div className="input-group">
              <label>NPD Upper Bound Offset</label>
              <input type="number" step="0.1" value={plotParams.u_bound_npd} onChange={e => setPlotParams({...plotParams, u_bound_npd: e.target.value})} placeholder="2" />
            </div>
            <div className="input-group">
              <label>NPD Lower Bound Offset</label>
              <input type="number" step="0.1" value={plotParams.l_bound_npd} onChange={e => setPlotParams({...plotParams, l_bound_npd: e.target.value})} placeholder="2" />
            </div>
            <div className="input-group">
              <label>Plot Options</label>
              <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'flex-start', minHeight: '38px', marginTop: '0.2rem' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>SpecAn Cal</span>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer', margin: 0, fontWeight: 'normal', fontSize: '0.9rem' }}>
                    <span>S21</span>
                    <span className="toggle-switch" style={{ transform: 'scale(0.85)', margin: '0' }}>
                      <input
                        type="checkbox"
                        checked={!!plotParams.plot_s12}
                        onChange={e => setPlotParams({...plotParams, plot_s12: e.target.checked})}
                      />
                      <span className="toggle-switch-track"></span>
                    </span>
                    <span>S12</span>
                  </label>
                </div>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Data Type</span>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer', margin: 0, fontWeight: 'normal', fontSize: '0.9rem' }}>
                    <span>NP</span>
                    <span className="toggle-switch" style={{ transform: 'scale(0.85)', margin: '0' }}>
                      <input
                        type="checkbox"
                        checked={!!plotParams.plot_density}
                        onChange={e => setPlotParams({...plotParams, plot_density: e.target.checked})}
                      />
                      <span className="toggle-switch-track"></span>
                    </span>
                    <span>NPD</span>
                  </label>
                </div>
                {hasS2P && (
                  <select 
                    value={plotParams.plot_trace_s2p} 
                    onChange={e => setPlotParams({...plotParams, plot_trace_s2p: e.target.value})}
                    style={{ padding: '0.2rem', marginLeft: '0.5rem', borderRadius: '4px', border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text)' }}
                  >
                    <option value="S11">S11</option>
                    <option value="S21">S21</option>
                    <option value="S12">S12</option>
                    <option value="S22">S22</option>
                  </select>
                )}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
            <button className="btn-primary" onClick={generatePlots} disabled={isProcessing || isUploading} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              {isProcessing ? <Activity className="animate-spin" size={18} /> : <Play size={18} />}
              Generate Plots
            </button>
          </div>
        </div>
        
        {error && <div style={{ color: 'var(--error)', marginBottom: '1rem', padding: '1rem', background: 'rgba(239,68,68,0.1)', borderRadius: '8px' }}>{error}</div>}
        
        {/* Tabs */}
        {(imagesCSV.length > 0 || imagesS2P.length > 0) && (
          <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', borderBottom: '1px solid var(--border)' }}>
            <button 
              onClick={() => setActiveTab('csv')} 
              style={{ background: 'none', border: 'none', padding: '0.5rem 1rem', borderBottom: activeTab === 'csv' ? '2px solid var(--accent)' : '2px solid transparent', color: activeTab === 'csv' ? 'var(--text)' : 'var(--text-muted)', cursor: 'pointer', fontSize: '1.1rem', fontWeight: 600 }}
            >
              CSV (NP/NPD) ({imagesCSV.length})
            </button>
            <button 
              onClick={() => setActiveTab('s2p')} 
              style={{ background: 'none', border: 'none', padding: '0.5rem 1rem', borderBottom: activeTab === 's2p' ? '2px solid var(--accent)' : '2px solid transparent', color: activeTab === 's2p' ? 'var(--text)' : 'var(--text-muted)', cursor: 'pointer', fontSize: '1.1rem', fontWeight: 600 }}
            >
              S2P ({imagesS2P.length})
            </button>
            
            <div style={{ marginLeft: 'auto', marginBottom: '0.5rem' }}>
              <button onClick={exportZip} className="btn-primary" style={{ padding: '0.5rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}>
                <Download size={16} />
                Export {activeTab.toUpperCase()} Plots
              </button>
            </div>
          </div>
        )}
        
        <div style={{ flexGrow: 1 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {currentImages.map((img, idx) => (
              <div key={idx} style={{ background: 'var(--panel-bg)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border)' }}>
                <div style={{ width: '100%', height: '700px' }}>
                  <InteractivePlot ref={el => currentRefs.current[idx] = el} plotData={img} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
