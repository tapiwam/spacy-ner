# pip install pdfminer PyPDF4 pdfplumber pymupdf



# https://pymupdf.readthedocs.io/en/latest/

import fitz, re
from string import printable

import re
import pdfplumber


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
            # print(f">>> Removing line [{line}]")
            continue
        elif i<len(l2)-1 and is_valid_line(l2[i-1], clean_list) and is_valid_line(l2[i+1], clean_list): # Line before and after match pattern
            #print(f">>> Removing line [Inbetween]: [{line}]")
            continue
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
        # print(f'<<< Page {i} >>>')
        page = doc[i]
        text = page.get_text()

        p = strip_headers(text, scrub_list, clean_regex)
        
        pages.append(p)
        final_text += p + "\n"

    return pages, final_text

# Test main
# extract_pdf_text_pymupdf('/Users/tapiwamaruni/projects/spacy-ner/ner_youtube/data/hc/pdfs/200090122-echoes-vol_1.pdf')


# helper function for pdfplumber
def remove_tables(page):
    ts = {"vertical_strategy": "lines", "horizontal_strategy": "lines"}
    bboxes = [table.bbox for table in page.find_tables(table_settings=ts)]

    def not_within_bboxes(obj):
        # Check if the object is in any of the table's bbox.
        def obj_in_bbox(_bbox):
            # See https://github.com/jsvine/pdfplumber/blob/stable/pdfplumber/table.py#L404
            v_mid = (obj["top"] + obj["bottom"]) / 2
            h_mid = (obj["x0"] + obj["x1"]) / 2
            x0, top, x1, bottom = _bbox
            return (h_mid >= x0) and (h_mid < x1) and (v_mid >= top) and (v_mid < bottom)

        return not any(obj_in_bbox(__bbox) for __bbox in bboxes)

    return page.filter(not_within_bboxes)


# helper function for pdfplumber
def remove_margins(page, dpi=72, size=0.7):
    # strip 0.7 inches from top and bottom (page numbers, header text if any), A4 is 8.25 x 11.75
    # syntax is page.crop((x0, top, x1, bottom))
    w = float(page.width) / dpi
    h = float(page.height) / dpi
    return page.crop((0, (size) * dpi, w * dpi, (h - size) * dpi))


# function: input file, output text of annex 1
def extract_pdf_text_pdfplumber(filename, no_margins=True, no_blanks=False, no_tables=False, no_annex=True):
    
    print(f"Extracting text from {filename}")
    text = []
    with pdfplumber.open(filename) as pdf:
        for page in pdf.pages:
            if no_margins:
                page = remove_margins(page)

            if no_tables:
                page = remove_tables(page)

            page_text = page.extract_text().split("\n")
            text += page_text

    if no_annex:
        annex_lines = [re.match(r".*ANNEX\s+I.*", line) is not None for line in text]
        annex_index = [i for i, v in enumerate(annex_lines) if v]
        if len(annex_index) > 1:
            text = text[annex_index[0] : annex_index[1]]

    if no_blanks:
        text = [line for line in text if not line.isspace()]
        
    final_text = "\n".join(text)

    return final_text # text