import pathlib
from resume_parser import extractDataPoints
import os
import shortuuid
from pprint import pprint
# from flask import jsonify
import json
import time


def generate_filename(org_name):
    uuid = shortuuid.ShortUUID()
    file_name = org_name.strip() + '_' + uuid.uuid()
    return file_name


def parseUnzippedResumes(path):
    file_names = os.listdir(path)
    # file_rename_dict = {}
    unparsed_resumes = []
    batch_output = {}
    final_batch_output = {}
    for fn in file_names:
        try:
            org_file_name, file_extn = fn.split('.')
            org_file_name = org_file_name.strip()
            org_file_path = pathlib.PurePath(path, fn)
            new_file_name = generate_filename(org_file_name).strip() + '.' + file_extn
            new_file_path = pathlib.PurePath(path, new_file_name)
            # file_rename_dict[fn] = new_file_name
            # Rename file to the new name
            os.rename(org_file_path, new_file_path)
            output_dict = extractDataPoints(str(new_file_path), file_extn)
            temp_dict = {}
            temp_dict["original_resume_name"] = fn
            temp_dict["extracted_data"] = output_dict
            batch_output[new_file_name] = temp_dict

        except Exception as e:
            print(e)
            unparsed_resumes.append(fn)
            continue
    final_batch_output["output"] = batch_output
    final_batch_output["unparsed_resumes"] = unparsed_resumes
    json_object = json.dumps(final_batch_output, indent=4)

    return json_object


if __name__ == '__main__':
    path = r'batch_parsing\\ipNLfea4wEqA34W8YnFzoe'
    # path = r'batch_parsing\B5gK5FDw7U8jbgmmq7TR2J'
    print(parseUnzippedResumes(path))
    print(time.perf_counter())
