import sys
import re

with open('frontend/src/App.jsx', 'r') as f:
    content = f.read()

start_idx = content.find('const handleDataUpload = async () => {')
end_idx = content.find('const uploadFiles = async () => {')

if start_idx == -1 or end_idx == -1:
    print("Could not find handleDataUpload")
    sys.exit(1)

new_handleDataUpload = """const handleDataUpload = async () => {
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
        if (test2Files.tempCal) Array.from(test2Files.tempCal).forEach(f => data.append('temp_cal_files', f));
      } else if (testType === 3) {
        if (!test3Files.runA || !test3Files.runB || !test3Files.cal) {
          alert('Run 1, Run 2, and Calibration folders are required for Test 3');
          setIsUploadingSource(false);
          return;
        }
        Array.from(test3Files.runA).forEach(f => data.append('runA_files', f));
        Array.from(test3Files.runB).forEach(f => data.append('runB_files', f));
        Array.from(test3Files.cal).forEach(f => data.append('cal_files', f));
      } else if (testType === 4) {
        if (!generalFiles || generalFiles.length === 0) {
          alert('Test Data Folder is required for Test 4');
          setIsUploadingSource(false);
          return;
        }
        Array.from(generalFiles).forEach(f => data.append('general_files', f));
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

  """

content = content[:start_idx] + new_handleDataUpload + content[end_idx:]

with open('frontend/src/App.jsx', 'w') as f:
    f.write(content)
