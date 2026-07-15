with open('backend/plot_generator.py', 'r') as f:
    content = f.read()

old_cal = """    cal_folder = ""
    if os.path.exists("Cal_Path.txt"):
        with open("Cal_Path.txt", "r") as f:
            cal_folder = f.read().strip()
    if not cal_folder and folderA:
        cal_folder = os.path.join(os.path.dirname(folderA), "Cable Loss")"""

new_cal = """    cal_folder = ""
    if len(runs) > 2 and runs[2]:
        cal_folder = runs[2]
    elif os.path.exists("Cal_Path.txt"):
        with open("Cal_Path.txt", "r") as f:
            cal_folder = f.read().strip()
    if not cal_folder and folderA:
        cal_folder = os.path.join(os.path.dirname(folderA), "Cable Loss")"""

content = content.replace(old_cal, new_cal)

with open('backend/plot_generator.py', 'w') as f:
    f.write(content)

with open('frontend/src/App.jsx', 'r') as f:
    content = f.read()

old_txt1 = '{testType === 3 ? "(Upload folders in order: Run A, then Run B, then Calibration)" : "(Click multiple times to add more runs!)"}'
new_txt1 = '{(testType === 3 || testType === 1) ? "(Upload folders in order: Run A, then Run B, then CalibrationFiles (Optional))" : "(Click multiple times to add more runs!)"}'
content = content.replace(old_txt1, new_txt1)

old_txt2 = """                          runs.filter(r => r !== '').length === 0 ? "Click to select Run A folder" :
                          runs.filter(r => r !== '').length === 1 ? "Click to select Run B folder" :
                          "Click to select Calibration (Cable Loss) folder"
                        ) : "Click to select and upload a run folder"}"""

new_txt2 = """                          runs.filter(r => r !== '').length === 0 ? "Click to select Run A folder" :
                          runs.filter(r => r !== '').length === 1 ? "Click to select Run B folder" :
                          "Click to select Calibration (Optional) folder"
                        ) : "Click to select and upload a run folder"}"""
content = content.replace(old_txt2, new_txt2)

old_txt3 = """                                {testType === 3 
                                  ? (idx === 0 ? 'Run A: ' : idx === 1 ? 'Run B: ' : 'Calibration: ') 
                                  : (runNames[idx] || `Run ${idx + 1}: `)}"""
new_txt3 = """                                {(testType === 3 || testType === 1)
                                  ? (idx === 0 ? 'Run A: ' : idx === 1 ? 'Run B: ' : 'Calibration: ') 
                                  : (runNames[idx] || `Run ${idx + 1}: `)}"""
content = content.replace(old_txt3, new_txt3)

with open('frontend/src/App.jsx', 'w') as f:
    f.write(content)
