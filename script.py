import requests
import xml.etree.ElementTree as ET
from collections import OrderedDict

# Download the XML file
url = "https://novalisvita.gr/export/export.xml"
response = requests.get(url)
with open("export.xml", "wb") as file:
    file.write(response.content)

# Parse the XML file
tree = ET.parse("export.xml")
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
        original_text = category.text
        modified_text = apply_replacements(original_text)
        
        if original_text == modified_text:
            unchanged_lines[original_text] = category.get('id')

# Save the modified XML file
tree.write("modified_export.xml", encoding="utf-8", xml_declaration=True)

# Print unique unchanged lines
if unchanged_lines:
    print("Unique lines that were not changed:")
    for text, id in unchanged_lines.items():
        print(f"ID: {id}, Text: {text}")
else:
    print("All lines were modified.")