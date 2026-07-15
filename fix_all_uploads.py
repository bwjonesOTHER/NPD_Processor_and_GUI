import re

with open('frontend/src/App.jsx', 'r') as f:
    content = f.read()

# Append testType to uploadRuns form data
old_upload = """        data.append('run_index', '0');
        data.append('chunk_index', i === 0 ? '0' : '1');
        
        const res = await fetch(`${API_BASE}/upload_run`"""

new_upload = """        data.append('run_index', '0');
        data.append('chunk_index', i === 0 ? '0' : '1');
        data.append('testType', testType);
        
        const res = await fetch(`${API_BASE}/upload_run`"""
content = content.replace(old_upload, new_upload)

old_upload_chunks = """                            data.append('chunk_index', i === 0 ? '0' : '1');
                            
                            const res = await fetch(`${API_BASE}/upload_run`"""

new_upload_chunks = """                            data.append('chunk_index', i === 0 ? '0' : '1');
                            data.append('testType', testType);
                            
                            const res = await fetch(`${API_BASE}/upload_run`"""
content = content.replace(old_upload_chunks, new_upload_chunks)

with open('frontend/src/App.jsx', 'w') as f:
    f.write(content)

with open('backend/app.py', 'r') as f:
    content = f.read()

# Fix upload_run in backend to use testType for isolation and completely ignore .txt files
old_backend_upload = """    chunk_index = request.form.get('chunk_index', '0')
    base_path = read_txt("upload_path.txt")
    if not base_path:
        # Fallback strictly to local uploads folder so we don't accidentally write to the user's root directory from a previous test
        base_path = os.path.join(os.getcwd(), 'uploads')
        
    if folder_name:
        dest_folder = os.path.join(base_path, folder_name)
    else:
        dest_folder = os.path.join(base_path, f'Run_{run_index}')"""

new_backend_upload = """    chunk_index = request.form.get('chunk_index', '0')
    test_type = request.form.get('testType', '1')
    
    # Completely sever ties to upload_path.txt and path.txt. 
    # Uploaded runs ALWAYS go into a strict, isolated local test folder.
    base_path = os.path.join(os.getcwd(), 'uploads', f'Test{test_type}')
        
    if folder_name:
        dest_folder = os.path.join(base_path, folder_name)
    else:
        dest_folder = os.path.join(base_path, f'Run_{run_index}')"""
content = content.replace(old_backend_upload, new_backend_upload)

# Fix generate_plots in backend for Test 1 to correctly read from the isolated Test 1 folder instead of the old txt files
old_test1_generate = """    # Gather paths based on the test type for backward compatibility with existing text file logic
    if test == 1:
        runs = []
        if os.path.exists("SelectedRuns.txt"):
            with open("SelectedRuns.txt", "r") as f:
                runs = [line.strip() for line in f if line.strip()]
        else:
            run_a = read_txt("RunA_Path.txt")
            run_b = read_txt("RunB_Path.txt")
            runs = [run for run in [run_a, run_b] if run]
        params['runs'] = runs"""

new_test1_generate = """    # Gather paths based on the test type for backward compatibility with existing text file logic
    if test == 1:
        runs = []
        # If in Upload mode, the runs are in uploads/Test1. The frontend passes dataSource as the path if we used Access mode.
        # But wait! For Test 1, the user uploads runs via Step 3 "Select Runs", which puts them in uploads/Test1!
        # So we should just read the directories from uploads/Test1!
        test1_dir = os.path.join(os.getcwd(), 'uploads', 'Test1')
        if os.path.exists(test1_dir):
            runs = [os.path.join(test1_dir, d) for d in os.listdir(test1_dir) if os.path.isdir(os.path.join(test1_dir, d))]
        params['runs'] = sorted(runs)"""
content = content.replace(old_test1_generate, new_test1_generate)

with open('backend/app.py', 'w') as f:
    f.write(content)
