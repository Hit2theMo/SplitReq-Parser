import requests
import json
payload = {"mytext": "lalala"}
res = requests.post('http://127.0.0.1:5000/api/v1/cvparser/', json=json.dumps(payload))
print(res)
if res.ok:
    print(res.json())
