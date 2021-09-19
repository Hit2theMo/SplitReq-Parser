from docx_doc_to_text import wordToText
from pdf_to_text import PdfToText
# import os
import spacy
from spacy.matcher import Matcher
from pprint import pprint
import regex as re
from pathlib import Path
import logging
import logging.config


# logging.config.fileConfig('logging.conf')  # , disable_existing_loggers=False)
logger = logging.getLogger(__name__)

nlp = spacy.load("en_core_web_md")
matcher = Matcher(nlp.vocab)


def extractText(path, file_extension):
    hyperlinks = []
    # file_name, file_extension = os.path.splitext(path)
    path = Path(path)
    if file_extension.lower() in ("docx", "doc"):
        try:
            txt = wordToText(str(path))
        except Exception:
            logger.critical(
                "Error converting given Doc or Docx file into Text- {0}".format(path), exc_info=True)
            return '', []
    elif file_extension.lower() == 'pdf':
        try:
            result = PdfToText(path)
            txt = result[0]
            hyperlinks = result[1]
        except Exception:
            logger.critical(
                "Error converting given PDF file into Text- {0}".format(path), exc_info=True)
            return '', []
    else:
        return '', []

    return txt, hyperlinks


def cleanText(text):
    # Removing New Lines and New tabs
    text = text.replace('\n', ' ')
    text = text.replace('\t', ' ')
    # Removing Non UTF-8 Characters or Symbols
    text = bytes(text, 'utf-8').decode('utf-8', 'ignore')
    return text


def spacyProcessText(text):
    text_cleaned = cleanText(text)
    doc = nlp(text_cleaned)
    # tokens = [(token.text, token.pos_) for token in doc]
    # sentences = [sent for sent in doc.sents]
    # emails = [token.text for token in doc if token.like_email]
    # urls = [token.text for token in doc if token.like_url]
    # ents = [(e.text, e.label_) for e in doc.ents]
    # for ent in doc.ents:
    #     if ent.label_ in ['GPE', 'LOC']:
    #         print(ent.text, ent.start_char, ent.end_char, ent.label_)
    # print(ents)
    # print(emails)
    # print(urls)
    # print(tokens)
    # pprint(sentences)
    return doc

# ----------------------------------------------------------------------------------------------------
# Function to extract the Name of user from text


def extractName(spacy_doc):
    # First name and Last name are always Proper Nouns
    pattern1 = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    pattern2 = [{'POS': 'PROPN'}, {'POS': 'SPACE'}, {'POS': 'PROPN'}]
    matcher.add('NAME', [pattern1, pattern2])
    matches = matcher(spacy_doc)
    # Returning the first match of the above two patterns
    for match_id, start, end in matches:
        # print(start, end)
        span = spacy_doc[start:end]
        name = span.text.title()
        return name

# ----------------------------------------------------------------------------------------------------
# Function to extract the LinkedIn URL of user from text


def extractLinkedIn(text, spacy_doc, hyperlinks):
    if not text and not hyperlinks:
        return []
    linkedin = []
    if hyperlinks:
        for link in hyperlinks:
            if 'linkedin' in link:
                return [link]
    url = re.search(
        r"http(s)?:\/\/([\w]+\.)?linkedin\.com\/in\/[A-z0-9_-]+\/?", text)
    if url == None:
        for token in spacy_doc:
            if "linkedin" in token.text.lower() and '/' in token.text.lower():
                return [token.text]
            else:
                return []
    else:
        return url.group()

# ----------------------------------------------------------------------------------------------------
# Function to extract mobile numbers from text


def extractMobileNumbers(text):
    if not text:
        return []
    mobile_numbers = []
    phone = re.findall(re.compile(
        r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), text)
    # print(phone)
    if phone:
        for num in phone:
            number = ''.join(num)
            if len(number) > 10:
                mobile_numbers.append('+' + number)
            else:
                mobile_numbers.append(number)
    return mobile_numbers
# ----------------------------------------------------------------------------------------------------


def extractEmail(text, hyperlinks):
    if not text:
        return []
    emails = []
    # if hyperlinks:
    #     for link in hyperlinks:
    #         if '@' in link and '.com' in link:
    #             return link
    emails = re.findall(
        "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", text)
    if emails:
        emails = list(set([e.lower() for e in emails if e]))
    return emails

# ----------------------------------------------------------------------------------------------------


def extractLocation(spacy_doc):
    for ent in spacy_doc.ents:
        if ent.label_ in ['GPE', 'LOC']:
            return ent.text

# ----------------------------------------------------------------------------------------------------
#  MAIN FUNCTION Below- (to be called by Flask)
# ----------------------------------------------------------------------------------------------------


def extractDataPoints(path, file_extension):
    path = str(path)
    # print(path)
    # logger.info("Starting Data extraction from the resume- {0}".format(path))
    data_dict = {}
    try:
        text, hyperlinks = extractText(path, file_extension)
        if not text:
            raise Exception
    except Exception:
        logger.exception(
            "Error extracting text from the resume- {0}".format(path))
        return {}
    try:
        clean_text = cleanText(text)
    except Exception:
        logger.exception(
            "Error performing text cleanup on the resume- {0}".format(path))
        clean_text = ''
    try:
        spacy_doc = spacyProcessText(text)
    except Exception:
        logger.exception(
            "Error processing text using Spacy on the resume- {0}".format(path))
        spacy_doc = ''
    try:
        name = extractName(spacy_doc)
    except Exception:
        logger.exception(
            "Error extracting data point- 'Name' from the resume- {0}".format(path))
        name = ''
    try:
        linkedin = extractLinkedIn(clean_text, spacy_doc, hyperlinks)
    except Exception:
        logger.exception(
            "Error extracting data point- 'LinkedIn from the resume- {0}".format(path))
        linkedin = []
    try:
        mobile_numbers = extractMobileNumbers(clean_text)
    except Exception:
        logger.exception(
            "Error extracting data point- 'Mobile Number' from the resume- {0}".format(path))
        mobile_numbers = []
    try:
        emails = extractEmail(text, hyperlinks)
    except Exception:
        logger.exception(
            "Error extracting data point- 'Emails' from the resume- {0}".format(path))
        emails = []
    try:
        location = extractLocation(spacy_doc)
    except Exception:
        logger.exception(
            "Error extracting data point- 'Location' from the resume- {0}".format(path))
        location = ''

    data_dict["name"] = name
    data_dict["mobile_numbers"] = mobile_numbers
    data_dict["emails"] = emails
    data_dict["linkedin"] = linkedin
    data_dict["location"] = location

    return data_dict


# --------------------------------------------------------------------------------------
if __name__ == '__main__':

    # path = r'resumes\Other\non_indian_cvs\EY_Kitman Tsang_Cosec Mgr.docx'
    # path = r'resumes\best\Arindam_Presales.docx'
    path = r'resumes\sample_CVs\Resume_1.docx'
    path = r'resumes\Other\non_indian_cvs\DwightIT-QA-Analyst_layout.pdf'
    path = r'resumes\sample_CVs\Resume_2.pdf'
    # path = r'resumes\sample_CVs\Resume_2.docx'
    # path = r'resumes\sample_CVs\my_resume.pdf'
    # path = r'resumes\Resumes_latest\2MichaelFarros.doc'
    path = r'resumes\Resumes_latest\Lawrence Acosta.docx'
    path = r'resumes\Resumes_latest\Kevin_Resumev2.docx'
    # path = r'resumes\Resumes_latest\Derrick-Joyner (1).pdf'
    # path = r'resumes\Resumes_latest\Garstang-Resume-LinuxAdmin.pdf'     # Wrong name because space between name chars
    path = r'resumes\Resumes_latest\Friedlander_Resume.pdf'
    # path = r'resumes\Resumes_latest\Eric_Kao_Resume.pdf'
    # path = r'resumes\Resumes_latest\EllenJacobs.pdf'
    # path = r'resumes\Resumes_latest\'
    # path = r'resumes\Resumes_latest\Gary_Greenberg_resume_09_10.pdf'  # Mult mobile nums - Wrong Name identification
    path = str(path)
    print(path)
    data = extractDataPoints(path, 'pdf')
    # print(repr(data['name']))
    pprint(data)
