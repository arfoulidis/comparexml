import requests
from lxml import etree
import json

# Function to read replacements from file
def read_replacements(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
        # Remove any leading/trailing whitespace and add curly braces to make it a valid JSON
        content = "{" + content.strip().rstrip(',') + "}"
        return json.loads(content)

# Download the XML file
url = "https://novalisvita.gr/export/export.xml"
response = requests.get(url)
with open("export.xml", "wb") as file:
    file.write(response.content)

# Parse the XML file
parser = etree.XMLParser(remove_blank_text=True, recover=True, encoding='utf-8')
tree = etree.parse("export.xml", parser)
root = tree.getroot()

# Read replacements from file
replacements = read_replacements("replacements.txt")

# Function to apply replacements
def apply_replacements(text):
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)
    return text

# Process product categories
for product_category in root.xpath("//product_category"):
    for category in product_category.xpath("category"):
        original_text = category.text if category.text else ""
        modified_text = apply_replacements(original_text)
        
        if original_text != modified_text:
            category.text = etree.CDATA(modified_text)

# Save the modified XML file
tree.write("modified_export.xml", encoding="utf-8", xml_declaration=True, pretty_print=True)

print("Script execution completed. Modified XML saved as 'modified_export.xml'.")