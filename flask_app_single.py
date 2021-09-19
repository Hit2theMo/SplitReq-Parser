# from datetime import datetime, date
import base64
import logging
import logging.config
# import json
import os
import pathlib
# import shutil
# import zipfile

import shortuuid
from celery import Celery
from flask import Flask, jsonify, request
from sentry_sdk import capture_message
from redis import Redis
# from batch_parsing import parseUnzippedResumes
from resume_parser import extractDataPoints

API_KEY = "ab8a7ff7-6659-4a44-b7d9-064612d825fa"
UPLOAD_PATH = "uploaded_files"
BATCH_UNZIP_PATH = "batch_parsing"

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logging.conf")
logging.config.fileConfig(log_file_path, disable_existing_loggers=False)

logger = logging.getLogger(__name__)
batch_logger = logging.getLogger("batch_parsing")

# Creating a file handler for the default flask app logger
# flask_file_handler = logging.FileHandler(os.path.join('logs', 'flask_error_logs.log'))
# flask_file_handler.setLevel(logging.WARNING)

# TIME_NOW = str(datetime.utcnow().date())
# date = TIME_NOW.split('-')
# batch_id = ''.join(date)
# print(TIME_NOW)

app = Flask(__name__)
# app.logger.addHandler(flask_file_handler)
redis_obj = Redis(host='localhost', port='6379')
simple_app = Celery('batch_parsing', broker='redis://localhost:6379/0',
                    backend='redis://localhost:6379/0')

username_err_msg = {
    "Error": "Invalid Account",
    "Message": "Please add your account id in the 'username' POST header",
}

invalid_token_err = {
    "Error": "Authentication Failed",
    "Message": "Please add a valid token in the 'api-token' POST header",
}

invalid_json_payload = {
    "Error": "Invalid JSON Payload",
    "Message": "Please send a valid JSON Payload in the body of your POST request",
}

invalid_b64_doc = {
    "Error": "Invalid Document",
    "Message": "Please send a valid Resume file in the JSON payload with Key- 'ResumeAsBase64String'",
}

unzip_err = {
    "Error": "Could not Unzip",
    "Message": "Please send a valid Zipped file in the JSON payload with Key- 'ZipAsBase64String'",
}

invalid_batch = {
    "Error": "Could not parse batch",
    "Message": "Please send zipped valid resumes, fatal error while batch parsing'",
}

unparsable_resume = {
    "Error": "Could not parse resume",
    "Message": "Please send a valid parsable resume in either DOC, DOCX or PDF format",
}


def generate_filename(batch, org_name=None):
    uuid = shortuuid.ShortUUID()
    if batch:
        return uuid.uuid()
    else:
        file_name = org_name.strip() + "_" + uuid.uuid()
        return file_name


def base64ToDocument(data, path, file_name, extn):
    file_path = pathlib.PurePath(path, file_name + "." + extn.lower())
    # try:
    with open(file_path, "wb") as fh:
        fh.write(base64.b64decode(data))
    return file_path
    # except Exception:
    #     return 'fail'
    # else:
    #     return file_path


def authenticate(headers, batch):
    global logger
    if batch:
        logger = batch_logger

    if "username" in headers:
        username = headers["username"]
    else:
        return jsonify(username_err_msg), ""
    if "api-token" in headers:
        api_token = headers["api-token"]
        if api_token == API_KEY:
            # print("Authenticated user '{0}' with key '{1}'".format(username, api_token))
            capture_message(
                "Authenticated user '{0}' with key '{1}'".format(username, api_token)
            )
            return "success", username
        else:
            # print("Authentication failed for user '{0}' with key '{1}'".format(username, api_token))
            capture_message(
                "Authentication failed for user '{0}', invalid key- '{1}'".format(
                    username, api_token
                )
            )
            return jsonify(invalid_token_err), username
    else:
        return jsonify(invalid_token_err), username


# =================================================================================================================================


@app.route("/api/v1/cvparser/single", methods=["POST"])
def parseResume():
    # capture_message("Recieved a post request")
    # Get headers
    headers = request.headers
    # Authenticate the POST request or return appt error messages
    try:
        status, username = authenticate(headers, batch=False)
    except Exception:
        logger.critical(
            "Error while authenticating a POST request at endpoint- '/api/v1/cvparser/single'\n",
            exc_info=True,
        )
        return jsonify(invalid_token_err)
    if status != "success":
        return status
    # ------------------------------------------------------------------------------------------------
    # Read the Resume in Base64 Encoded string
    # Check if content-type= application/json has to be forced
    try:
        payload = request.get_json(force=True)
    except Exception:
        logger.exception("Incorrect JSON payload, request sent by {0}".format(username))
        return jsonify(invalid_json_payload)

    if ("ResumeAsBase64String" in payload and "file_extension" in payload and "file_name" in payload):
        b64str = payload["ResumeAsBase64String"]
        file_extn = payload["file_extension"]
        org_file_name = payload["file_name"]
    else:
        return jsonify(invalid_json_payload)
    # ------------------------------------------------------------------------------------------------
    # Convert Resume from Base64 String to Document
    unique_file_name = generate_filename(False, org_file_name)
    try:
        file_path = base64ToDocument(b64str, UPLOAD_PATH, unique_file_name, file_extn)
    except Exception:
        logger.exception(
            "Invalid Base64 string- Error converting Resume from Base64 string to file, request sent by user- {0}".format(
                username
            )
        )
        return jsonify(invalid_b64_doc)
    # if file_path == 'fail':
    #     return jsonify(invalid_b64_doc)
    # ------------------------------------------------------------------------------------------------
    # Call the Parsing script and send the file path as param
    # print(file_path)
    try:
        final_output = extractDataPoints(file_path, file_extn)
        if not final_output:
            raise Exception
        capture_message(
            "Finished parsing resume- {0}, Extracted data points- \n {1}".format(
                file_path, final_output
            )
        )
    except Exception:
        logger.critical(
            "Error extracting data points from provided resume file- {0}, request sent by user- {1}".format(
                file_path, username
            ),
            exc_info=True,
        )
        return jsonify(unparsable_resume)
    # ------------------------------------------------------------------------------------------------
    # Delete the parsed resume
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
    except Exception:
        logger.exception(
            "Error deleting parsed resume file- {0}.{1}".format(file_path, file_extn)
        )
    return jsonify(final_output)


# =================================================================================================================================


if __name__ == "__main__":
    app.run(debug=True)
# celery --broker=redis://localhost:6379/0 flower --port=8080
# celery -A batch_parsing  worker --loglevel=INFO
