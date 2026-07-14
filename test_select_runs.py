import requests

payload = {
    "runA": "dummy_runA",
    "runB": "dummy_runB",
    "calPath": "C:\\fake\\Cable Loss"
}

try:
    r = requests.post("http://localhost:5001/api/select-runs", json=payload)
    print("Response:", r.status_code, r.text)
    with open("Cal_Path.txt", "r") as f:
        print("Cal_Path.txt contains:", f.read())
except Exception as e:
    print("Error:", e)
