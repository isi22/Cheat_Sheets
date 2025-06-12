import json
import re
import unicodedata

def get_anchor_id(value):
    value = re.sub(r'[-\s]+', '-', value).strip()
    return value

def get_html_toc(ipynb_filepath):
    
    headers = []
    try:
        with open(ipynb_filepath, 'r', encoding='utf-8') as f:
            notebook_content = json.load(f)

        if 'cells' not in notebook_content:
            print(f"Error: '{ipynb_filepath}' does not appear to be a valid Jupyter notebook (missing 'cells' key).")
            return []

        for cell in notebook_content['cells']:
            if cell['cell_type'] == 'markdown':
                # 'source' can be a list of strings (lines) or a single string
                markdown_source = "".join(cell['source']) if isinstance(cell['source'], list) else cell['source']

                # Split the markdown source into lines
                lines = markdown_source.split('\n')

                for line in lines:
                    line = line.strip() # Remove leading/trailing whitespace

                    # Regular expression to find ATX style headings (e.g., # H1, ## H2)
                    # It captures the hash symbols and the text content
                    match = re.match(r'^(#+)\s*(.*)$', line)
                    if match:
                        level = len(match.group(1)) # Number of '#' characters determines the level
                        text = match.group(2).strip() # The text after the hashes
                        headers.append({'level': level, 'text': text})
                        
        html_toc = generate_html_toc(headers)

    except FileNotFoundError:
        print(f"Error: File not found at '{ipynb_filepath}'")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{ipynb_filepath}'. Is it a valid .ipynb file?")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return html_toc

def generate_html_toc(headers_list):

    html_output = []
    html_output.append('<div style="background-color: whitesmoke; padding: 10px; padding-left: 30px;">')
    html_output.append('  <h2>Table of Contents</h2>')
    html_output.append('  <hr>')

    # Keep track of the top-level (H1) counter
    h2_counter = 0

    for header in headers_list:
        level = header['level']
        text = header['text']

        if level > 1:
        
            # Create a URL-friendly ID for the anchor link
            anchor_id = get_anchor_id(text)
    
            # Determine styling based on header level
            style = ""
            prefix = ""
            
            if level == 2:
                h2_counter += 1
                # Reset sub-counters for each new H1 (though not strictly required by the example)
                style = "font-weight: bold; font-size: 1.1em;"
                prefix = f"{h2_counter}. "
                padding_left_value = 0 # No extra padding for H1 from base 30px
            else:
                # Adjust padding for sub-levels. The example uses 25px increment for H2, 50px for H3, etc.
                # Base padding for the container is 30px, so we add from there.
                # Level 3: 25px
                # Level 4: 50px
                # Level 5: 75px
                padding_left_value = (level - 2) * 25 # Each level deeper adds 25px padding
                
                style = f"padding-left: {padding_left_value}px;"
            
            # Add the HTML div for the current header
            html_output.append(f'  <div style="{style}"><a href="#{anchor_id}">{prefix}{text}</a></div>')

    html_output.append('  <hr>')
    html_output.append('</div>')

    return "\n".join(html_output)
