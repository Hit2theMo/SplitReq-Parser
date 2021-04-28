import requests
import json
import base64
import os
import time

path = r'uploaded_files\zipped_resume.zip'
path = r'uploaded_files\Linda_Chang.zip'
# file_name, file_extension = os.path.splitext(path)
file_name, file_extension = os.path.basename(path).split('.')

print(file_name)
print(file_extension)
try:
    with open(path, 'rb') as f:
        base64str = base64.b64encode(f.read()).decode('UTF-8')
except UnicodeDecodeError:
    print("critical", "Unicode Decode error while converting file to Base64 string-", __name__, 1)
except Exception:
    print("critical",
          "Some other error occured while converting file to Base64 string", __name__, 1)

payload = {
    "ZipAsBase64String": base64str
}
headers = {
    "username": "markabbot",
    "api-token": "123abc456"
}
res = requests.post('http://127.0.0.1:5000/api/v1/cvparser/batch',
                    json=json.dumps(payload), headers=headers)
print(res.text)
print(time.perf_counter())
