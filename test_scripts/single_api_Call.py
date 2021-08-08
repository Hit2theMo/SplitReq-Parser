import requests
import json
import base64
import os
import time
from pprint import pprint

# path = r'resumes\Other\non_indian_cvs\EY_Kitman Tsang_Cosec Mgr.docx'
# path = r'resumes\best\Arindam_Presales.docx'
path = r"resumes\sample_CVs\Resume_1.docx"
# path = r"resumes\Other\non_indian_cvs\DwightIT-QA-Analyst_layout.pdf"
# path = r'resumes\sample_CVs\Resume_2.pdf'
# path = r'resumes\sample_CVs\Resume_2.docx'
# path = r"resumes\sample_CVs\my_resume.pdf"
# path = r'resumes\Resumes_latest\2MichaelFarros.doc'
# path = r'resumes\Resumes_latest\Lawrence Acosta.docx'
# path = r"resumes\Resumes_latest\Kevin_Resumev2.docx"
# path = r'resumes\Resumes_latest\Derrick-Joyner (1).pdf'
# path = r'resumes\Resumes_latest\Garstang-Resume-LinuxAdmin.pdf'     # Wrong name because space between name chars
# path = r"resumes\Resumes_latest\Friedlander_Resume.pdf"
# path = r"resumes\Resumes_latest\Eric_Kao_Resume.pdf"
# path = r'resumes\Resumes_latest\EllenJacobs.pdf'
# path = r'resumes\Resumes_latest\'
# Mult mobile nums - Wrong Name identification
# path = r"resumes\Resumes_latest\Gary_Greenberg_resume_09_10.pdf"
# path = r'uploaded_files\zipped_resume.zip'
path = r"resumes\sample_CVs\my_resume.pdf"
path = r"C:\Users\Mohit Khanwale\Downloads\Eric_Sundby_Resume_eSolytics_Alterxy_Oracle_ETL_Developer.docx"
# path = r"uploaded_files\BenDean.pdf"

# file_name, file_extension = os.path.splitext(path)
file_name, file_extension = os.path.basename(path).split(".")

print("file_name-", file_name)
print("file_extension-", file_extension)
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


# payload = {
#     "ResumeAsBase64String": base64str,
#     "file_name": file_name,
#     "file_extension": file_extension
# }

payload = {
    'ResumeAsBase64String': base64str,
    'file_name': file_name,
    'file_extension': file_extension
}

headers = {"username": "markabbot", "api-token": "ab8a7ff7-6659-4a44-b7d9-064612d825fa"}

# print(file_extension, file_name)
# print(base64str)

# http://149.28.197.77/api/v1/cvparser/single
res = requests.post(
    "http://149.28.197.77/api/v1/cvparser/single",
    json=payload,
    headers=headers,
)
print("response-", res)
# print(res.text)
# print(res.json())
print(time.perf_counter())
pprint(json.loads(res.text))

['/mnt/root/Enriched/Common/Global/Valign/Commercial/Canada/roster_member_territory__aln/2016/roster_member_territory__aln.csv',
 '/mnt/root/Enriched/Common/Global/Valign/Medical/Canada/roster_member_territory__aln/2017/roster_member_territory__aln.csv',
 '/mnt/root/Enriched/Common/Global/Valign/Common/Unknown/NA/roster_member_territory__aln/2017/roster_member_territory__aln.csv',
 '/mnt/root/Enriched/Common/Global/Valign/Medical/Canada/roster_member_territory__aln/2016/roster_member_territory__aln.csv',
 '/mnt/root/Enriched/Common/Global/Valign/Commercial/Unknown/NA/roster_member_territory__aln/2015/roster_member_territory__aln.csv',
 '/mnt/root/Enriched/Common/Global/Valign/Medical/Canada/roster_member_territory__aln/2021/roster_member_territory__aln.csv',
 '/mnt/root/Enriched/Common/Global/Valign/Commercial/Canada/roster_member_territory__aln/2019/roster_member_territory__aln.csv',
 '/mnt/root/Enriched/Common/Global/Valign/Medical/Unknown/NA/roster_member_territory__aln/2016/roster_member_territory__aln.csv',
 '/mnt/root/Enriched/Common/Global/Valign/Common/Unknown/NA/roster_member_territory__aln/2021/roster_member_territory__aln.csv',
 '/mnt/root/Enriched/Common/Global/Valign/Commercial/United States/roster_member_territory__aln/2021/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Commercial/Canada/roster_member_territory__aln/2017/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Medical/Unknown/NA/roster_member_territory__aln/2019/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Medical/Unknown/NA/roster_member_territory__aln/2017/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Commercial/Unknown/NA/roster_member_territory__aln/2017/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Medical/Unknown/NA/roster_member_territory__aln/2020/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Medical/United States/roster_member_territory__aln/2015/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Medical/Canada/roster_member_territory__aln/2020/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Commercial/United States/roster_member_territory__aln/2016/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Medical/United States/roster_member_territory__aln/2017/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Common/United States/roster_member_territory__aln/2020/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Medical/United States/roster_member_territory__aln/2018/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Commercial/Canada/roster_member_territory__aln/2020/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Medical/Unknown/NA/roster_member_territory__aln/2021/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Common/Unknown/NA/roster_member_territory__aln/2019/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Medical/Canada/roster_member_territory__aln/2015/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Medical/United States/roster_member_territory__aln/2019/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Commercial/United States/roster_member_territory__aln/2018/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Commercial/Unknown/NA/roster_member_territory__aln/2016/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Commercial/United States/roster_member_territory__aln/2015/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Common/Canada/roster_member_territory__aln/2020/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Commercial/Unknown/NA/roster_member_territory__aln/2018/roster_member_territory__aln.csv',
    '/mnt/root/Enriched/Common/Global/Valign/Common/Canada/roster_member_territory__aln/2019/roster_member_territory__aln.csv',
    '/mnt/root/Enriched/Common/Global/Valign/Common/United States/roster_member_territory__aln/2018/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Commercial/United States/roster_member_territory__aln/2017/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Common/Unknown/NA/roster_member_territory__aln/2015/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Commercial/Unknown/NA/roster_member_territory__aln/2021/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Medical/United States/roster_member_territory__aln/2021/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Common/Canada/roster_member_territory__aln/2015/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Common/Canada/roster_member_territory__aln/2017/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Common/United States/roster_member_territory__aln/2015/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Medical/Unknown/NA/roster_member_territory__aln/2018/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Common/Unknown/NA/roster_member_territory__aln/2020/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Common/Canada/roster_member_territory__aln/2016/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Common/United States/roster_member_territory__aln/2017/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Commercial/United States/roster_member_territory__aln/2019/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Common/Canada/roster_member_territory__aln/2021/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Common/Unknown/NA/roster_member_territory__aln/2018/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Medical/Canada/roster_member_territory__aln/2018/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Commercial/Unknown/NA/roster_member_territory__aln/2020/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Commercial/Unknown/NA/roster_member_territory__aln/2019/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Commercial/Canada/roster_member_territory__aln/2015/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Common/United States/roster_member_territory__aln/2019/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Medical/Unknown/NA/roster_member_territory__aln/2015/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Medical/United States/roster_member_territory__aln/2016/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Medical/United States/roster_member_territory__aln/2020/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Commercial/Canada/roster_member_territory__aln/2021/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Common/United States/roster_member_territory__aln/2021/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Commercial/United States/roster_member_territory__aln/2020/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Commercial/Canada/roster_member_territory__aln/2018/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Common/Unknown/NA/roster_member_territory__aln/2016/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Medical/Canada/roster_member_territory__aln/2019/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Common/United States/roster_member_territory__aln/2016/roster_member_territory__aln.csv', '/mnt/root/Enriched/Common/Global/Valign/Common/Canada/roster_member_territory__aln/2018/roster_member_territory__aln.csv']
