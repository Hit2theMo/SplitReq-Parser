# from datetime import datetime, date
import base64
import logging
import logging.config
# import json
import os
import pathlib
import shutil
import zipfile

import shortuuid
from celery import Celery
from flask import Flask, jsonify, request
from sentry_sdk import capture_message
from redis import Redis
# from batch_parsing import parseUnzippedResumes
# from resume_parser import extractDataPoints

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
celery_app = Celery('batch_parsing', broker='redis://localhost:6379/0',
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

task_status_pending = {
    "Message": "Status of the task is Pending, please wait and check again later",
}


def generate_filename(batch, org_name=None):
    uuid = shortuuid.ShortUUID()
    if batch:
        return uuid.uuid()
    else:
        file_name = org_name.strip() + "_" + uuid.uuid()
        return file_name


def unzipFile(base_unzip_path, uploaded_zip_path, zip_name):
    unzip_path = pathlib.PurePath(base_unzip_path, zip_name)
    # Create Folder for Files to be unzipped
    pathlib.Path(unzip_path).mkdir(parents=False, exist_ok=False)

    with zipfile.ZipFile(uploaded_zip_path, "r") as zip_ref:
        zip_ref.extractall(unzip_path)
    return unzip_path


def base64ToDocument(data, path, file_name, extn):
    file_path = pathlib.PurePath(path, file_name + "." + extn.lower())
    with open(file_path, "wb") as fh:
        fh.write(base64.b64decode(data))
    return file_path


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


def deleteZipUnzipFiles(zip_file_path, unzip_path):
    try:
        # Remove Uploaded zip file
        if os.path.isfile(zip_file_path):
            # print(zip_file_path)
            os.remove(zip_file_path)
        # remove unzipped files and folders
        # print(unzip_path)
        shutil.rmtree(unzip_path)
    except Exception:
        logger.exception(
            "Error deleting parsed resume file- {0}.{1}".format(zip_file_path, "zip")
        )

# =================================================================================================================================


@app.route("/api/v1/cvparser/batch", methods=["POST"])
def batchResumeParsing():
    headers = request.headers
    try:
        status, username = authenticate(headers, batch=True)
    except Exception:
        batch_logger.critical(
            "Error while authenticating a POST request at endpoint- '/api/v1/cvparser/batch'\n",
            exc_info=True,
        )
        # Add a separate error while authentication err msg if needed below
        return jsonify(invalid_token_err)
    if status != "success":
        return status
    # ------------------------------------------------------------------------------------------------
    try:
        payload = request.get_json(force=True)
    except Exception:
        batch_logger.exception("Incorrect JSON payload sent by {0}".format(username))
        return jsonify(invalid_json_payload)
    if "ZipAsBase64String" in payload:
        b64str = payload["ZipAsBase64String"]
    else:
        return jsonify(invalid_json_payload)
    # ------------------------------------------------------------------------------------------------
    unique_file_name = generate_filename(batch=True)
    try:
        zip_file_path = base64ToDocument(b64str, UPLOAD_PATH, unique_file_name, "zip")
    except Exception:
        batch_logger.exception(
            "Invalid Base64 string- Error converting Base64 string into a zip file, request sent by user- {0}".format(
                username
            )
        )
        return jsonify(invalid_b64_doc)
    # ------------------------------------------------------------------------------------------------
    try:
        unzip_path = unzipFile(BATCH_UNZIP_PATH, zip_file_path, unique_file_name)
    except Exception:
        batch_logger.exception(
            "Error un-zipping given zip file-{0}, request sent by user- {1}".format(
                zip_file_path, username
            )
        )
        return jsonify(unzip_err)
    r = celery_app.send_task('batch_parsing.parseUnzippedResumes',
                             kwargs={'path': str(unzip_path)})  # countdown=10
    app.logger.info(r.backend)
    redis_obj.set(f"zip_path_{r.id}", str(zip_file_path))
    redis_obj.set(f"unzip_path_{r.id}", str(unzip_path))
    task_id_result = {
        "Taskid": r.id,
        "Message": "Task has been submitted and will start soon",
    }
    return jsonify(task_id_result)


@app.route('/api/v1/cvparser/batch/task_result/<task_id>')
def get_status(task_id):
    try:
        celery_res = celery_app.AsyncResult(task_id, app=celery_app)
        result = celery_res.result
        redis_keys = [f'zip_path_{task_id}', f'unzip_path_{task_id}']
        zip_file_path = redis_obj.get(redis_keys[0])
        unzip_path = redis_obj.get(redis_keys[1])
        # print(zip_file_path, unzip_path, redis_keys)
        # print("Invoking Method ")
        if str(celery_res.state) == 'SUCCESS':
            deleteZipUnzipFiles(zip_file_path, unzip_path)
            redis_obj.delete(*redis_keys)
            # add logic to delete files after X amount after task completion (if needed)
            celery_res.forget()
            return jsonify(result)

        elif str(celery_res.state) == 'PENDING':
            return jsonify(task_status_pending)

        elif str(celery_res.state) == 'FAILURE':
            task_status_failed = {
                "Error": str(result),  # str(celery_res.traceback)
                "Message": "Status of the task is Failed, please check the error and try again",
            }
            deleteZipUnzipFiles(zip_file_path, unzip_path)
            redis_obj.delete(*redis_keys)
            celery_res.forget()
            return jsonify(task_status_failed)

        else:
            task_status_failed = {
                "Message": f"Something went wrong, status of the task is {celery_res.state}, please try again",
            }
    except Exception:
        batch_logger.critical(
            "Unexpected error while fetching task status from Celery, please check logs",
            exc_info=True,
        )
        return jsonify(invalid_batch)


if __name__ == "__main__":
    app.run(debug=True)
# celery --broker=redis://localhost:6379/0 flower --port=8080
# celery -A batch_parsing  worker --loglevel=INFO
# redis-server
