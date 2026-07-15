import requests

# 1. file-info
res = requests.post('http://127.0.0.1:5001/api/file-info', json={
    'testType': 2,
    'uploadMode': 'upload',
    'pmaArea': 'L110173C',
    'lmoNumber': '1234',
    'serialNumber': '0001'
})
print("file-info:", res.json())

# 2. generate plots
res2 = requests.post('http://127.0.0.1:5001/api/generate_plots?testType=2', json={
    'testType': 2,
    'outputFolder': '',
    'dataSource': '',
    'freq_min': 2.7,
    'freq_max': 4.1,
    'reqS11Val': -10,
    'n_avg': 20
})
print("generate_plots:", res2.json())

