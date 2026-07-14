import requests

try:
    r = requests.post("http://localhost:5001/api/select-runs", json={
        "runA": "A",
        "runB": "B",
        "calPath": "C:\\fake\\Cable Loss"
    })
    print("Response:", r.status_code, r.text)
    with open("Cal_Path.txt", "r") as f:
        print("Cal_Path.txt:", f.read())
except Exception as e:
    print(e)
