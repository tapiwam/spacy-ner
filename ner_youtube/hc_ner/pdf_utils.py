# pip install pdfminer PyPDF4 pdfplumber pymupdf


# https://pymupdf.readthedocs.io/en/latest/

import fitz, re

# Strip head lines
def strip_headers(text):
    # Use re to check if there is a header
    lines = text.split('\n')
    
    
    for i, line in enumerate(lines):
        
        tokens = line.split()
        
        # If line has just 1 token then remove
        if len(tokens) < 2:
            lines.pop(i)
            continue
        
        # Check pattern
        PATTERN = r'([A-Z]( )*)+'
        # If line matches pattern print
        if re.findall(PATTERN, line):
            print(line)
            

    # return '\n'.join(lines)

def extract_pdf_text_pymupdf(file_name):
    # Create a document object
    doc = fitz.open(file_name)
    
    print(f'Document has {doc.page_count} pages')
    
    for i in range(doc.page_count):
        page = doc[i]
        text = page.get_text()
        # print(text)

        strip_headers(text)
        
        # links = page.get_links()
        # print(links)

# Test main
extract_pdf_text_pymupdf('/Users/tapiwamaruni/projects/spacy-ner/ner_youtube/data/hc/pdfs/200090122-echoes-vol_1.pdf')