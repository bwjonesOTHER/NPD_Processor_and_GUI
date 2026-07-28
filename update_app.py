import re

with open('backend/app.py', 'r') as f:
    content = f.read()

upload_test_data_endpoint = """
@app.route('/api/upload_test_data', methods=['POST'])
def upload_test_data():
    test_type = request.form.get('test_type', '1')
    
    base_path = os.path.join(os.getcwd(), 'uploads', f'Test{test_type}')
    
    # Always clear the test directory before uploading new data
    if os.path.exists(base_path):
        import shutil
        shutil.rmtree(base_path)
    os.makedirs(base_path, exist_ok=True)
    
    def save_files(files_list, subfolder):
        dest_folder = os.path.join(base_path, subfolder)
        os.makedirs(dest_folder, exist_ok=True)
        for file in files_list:
            if file.filename:
                # Keep original folder structure if present
                rel_path = file.filename
                if '/' in rel_path:
                    # Strip the first folder name to avoid nested roots
                    parts = rel_path.split('/')
                    if len(parts) > 1:
                        rel_path = '/'.join(parts[1:])
                
                filepath = os.path.join(dest_folder, rel_path)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
        return dest_folder
        
    paths = {}
    if test_type == '2':
        paths['bench'] = save_files(request.files.getlist('bench_files'), 'Bench')
        paths['temp'] = save_files(request.files.getlist('temp_files'), 'Temp')
        paths['cal'] = save_files(request.files.getlist('cal_files'), 'Bench_Cal')
        paths['tempCal'] = save_files(request.files.getlist('temp_cal_files'), 'Temp_Cal')
    elif test_type == '3':
        paths['runA'] = save_files(request.files.getlist('runA_files'), 'Run_0')
        paths['runB'] = save_files(request.files.getlist('runB_files'), 'Run_1')
        paths['cal'] = save_files(request.files.getlist('cal_files'), 'Run_2')
        paths['runs'] = [paths['runA'], paths['runB'], paths['cal']]
    else:
        paths['general'] = save_files(request.files.getlist('general_files'), 'Data')
        
    return jsonify({
        "success": True,
        "paths": paths
    })
"""

# Insert it before @app.route('/api/upload_run')
content = content.replace("@app.route('/api/upload_run'", upload_test_data_endpoint + "\n@app.route('/api/upload_run'")

with open('backend/app.py', 'w') as f:
    f.write(content)
