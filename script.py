import requests
import xml.etree.ElementTree as ET
from collections import OrderedDict

# Download the XML file
url = "https://novalisvita.gr/export/export.xml"
response = requests.get(url)
with open("export.xml", "wb") as file:
    file.write(response.content)

# Parse the XML file
parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
tree = ET.parse("export.xml", parser=parser)
root = tree.getroot()

# Define the replacements
replacements = {
    "Ιατρείο>Αναλώσιμα Ιατρείου>Γάντια": "TEST>Ιατρείο>Αναλώσιμα Ιατρείου>Γάντια",
    "Μέσα Ατομικής Προστασίας - Covid -19": "TEST>Μέσα Ατομικής Προστασίας - Covid -19"
}

# Function to apply replacements
def apply_replacements(text):
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

# OrderedDict to store unique unchanged lines
unchanged_lines = OrderedDict()

# Process product categories
for product_category in root.findall(".//product_category"):
    for category in product_category.findall("category"):
        # Get the text content, including CDATA
        original_text = ''.join(category.itertext())
        modified_text = apply_replacements(original_text)
        
        if original_text != modified_text:
            # Update the category text
            category.text = modified_text
            # Remove any existing children (like CDATA sections)
            category.clear()
        else:
            unchanged_lines[original_text] = category.get('id')

# Custom function to write XML and preserve CDATA
def write_xml_with_cdata(elem, file, encoding="us-ascii", xml_declaration=None, default_namespace=None,
                         method="xml", short_empty_elements=True):
    from xml.etree import ElementTree as ET
    from xml.dom import minidom
    
    rough_string = ET.tostring(elem, encoding, method=method)
    reparsed = minidom.parseString(rough_string)
    
    if xml_declaration:
        file.write(f'<?xml version="1.0" encoding="{encoding}"?>\n'.encode(encoding))
    
    reparsed.writexml(file, addindent="  ", newl="\n", encoding=encoding)

# Save the modified XML file
with open("modified_export.xml", "wb") as file:
    write_xml_with_cdata(root, file, encoding="utf-8", xml_declaration=True)

# Print unique unchanged lines
if unchanged_lines:
    print("Unique lines that were not changed:")
    for text, id in unchanged_lines.items():
        print(f"ID: {id}, Text: {text}")
else:
    print("All lines were modified.")