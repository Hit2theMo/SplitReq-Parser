from pprint import pprint
import requests
import json
import base64
import os
import time
from pprint import pprint

# log_file_path = os.path.join('logs', 'sample.log')

# logger = logging.getLogger(__name__)
# file_handler = logging.FileHandler(log_file_path)
# file_handler.setLevel(logging.ERROR)
# formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
# file_handler.setFormatter(formatter)

# logger.addHandler(file_handler)
# logger.setLevel(logging.INFO)

path = r"uploaded_files\zipped_resume.zip"
path = r"uploaded_files\Linda_Chang.zip"
path = r"uploaded_files\zip_test_3.zip"
# path = r"uploaded_files\zipzip_test_4.zip"
path = r"uploaded_files\zip_test_1.zip"
path = r'uploaded_files\batch_zip_test_5.zip'
path = r'uploaded_files\Justin Yung.zip'
# path = r"uploaded_files\zip_test_4.zip"
# file_name, file_extension = os.path.splitext(path)
file_name, file_extension = os.path.basename(path).split(".")

print(file_name)
print(file_extension)
try:
    with open(path, "rb") as f:
        base64str = base64.b64encode(f.read()).decode("UTF-8")
except UnicodeDecodeError:
    print(
        "critical",
        "Unicode Decode error while converting file to Base64 string-",
        __name__,
        1,
    )
except Exception:
    print(
        "critical",
        "Some other error occured while converting file to Base64 string",
        __name__,
        1,
    )

payload = {"ZipAsBase64String": base64str}

headers = {
    "username": "markabbot",
    "api-token": "ab8a7ff7-6659-4a44-b7d9-064612d825fa"
}
res = requests.post(
    "http://149.28.197.77/api/v1/cvparser/batch",
    json=payload,
    headers=headers,
)
# print(res.text)
print(time.perf_counter())
pprint(json.loads(res.text))
print(res.json())
