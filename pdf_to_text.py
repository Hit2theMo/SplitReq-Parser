import pdfplumber


def PdfToText(path):
    text = ''
    hyperlinks = []
    pdf = pdfplumber.open(path)
    for page in pdf.pages:
        # pprint(page.hyperlinks)
        for link in page.hyperlinks:
            hyperlinks.append(link['uri'])
        text = text + '\n' + page.extract_text()
    # print(hyperlinks)
    pdf.close()
    return text, hyperlinks


# --------------------------------------------------------------------------------------
if __name__ == '__main__':

    path = r'resumes\Other\non_indian_cvs\DwightIT-QA-Analyst_layout.pdf'
    path = r'resumes\sample_CVs\Resume_2.pdf'
    path = r'resumes\sample_CVs\my_resume.pdf'

    text, hyperlinks = PdfToText(path)
