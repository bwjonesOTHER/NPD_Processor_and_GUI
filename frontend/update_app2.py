import re

with open('src/App.jsx', 'r') as f:
    content = f.read()

# Add states
state_pattern = r'const \[testType, setTestType\] = useState\(null\);'
new_states = """const [testType, setTestType] = useState(null);
  const [test2Files, setTest2Files] = useState({ bench: null, temp: null, cal: null });
  const [generalFiles, setGeneralFiles] = useState(null);
  const [sessionData, setSessionData] = useState(null);"""
content = content.replace(state_pattern, new_states)

# Replace old handleDataSourceUpload with handleDataUpload
upload_func_pattern = r'const handleDataSourceUpload = async \(e\) => \{.*?\}\;'

new_upload_func = """const handleDataUpload = async () => {
    setIsUploadingSource(true);
    try {
      const data = new FormData();
      data.append('test_type', testType);
      
      if (testType === 2) {
        if (!test2Files.bench || test2Files.bench.length === 0) {
          alert('Bench Data Folder is required for Test 2');
          setIsUploadingSource(false);
          return;
        }
        Array.from(test2Files.bench).forEach(f => data.append('bench_files', f));
        if (test2Files.temp) Array.from(test2Files.temp).forEach(f => data.append('temp_files', f));
        if (test2Files.cal) Array.from(test2Files.cal).forEach(f => data.append('cal_files', f));
      } else {
        if (!generalFiles || generalFiles.length === 0) {
          alert('Test Data Folder is required');
          setIsUploadingSource(false);
          return;
        }
        Array.from(generalFiles).forEach(f => data.append('general_files', f));
      }

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
      
      // Update session data with paths and metadata
      setSessionData(json);
      
      // If Test 2 extracted metadata, apply it
      if (testType === 2 && json.metadata) {
        setFormData(prev => ({
          ...prev,
          serialNumber: json.metadata.sn || prev.serialNumber,
          pmaArea: json.metadata.pmaArea || prev.pmaArea
        }));
      }
      
      setCurrentStep(2);
    } catch (err) {
      alert("Error uploading data: " + err.message);
    } finally {
      setIsUploadingSource(false);
    }
  };"""

content = re.sub(upload_func_pattern, new_upload_func, content, flags=re.DOTALL)

with open('src/App.jsx', 'w') as f:
    f.write(content)
