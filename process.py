import json
import os
import re

output_filename = 'bitwarden_export_processed'
WRITE_TXT = False
WRITE_JSON = False
WRITE_PDF = True

# get list of files in directory
files = os.listdir('.')
# filter bitwarden export files
files = sorted(list(filter(lambda f: re.match('bitwarden_export_[0-9]*.json', f), files)))

print(f'found these exported files: {files}')

input_file = files[-1]
print(f'selecting latest: {input_file}\n')

data = json.load(open(input_file))

# remove unnecessary fields
items = data['items']
for item in items:
    # unconditional remove on top level
    for i in ['revisionDate', 'creationDate', 'lastUsedDate', 'folderId', 'id', 'type', 'reprompt', 'favorite']:
        if i in item:
            del item[i]

    def remove_match(d, k):
        if isinstance(d, dict):
            for i in list(d.keys()):
                if k is None and d[i] is None or i == k:
                    del d[i]
                elif isinstance(d[i], (dict, list)):
                    remove_match(d[i], k)
        elif isinstance(d, list):
            for i in reversed(d):
                if k is None and i is None:
                    d.remove(i)
                elif isinstance(i, (dict, list)):
                    remove_match(i, k)

    # find keys and remove
    for i in ['type', 'lastUsedDate']:
        remove_match(item, i)

    # remove if null
    remove_match(item, None)

    # remove if empty
    def remove_empty(d):
        if isinstance(d, dict):
            for i in list(d.keys()):
                if len(d[i]) == 0:
                    del d[i]
                elif isinstance(d[i], (dict, list)):
                    remove_empty(d[i])
        elif isinstance(d, list):
            for i in reversed(d):
                if len(i) == 0:
                    d.remove(i)
                elif isinstance(i, (dict, list)):
                    remove_empty(i)

    remove_empty(item)
    remove_empty(item)

# replace generic key-value pairs with logic keys
for item in items:
    # change passwordHistory to a list
    if 'passwordHistory' in item:
        item['passwordHistory'] = [p['password'] for p in item['passwordHistory']]
    
    # process other fields
    if 'fields' in item:
        item['fields'] = {f['name']: f['value'] for f in item['fields']}

    # make a simple list of uris
    if 'login' in item and 'uris' in item['login']:
        item['login']['uris'] = [u['uri'] for u in item['login']['uris'] if 'uri' in u]

# save list of dicts to json file
if WRITE_JSON:
    with open(f'{output_filename}.json', 'w') as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

# create text lines for output
output = []
for item in items:
    line = rf"{item['name']}:  "
    for k, v in item.items():
        if k != 'name':
            line += rf'{k}: {v} ;'
    # print(line.encode('unicode_escape').decode())
    output.append(line)

# write to text file
if WRITE_TXT:
    with open(f'{output_filename}.txt', 'w') as f:
        for line in output:
            f.write(line.encode('unicode_escape').decode())
            f.write('\n')


# write to pdf
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

def create_pdf(strings, file_name="output.pdf"):
    # Set up the PDF canvas
    c = canvas.Canvas(file_name, pagesize=A4)
    width, height = A4
    
    # Define the margins and line height
    x_offset = 20
    y_offset_init = height - 25
    y_offset = y_offset_init  # Start near the top of the page
    usable_width = width - 2 * x_offset  # Calculate the usable width for the text
    
    # Set up the font
    font_name = "Courier"
    font_size = 7.2
    line_height = font_size  # Adjust line height as necessary
    c.setFont(font_name, font_size)

    # Page counter
    page_num = 1
    
    # Function to wrap text based on the usable width
    def wrap_text(text, font_name, font_size, usable_width):
        wrapped_lines = []
        words = text.split(' ')
        line = ""
        for word in words:
            # Measure the width of the current line plus the next word
            line_width = stringWidth(line + word + " ", font_name, font_size)
            if line_width <= usable_width:
                line += word + " "
            else:
                wrapped_lines.append(line.strip())
                line = word + " "
        if line:
            wrapped_lines.append(line.strip())
        return wrapped_lines
    
    # Function to add page number at the bottom of the page
    def add_page_number(page_num):
        page_number_text = f"Page {page_num}"
        # Calculate position for centered page number
        page_number_width = stringWidth(page_number_text, font_name, font_size)
        c.drawString((width - page_number_width) / 2, 15, page_number_text)  # Position at bottom (10 units above the bottom)
    
    # Process each string
    for string in strings:
        # Wrap the string into multiple lines to fit the page width
        wrapped_lines = wrap_text(string, font_name, font_size, usable_width)
        
        # Write each line to the PDF
        for line in wrapped_lines:
            if y_offset <= 20:  # Check if we need to start a new page
                add_page_number(page_num)
                page_num += 1
                c.showPage()  # End current page
                c.setFont(font_name, font_size)  # Reset the font after the new page
                y_offset = y_offset_init  # Reset the y position
            
            c.drawString(x_offset, y_offset, line)
            y_offset -= line_height  # Move down to the next line

    add_page_number(page_num)
    # Save the PDF
    c.save()

if WRITE_PDF:
    create_pdf(output, f"{output_filename}.pdf")

print('done')
