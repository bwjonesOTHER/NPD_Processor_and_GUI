import os
import uuid
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import re

upload_bp = Blueprint('upload_bp', __name__)
TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp_uploads")

@upload_bp.route('/api/upload_test_data', methods=['POST'])
def upload_test_data():
    session_id = request.form.get('session_id') or str(uuid.uuid4())
    test_type = request.form.get('test_type', type=int)
    
    session_dir = os.path.join(TEMP_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Categories of files we expect
    categories = ['bench', 'temp', 'cal', 'general']
    paths = {}
    
    for cat in categories:
        files = request.files.getlist(f'{cat}_files')
        if files and any(f.filename for f in files):
            cat_dir = os.path.join(session_dir, cat)
            os.makedirs(cat_dir, exist_ok=True)
            paths[cat] = cat_dir
            for file in files:
                if file.filename:
                    # Preserve directory structure
                    rel_path = file.filename
                    if rel_path:
                        # Split path and secure each part
                        parts = rel_path.replace('\\', '/').split('/')
                        safe_parts = [secure_filename(p) for p in parts if p]
                        if safe_parts:
                            safe_path = os.path.join(cat_dir, *safe_parts)
                            os.makedirs(os.path.dirname(safe_path), exist_ok=True)
                            file.save(safe_path)
    
    # Metadata parsing
    metadata = {}
    if test_type == 2 and 'bench' in paths:
        bench_dir = paths['bench']
        area = None
        sn = None
        
        # Regex to find something like SN1234, SN_1234, EM-1234
        sn_pattern = re.compile(r'(?:SN|EM-)[_-]?(\d+)', re.IGNORECASE)
        # Regex to find Area, e.g., Area1, Area_1
        area_pattern = re.compile(r'Area[_-]?(\d+)', re.IGNORECASE)
        
        for root, dirs, files in os.walk(bench_dir):
            for f in files:
                if not f.lower().endswith('.csv'): continue
                if not sn:
                    m = sn_pattern.search(f)
                    if m:
                        sn = m.group(1)
                if not area:
                    m = area_pattern.search(f)
                    if m:
                        area = f"Area{m.group(1)}"
                if sn and area:
                    break
            if sn and area:
                break
                
        metadata['sn'] = sn
        metadata['pmaArea'] = area
        
        # Validate Temp files
        if 'temp' in paths and sn:
            temp_dir = paths['temp']
            matching_files = []
            for root, dirs, files in os.walk(temp_dir):
                for f in files:
                    if sn in f:
                        matching_files.append(f)
            if not matching_files:
                return jsonify({"success": False, "error": f"Failed to Locate matching Temp files for SN {sn}"}), 400
                
    return jsonify({"success": True, "session_id": session_id, "paths": paths, "metadata": metadata})
