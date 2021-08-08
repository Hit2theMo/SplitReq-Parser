import textract


def wordToText(path):
    text = textract.process(path)
    return text.decode("utf-8")


# --------------------------------------------------------------------------------------
if __name__ == '__main__':
    path = r'resumes\Other\non_indian_cvs\EY_Kitman Tsang_Cosec Mgr.docx'
    path = r'resumes\best\Arindam_Presales.docx'
    path = r'resumes\sample_CVs\Resume_1.docx'
    path = r'resumes\Resumes_latest\2MichaelFarros.doc'
    path = r'resumes\Resumes_latest\Lawrence Acosta.docx'
    path = r'resumes\Resumes_latest\Kevin_Resumev2.docx'

    text = wordToText(path)
