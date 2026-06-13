import os
import re

try:
    from docx import Document
    from docx.shared import Inches, Pt
except ImportError:
    os.system("pip install python-docx")
    from docx import Document
    from docx.shared import Inches, Pt

def convert():
    doc = Document()
    
    with open("penjelasan_analisis_udang.md", "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    table_data = []
    in_table = False
    
    for line in lines:
        line = line.strip()
        if not line or line == '<br>' or line == '---':
            continue
            
        if line.startswith('|'):
            in_table = True
            if ':---' in line:
                continue
            
            parts = line.split('|')
            if len(parts) > 1 and not parts[0].strip():
                parts = parts[1:]
            if len(parts) > 0 and not parts[-1].strip():
                parts = parts[:-1]
                
            row = [cell.strip() for cell in parts]
            if row:
                table_data.append(row)
            continue
            
        if in_table and not line.startswith('|'):
            if table_data:
                table = doc.add_table(rows=len(table_data), cols=len(table_data[0]))
                table.style = 'Table Grid'
                for i, row in enumerate(table_data):
                    for j, cell_text in enumerate(row):
                        is_bold = False
                        if cell_text.startswith('**') and cell_text.endswith('**'):
                            is_bold = True
                            cell_text = cell_text[2:-2]
                        cell_text = cell_text.replace('**', '').replace('*', '')
                        
                        p = table.cell(i, j).paragraphs[0]
                        run = p.add_run(cell_text)
                        if i == 0 or is_bold:
                            run.bold = True
                        run.font.size = Pt(9)
                table_data = []
            in_table = False
        
        if line.startswith('# '):
            doc.add_heading(line[2:].replace('**',''), level=1)
        elif line.startswith('## '):
            doc.add_heading(line[3:].replace('**',''), level=2)
        elif line.startswith('### '):
            doc.add_heading(line[4:].replace('**',''), level=3)
        elif line.startswith('![') and '](' in line:
            match = re.search(r'!\[.*?\]\((.*?)\)', line)
            if match:
                img_path = match.group(1).replace('file:///', '').replace('%20', ' ')
                try:
                    doc.add_picture(img_path, width=Inches(6.0))
                except Exception as e:
                    doc.add_paragraph(f"[Gagal meload gambar: {img_path}]")
        else:
            p = doc.add_paragraph()
            if line.startswith('**'):
                p.add_run(line.replace('**', '')).bold = True
            else:
                p.add_run(line.replace('**', '').replace('*', ''))
                
    if in_table and table_data:
        table = doc.add_table(rows=len(table_data), cols=len(table_data[0]))
        table.style = 'Table Grid'
        for i, row in enumerate(table_data):
            for j, cell_text in enumerate(row):
                cell_text = cell_text.replace('**', '')
                p = table.cell(i, j).paragraphs[0]
                run = p.add_run(cell_text)
                if i == 0:
                    run.bold = True
                run.font.size = Pt(9)
                
    doc.save("Laporan_Analisis_Udang_MDS_V11.docx")

if __name__ == "__main__":
    convert()
