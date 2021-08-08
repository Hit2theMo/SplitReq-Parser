import pathlib
from resume_parser import extractDataPoints
import os
import shortuuid
from pprint import pprint
import json
import time
import logging
import base64
from zipfile import ZipFile
from sentry_sdk import capture_message

# logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

# logger = logging.getLogger('batch_parsing')


def generate_filename(org_name):
    uuid = shortuuid.ShortUUID()
    file_name = org_name.strip() + "_" + uuid.uuid()
    return file_name


def parseUnzippedResumes(path):
    capture_message("Starting the Batch Parsing of {0}".format(path))
    file_names = os.listdir(path)
    # file_rename_dict = {}
    unparsed_resumes = []
    batch_output = {}
    final_batch_output = {}
    for fn in file_names:
        try:
            org_file_name, file_extn = fn.split(".")
            org_file_name = org_file_name.strip()
            org_file_path = pathlib.PurePath(path, fn)
            new_file_name = generate_filename(org_file_name).strip() + "." + file_extn
            new_file_path = pathlib.PurePath(path, new_file_name)
            # file_rename_dict[fn] = new_file_name
            # Rename file to the new name
            os.rename(org_file_path, new_file_path)
            output_dict = extractDataPoints(str(new_file_path), file_extn)
            if not output_dict:
                raise Exception
            temp_dict = {}
            temp_dict["original_resume_name"] = fn
            temp_dict["extracted_data"] = output_dict
            batch_output[new_file_name] = temp_dict

        except Exception as e:
            logger.exception(
                "Error in batch parser while parsing resume- {0}".format(fn)
            )
            if new_file_path:
                unparsed_resumes.append(str(new_file_path))
            continue

    zip_path = pathlib.PurePath(path, "unparsed_resumes.zip")
    # Zipping unparsed resumes
    base64str = ""
    if unparsed_resumes:
        with ZipFile(zip_path, "w") as zip:
            for fn in unparsed_resumes:
                zip.write(fn)
        # Converting above Zip into Base64
        try:
            with open(zip_path, "rb") as f:
                base64str = base64.b64encode(f.read()).decode("UTF-8")
        except Exception:
            logger.critical(
                "Error converting unparsed resume Zip file to Base64 string", exc_info=True
            )
            base64str = ""

    final_batch_output["output"] = batch_output
    final_batch_output["unparsed_resumes"] = unparsed_resumes
    final_batch_output["unparsed_resume_zip_as_base64"] = base64str
    json_object = json.dumps(final_batch_output, indent=4)
    capture_message(
        "Finished processing batch file- {0}, JSON Result-{1}".format(path, json_object)
    )
    return json_object


if __name__ == "__main__":
    path = r"batch_parsing\ipNLfea4wEqA34W8YnFzoe"
    # path = r'batch_parsing\B5gK5FDw7U8jbgmmq7TR2J'
    print(json.loads(parseUnzippedResumes(path)))
    print(time.perf_counter())
