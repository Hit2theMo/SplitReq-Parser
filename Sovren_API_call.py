# -*- coding: UTF-8 -*-
import base64
import json
# import logging
import ntpath
# from json.decoder import JSONDecodeError
from pathlib import Path
from time import strftime

import docx
from PyPDF2 import PdfFileReader
import requests
from ResumeScorer.scripts.custom_logger import logger
# from custom_logger import logger
# logger = logging.getLogger(__name__)
# logger("info", "Initialised Sovren API handler", __name__, 0)


def getLastModified(file_path):
    """Funtion to extract the last modified date of the file from its metadata
    Args:
        file_path (string): File Path
    Returns:
        string: Extracted Last modified date
    """
    file_extension = Path(file_path).suffix.split(".")[-1].upper()
    if file_extension == "DOCX":
        DOCX_OBJ = docx.Document(file_path)
        prop = DOCX_OBJ.core_properties
        return prop.modified.strftime("%Y-%m-%d")
    elif file_extension == "PDF":
        PDF_OBJ = PdfFileReader(open(file_path, 'rb'))
        doc_moddate = dict(PDF_OBJ.getDocumentInfo())["/ModDate"]
        mod_date = doc_moddate[2:6]+"-"+doc_moddate[6:8]+"-"+doc_moddate[8:10]
        return mod_date


def sendPostRequest(url, headers, payload):
    """Function to send a POST request to the Sovren API Parser Endpoint
    Args:
        url (string): The Sovren API endppoint URL
        headers (dict): The headers which has to be sent along with the API call
        payload (dict): API Call Payload
    Returns:
        string: Returns if the API call was a success or failure
        dict: The JSON response recieved from the API
    """
    logger("info", "Sending the request to API", __name__)
    try:
        response = requests.request("POST", url, data=json.dumps(
            payload), headers=headers, timeout=30)
        response.raise_for_status()
        # json_response = response.json()
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        logger("critical", f"HTTP {status_code} Error- {e}", __name__)
        try:
            json_response = response.json()
            logger("critical",
                   f"{json_response['Info']['Code']} -> {json_response['Info']['Message']}", __name__)
        except ValueError as jsonerr:
            logger("critical",
                   "JSON Decoding Failed- Did not receive a proper JSON Response from the API- " + str(jsonerr), __name__)
        return "failure", {}
    except requests.exceptions.Timeout as e:
        logger("critical", "Timed out waiting for a response"+str(e), __name__)
        return "failure", {}
    except requests.exceptions.ConnectionError as errc:
        logger("critical", "Connection Error, check your URL and internet connection:"+str(errc), __name__)
        return "failure", {}
    except requests.exceptions.TooManyRedirects as e:
        # Tell the user their URL was bad and try a different one
        logger("critical", "Wrong URL"+str(e), __name__)
        return "failure", {}
    except requests.exceptions.RequestException:
        logger("critical", "Some other error- ", __name__, 1)
        return "failure", {}
    logger("info", "Received response from API", __name__)
    # print("received response from API")
    try:
        json_response = response.json()
    except ValueError as e:
        logger("critical",
               f"JSON Decoding Failed- Did not receive a proper JSON Response from the API- {e}", __name__)
        return "failure", {}
    return "success", json_response


def extractParsedData(json_response, file_name, to_path):
    """Extract the JSON containing the resume extracted data and write to a new file
    Args:
        json_response (dict): JSON response received from sovren api
        file_name (string): file name of the resume
        to_path (string): Path where the JSON file will be stored
    Returns:
        string: sucess or failure message
    """
    # Saving response to json file- the next 4 lines are not required (only for testing)
    # json_string = json.dumps(json_response, indent=4)
    # store_json_at = Path(to_path, file_name+"_sovren_resp.json")
    # with open(store_json_at, "w", encoding='utf-8') as f:
    #     f.write(json_string)
    # with open(r"testing_dataset\sovren_api_json\Naman_Singhal.pdf_sovren_resp.json", encoding='utf-8') as fh:
    #     json_response = json.load(fh)
    # file_name = "Naman_Singhal.pdf"
    try:
        parsed_serialised_json_op = json_response["Value"]["ParsedDocument"]
    except KeyError:
        logger("critical",
               "Key Error- could not find the required key while extracting the Parsed Document JSON", __name__)
        return "failure"
    store_json_at = Path(to_path, file_name+".json")
    try:
        with open(store_json_at, "w", encoding='utf-8') as f:
            f.write(parsed_serialised_json_op)
    except FileNotFoundError:
        logger("critical",
               "FileNotFoundError - Could not write the JSON to the given path-", __name__)
        return "failure"
    except Exception:
        logger("critical", "Unknown error - Could not write the JSON to the given path-", __name__, 1)
        return "failure"

    logger("info", "Credits left-"+str(json_response["Value"]["CreditsRemaining"]), __name__)
    return "success"


def sovrenAPIHandler(file_path, to_path):
    """Master function to handle the Sovren API. The program flow is as follows-
        1. Get file name and file extenstion from file path and convert the file into base64 string
        2. Verify the integrity of the resume file- if error program will terminate
        3. Extract the last modified date from the file metadata
        4. Create the headers and payload to be used for calling the API
        5. Send a POST request to the correct API endpoint and handle all errors - if error program will Terminate
        6. Extract the required Parser JSON from the received API response JSON.
    Args:
        file_path (string): Path where the resume is stored
        to_path (string): Path where the JSON will be stored
    Returns:
        string: Returns if the API call was a success or failure
    """
    file_name = ntpath.basename(file_path)
    file_extension = Path(file_path).suffix.split(".")[-1].upper()
    # verifyFileIntegrity(file_extension)
    # open the file, encode the bytes to base64, then decode that to a UTF-8 string
    try:
        with open(file_path, 'rb') as f:
            base64str = base64.b64encode(f.read()).decode('UTF-8')
    except UnicodeDecodeError:
        logger("critical", "Unicode Decode error while converting file to Base64 string-", __name__, 1)
        # logger("critical", "Fatal Error- Terminating program!", __name__)
        return "failure"
    except Exception:
        logger("critical",
               "Some other error occured while converting file to Base64 string", __name__, 1)
        return "failure"
    url = "https://rest.resumeparsing.com/v9/parser/resume"
    # url = "http://ptsv2.com/t/8c7kr-1594224587/post"
    # url = "https://httpbin.org/status/200"
    current_date = strftime("%Y-%m-%d")
    file_mod_date = getLastModified(file_extension)
    if file_mod_date:
        revision_date = file_mod_date
    else:
        revision_date = current_date
    payload = {
        'DocumentAsBase64String': base64str,
        "RevisionDate": revision_date,
        "OutputHtml": False,
        "OutputRtf": False,
        "OutputPdf": True,
        "OutputCandidateImage": False,
        "Configuration": "Coverage.PatentsPublicationsAndSpeakingEvents = true; OutputFormat.CreateBullets = true; OutputFormat.DateOutputStyle = InferMissingDateParts; OutputFormat.ReformatPositionHistoryDescription = true",
    }
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'sovren-accountid': "aa",
        'sovren-servicekey': "aa",
    }
    status, json_response = sendPostRequest(url, headers, payload)
    if status == "failure":
        return "failure"
    msg = extractParsedData(json_response, file_name, to_path)
    return msg


if __name__ == "__main__":
    import time
    to_path = r'testing_dataset\sovren_api_json'
    # file_path = r'testing_dataset\ATS_templates\recent-graduate-v3.doc'
    file_path = r'testing_dataset\all_cvs\Ashish Khurana Resume New.pdf'
    file_path = r'testing_dataset\all_cvs\Apita Patra_Updated Resume.docx'
    file_path = r'testing_dataset\all_cvs\Dominion Funds_HASSAN HANNOUF_Regional Head.pdf'
    # file_path = r'testing_dataset\all_cvs\Ankit Singh CV.pdf'
    file_path = r"C:\Users\MohiT\Desktop\Sample_Resumes\Other\non_indian_cvs\DwightIT-QA-Analyst_layout.pdf"
    file_path = r"C:\Users\MohiT\Desktop\Sample_Resumes\Other\non_indian_cvs\Expat Group_Puneet Narulla_SVP.pdf"

    msg = sovrenAPIHandler(file_path, to_path)
    print("This program took -", time.perf_counter(), "seconds")
    print(msg)
