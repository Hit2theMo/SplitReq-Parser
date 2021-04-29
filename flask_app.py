from datetime import datetime, date
from resume_parser import extractDataPoints
from flask import Flask, jsonify, request
import json
import base64
import shortuuid
import pathlib
import zipfile
from batch_parsing import parseUnzippedResumes

API_KEY = '123abc456'
UPLOAD_PATH = 'uploaded_files'
BATCH_UNZIP_PATH = 'batch_parsing'
time_now = str(datetime.utcnow().date())
print(time_now)
date = time_now.split('-')
batch_id = ''.join(date)
print(time_now)

app = Flask(__name__)


username_err_msg = {
    "Error": "Invalid Account",
    "Message": "Please add your account id in the 'username' POST header"
}

invalid_token_err = {
    "Error": "Authentication Failed",
    "Message": "Please add a valid token in the 'api-token' POST header"
}

invalid_b64_doc = {
    "Error": "Invalid Document",
    "Message": "Please send a valid Resume file in the JSON payload with Key- 'ResumeAsBase64String'"
}


# def authenticate(username, key):
#     if key == API_KEY:
#         print("Authenticated user '{0}' with key '{1}'".format(username, key))
#         return 'success'
#     else:
#         print("Authentication failed for user '{0}' with key '{1}'".format(username, key))
#         return 'fail'


def generate_filename(batch, org_name=None):
    uuid = shortuuid.ShortUUID()
    if batch:
        return uuid.uuid()
    else:
        file_name = org_name.strip() + '_' + uuid.uuid()
        return file_name


def unzipFile(base_unzip_path, uploaded_zip_path, zip_name):
    unzip_path = pathlib.PurePath(base_unzip_path, zip_name)
    # Create Folder for Files to be unzipped
    pathlib.Path(unzip_path).mkdir(parents=False, exist_ok=False)

    with zipfile.ZipFile(uploaded_zip_path, 'r') as zip_ref:
        zip_ref.extractall(unzip_path)
    return unzip_path


def base64ToDocument(data, path, file_name, extn):
    file_path = pathlib.PurePath(path, file_name + '.' + extn.lower())
    # try:
    with open(file_path, "wb") as fh:
        fh.write(base64.b64decode(data))
    return file_path
    # except Exception:
    #     return 'fail'
    # else:
    #     return file_path


def authenticate(headers):
    if 'username' in headers:
        username = headers['username']
    else:
        return jsonify(username_err_msg)
    if 'api-token' in headers:
        api_token = headers['api-token']
        if api_token == API_KEY:
            print("Authenticated user '{0}' with key '{1}'".format(username, api_token))
            return 'success'
        else:
            print("Authentication failed for user '{0}' with key '{1}'".format(username, api_token))
            return jsonify(invalid_token_err)
    else:
        return jsonify(invalid_token_err)

# ----------------------------------------------------------------------------------------------------------------------


@app.route('/api/v1/cvparser/single', methods=['POST'])
def parseResume():
    # Get headers
    headers = request.headers
    # Authenticate the POST request or return appt error messages
    status = authenticate(headers)
    if status != 'success':
        return status

    # Read the Resume in Base64 Encoded string
    # Check if content-type= application/json has to be forced
    payload = json.loads(request.get_json(force=True))
    if 'ResumeAsBase64String' in payload and 'file_extension' in payload and 'file_name' in payload:
        b64str = payload['ResumeAsBase64String']
        file_extn = payload['file_extension']
        org_file_name = payload['file_name']
    else:
        return jsonify(invalid_b64_doc)

    # Convert Resume from Base64 String to Document
    unique_file_name = generate_filename(False, org_file_name)
    file_path = base64ToDocument(b64str, UPLOAD_PATH, unique_file_name, file_extn)
    if file_path == 'fail':
        return jsonify(invalid_b64_doc)

    # Call the Parsing script and send the file path as param
    print(file_path)
    final_output = extractDataPoints(file_path, file_extn)
    return jsonify(final_output)

# ----------------------------------------------------------------------------------------------------------------------


@ app.route('/api/v1/cvparser/batch', methods=['POST'])
def batchResumeParsing():
    headers = request.headers
    status = authenticate(headers)
    if status != 'success':
        return status

    payload = json.loads(request.get_json(force=True))
    if 'ZipAsBase64String' in payload:
        b64str = payload['ZipAsBase64String']
    else:
        return jsonify(invalid_b64_doc)

    unique_file_name = generate_filename(batch=True)
    zip_file_path = base64ToDocument(b64str, UPLOAD_PATH, unique_file_name, 'zip')
    unzip_path = unzipFile(BATCH_UNZIP_PATH, zip_file_path, unique_file_name)
    batch_output = parseUnzippedResumes(unzip_path)
    # return batch_output
    return jsonify(batch_output)


if __name__ == '__main__':
    app.run(debug=True)
