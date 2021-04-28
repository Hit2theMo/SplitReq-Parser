from flask import Flask, jsonify, request
import json
import base64
from resume_parser import extractDataPoints

API_KEY = '123abc456'
UPLOAD_FOLDER = 'uploaded_files'
app = Flask(__name__)

account_err_msg = {
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


def authenticate(username, key):
    if key == API_KEY:
        print("Authenticated user '{0}' with key '{1}'".format(username, key))
        return 'success'
    else:
        print("Authentication failed for user '{0}' with key '{1}'".format(username, key))
        return 'fail'


def base64ToDocument(data, path, extn):
    file_path = path+r"\file."+extn
    try:
        with open(file_path, "wb") as fh:
            fh.write(base64.b64decode(data))
    except Exception:
        return 'fail'
    else:
        return file_path


@app.route('/api/v1/cvparser/single', methods=['POST'])
def parseResume():
    # Get headers
    headers = request.headers
    # Authenticate the POST request or return appt error messages
    if 'username' in headers:
        username = headers['username']
    else:
        return jsonify(account_err_msg)
    if 'api-token' in headers:
        api_token = headers['api-token']
        auth = authenticate(username, api_token)
        if auth == 'fail':
            return jsonify(invalid_token_err)
    else:
        return jsonify(invalid_token_err)

    # Read the Resume in Base64 Encoded string
    # Check if content-type= application/json has to be forced
    payload = json.loads(request.get_json(force=True))

    if 'ResumeAsBase64String' in payload and 'file_extension' in payload:
        b64str = payload['ResumeAsBase64String']
        file_extn = payload['file_extension']
    else:
        return jsonify(invalid_b64_doc)

    # Convert Resume from Base64 String to Document
    file_path = base64ToDocument(b64str, UPLOAD_FOLDER, file_extn)
    if file_path == 'fail':
        return jsonify(invalid_b64_doc)

    # Call the Parsing script and send the file path as param
    final_output = extractDataPoints(file_path)
    return jsonify(final_output)


@ app.route('/api/v1/cvparser/batch', methods=['POST'])
def batchResumeParsing():
    return 'Under development'


if __name__ == '__main__':
    app.run(debug=True)
