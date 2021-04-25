import pdfminer
import os
import re

from docx import Document

import nltk
import pandas as pd
import textract
from pprint import pprint
# nltk.download('punkt', quiet=True)
# nltk.download('averaged_perceptron_tagger', quiet=True)

# ------------------------------------
# PDFs - PDFPlumber
# DOCX - Textract (Docx2txt)
# DOC - Textract (antiword)
# ------------------------------------


def file_To_Text(path, method):
    if method:
        text = textract.process(path, method=method)
    else:
        text = textract.process(path)
    return text.decode("utf-8")


# ----------------------------------------------------------------------------------------------------
# Function to extract email ids from both PDF and DOCX files


def extract_emails(txt):
    emails = re.findall(
        "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", txt)
    if emails == []:
        emails.append(None)
    return emails
# ----------------------------------------------------------------------------------------------------
# Function to extract mobile numbers from both PDF and DOCX files


def extract_mobile_number(text):
    phone = re.findall(re.compile(
        r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), text)
    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return '+' + number
        else:
            return number

# ----------------------------------------------------------------------------------------------------
# Function to extract the LinkedIn URL of user from both PDF and DOCX files


def extract_Linkedin(txt):
    url = re.search(
        r"http(s)?:\/\/([\w]+\.)?linkedin\.com\/in\/[A-z0-9_-]+\/?", txt)
    if url == None:
        return None
    else:
        return url.group()

# ----------------------------------------------------------------------------------------------------
# Function to extract the "INDIAN NAMES" from both PDF and DOCX files


def extract_name(document):

    # Reads Indian Names from the file, reduce all to lower case for easy comparision [Name lists]
    # indianNames = open(r"indian_names.txt", "r").read().lower()
    # indianNames = set(indianNames.split())
    otherNameHits = []
    nameHits = []
    name = None

    lines = [el.strip() for el in document.split("\n") if len(el)
             > 0]  # Splitting on the basis of newlines
    lines = [nltk.word_tokenize(el) for el in lines]
    lines = [nltk.pos_tag(el) for el in lines]

    sentences = nltk.sent_tokenize(document)
    # Split/Tokenize sentences into words (List of lists of strings)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    tokens = sentences
    # Tag the tokens - list of lists of tuples - each tuple is (<word>, <tag>)
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    dummy = []
    for el in tokens:
        dummy += el
    tokens = dummy
    # Try a regex chunk parser
    grammar = r'NAME: {<NN.*><NN.*><NN.*>*}'
    chunkParser = nltk.RegexpParser(grammar)
    all_chunked_tokens = []
    for tagged_tokens in lines:
        # Creates a parse tree
        if len(tagged_tokens) == 0:
            continue
        chunked_tokens = chunkParser.parse(tagged_tokens)
        all_chunked_tokens.append(chunked_tokens)
        for subtree in chunked_tokens.subtrees():
            if subtree.label() == 'NAME':
                for ind, leaf in enumerate(subtree.leaves()):
                    # if leaf[0].lower() in indianNames and 'NN' in leaf[1]:
                    if 'NN' in leaf[1]:

                        hit = " ".join([el[0]
                                        for el in subtree.leaves()[ind:ind + 3]])
                        if re.compile(r'[\d,:]').search(hit):
                            continue
                        nameHits.append(hit)
    if len(nameHits) > 0:
        nameHits = [re.sub(r'[^a-zA-Z \-]', '', el).strip() for el in nameHits]
        name = " ".join([el[0].upper() + el[1:].lower()
                         for el in nameHits[0].split() if len(el) > 0])
        otherNameHits = nameHits[1:]
    return name, otherNameHits

# ----------------------------------------------------------------------------------------------------
# Master function which combines all above methods to return a data frame


def extract_info(path):
    file_name, file_extension = os.path.splitext(path)
    if file_extension in (".docx", ".doc"):
        txt = file_To_Text(path)
    if file_extension == '.pdf':
        txt = file_To_Text(path, method='pdfminer')

    else:
        return "Invalid Format"

    linkedin = extract_Linkedin(txt)
    mobile = extract_mobile_number(txt)
    email = extract_emails(txt)
    name = extract_name(txt)[0]

    data = [{
        "File Name": file_name + file_extension,
        "Name": name,
            "Contact Number": str(mobile),
            "Email ID(s)": str(email),
            "Linkedin URL": str(linkedin),
            }]
    df = pd.DataFrame(data)
    return df


# ----------------------------------------------------------------------------------------------------
path = r'resumes\Other\non_indian_cvs\EY_Kitman Tsang_Cosec Mgr.docx'
# path = 'resumes\Other\non_indian_cvs\DwightIT-QA-Analyst_layout.pdf'
path = r'resumes\best\Arindam_Presales.docx'
path1 = r'resumes\sample_CVs\Resume_1.docx'
path = r'resumes\sample_CVs\Resume_1.pdf'
path = r'C:\Users\Mohit Khanwale\Desktop\SplitReq\SplitReq-Parser\resumes\sample_CVs\Resume_1.pdf'
path = r'resumes\Resumes_latest\2MichaelFarros.doc'
path = r'resumes\Resumes_latest\Lawrence Acosta.docx'
# path = 'C:\\2MichaelFarros.doc'
# text = file_To_Text(path)
# text = pdf_To_Text(path)
# text = text.replace('\n', '')
# print(text)
# print()
# # text1 = file_To_Text(path1, method='')
# # text1 = text1.replace('\n', ' ')

# # print(text1)
# text1 = pdfminer.high_level.extract_text(path)
# print(text1)
# df = extract_info(path)
# pprint(df)
text = textract.process(path)
print(text.decode("utf-8"))
