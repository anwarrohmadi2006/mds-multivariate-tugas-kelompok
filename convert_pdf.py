import markdown2
from xhtml2pdf import pisa
import sys

md_file = 'Laporan_Kunjungan_Industri_JalaTech.md'
pdf_file = 'Laporan_Kunjungan_Industri_JalaTech.pdf'

with open(md_file, 'r', encoding='utf-8') as f:
    md_text = f.read()

html_body = markdown2.markdown(md_text)

html_content = f"""
<html>
<head>
<style>
    @page {{
        size: A4 portrait;
        margin: 2cm;
    }}
    body {{
        font-family: "Times New Roman", Times, serif;
        font-size: 12pt;
        line-height: 1.5;
        text-align: justify;
    }}
    h1 {{ 
        font-size: 16pt; 
        text-align: center; 
        margin-bottom: 20px;
    }}
    h2 {{ 
        font-size: 14pt; 
        margin-top: 20px;
        margin-bottom: 10px;
    }}
    p {{
        margin-bottom: 10px;
    }}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""

with open(pdf_file, 'wb') as pdf_out:
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_out)

if pisa_status.err:
    sys.exit(1)
else:
    print('Success')
