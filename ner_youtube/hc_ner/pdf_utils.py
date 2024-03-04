# pip install pdfminer PyPDF4 pdfplumber pymupdf



# https://pymupdf.readthedocs.io/en/latest/

import fitz, re
from string import printable


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


def is_valid_line(line, clean_list, clean_regex=[], remove_digits=False):
    # Check using basic filter list
    status =  line.strip() in clean_list or line.isdigit()
    
    if status:
        # Check each regex
        for r in clean_regex:
            if len(re.findall(r, line)) > 0:
                status = False
                break
        
        # Check for digits if required
        if remove_digits:
            status = not line.isdigit()
        
    return status
    

# Strip head lines
def strip_headers(text, scrub_list=[], clean_regex=[]):
    # Use re to check if there is a header
    lines = text.split('\n')
    
    # Strip scrub list into new list
    clean_list = [s.strip() for s in scrub_list]
    # print (f"Final clean list: {clean_list}")
    
    # Clean lines
    l2 = []
    for i, line in enumerate(lines):
        
        # Cleanup hidden characters
        line = ''.join(char for char in line if char in printable)
        l2.append(line)
    
    final_list = []
    for i, line in enumerate(l2):
        
        # If line in scrub list then remove
        if is_valid_line(line, clean_list) or len(line) < 2:
            print(f">>> Removing line [{line}]")
        elif i<len(l2)-1 and is_valid_line(l2[i-1], clean_list) and is_valid_line(l2[i+1], clean_list): # Line before and after match pattern
            print(f">>> Removing line [Inbetween]: [{line}]")
        else:
            final_list.append(line.strip())
            # print(f"<<< Keeping line: [{line}]")
            
    return '\n'.join(final_list)

def extract_pdf_text_pymupdf(file_name, scrub_list=[], clean_regex=[]):
    # Create a document object
    doc = fitz.open(file_name)
    
    print(f'Document has {doc.page_count} pages')
    
    pages = []
    final_text = ""
    for i in range(doc.page_count):
        print(f'<<< Page {i} >>>')
        page = doc[i]
        text = page.get_text()
        # print(text)

        p = strip_headers(text, scrub_list, clean_regex)
        
        # links = page.get_links()
        # print(links)
        
        pages.append(p)
        final_text += p + "\n"

    return pages, final_text

# Test main
# extract_pdf_text_pymupdf('/Users/tapiwamaruni/projects/spacy-ner/ner_youtube/data/hc/pdfs/200090122-echoes-vol_1.pdf')