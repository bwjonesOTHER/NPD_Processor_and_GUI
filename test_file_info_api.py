import requests
import json

url = "http://127.0.0.1:5000/api/file-info"
data = {
    "testType": 2,
    "basePath": "./TestArea",
    "pmaArea": "",
    "lmoNumber": "123",
    "serialNumber": "0001"
}

try:
    res = requests.post(url, json=data)
    print(res.status_code)
    print(res.text)
except Exception as e:
    print(e)
