import requests
from lxml import etree
from collections import OrderedDict

# Download the XML file
url = "https://novalisvita.gr/export/export.xml"
response = requests.get(url)
with open("export.xml", "wb") as file:
    file.write(response.content)

# Parse the XML file
parser = etree.XMLParser(remove_blank_text=True)
tree = etree.parse("export.xml", parser)
root = tree.getroot()

# Define the replacements
replacements = {
    "Ιατρείο>Αναλώσιμα Ιατρείου>Γάντια": "TEST>Ιατρείο>Αναλώσιμα Ιατρείου>Γάντια",
    "Μέσα Ατομικής Προστασίας - Covid -19": "TEST>Μέσα Ατομικής Προστασίας - Covid -19"
}

# Function to apply replacements
def apply_replacements(text):
    for old, new in replacements.items():
        if old in text:
            print(f"Replacing '{old}' with '{new}'")
            text = text.replace(old, new)
    return text

# OrderedDict to store unique unchanged lines
unchanged_lines = OrderedDict()

# Process product categories
for product_category in root.xpath("//product_category"):
    for category in product_category.xpath("category"):
        # Get the text content, including CDATA
        original_text = category.text if category.text else ""
        print(f"Original text: {original_text}")
        
        modified_text = apply_replacements(original_text)
        print(f"Modified text: {modified_text}")
        
        if original_text != modified_text:
            # Update the category text
            category.text = etree.CDATA(modified_text)
        else:
            unchanged_lines[original_text] = category.get('id')

# Save the modified XML file
tree.write("modified_export.xml", encoding="utf-8", xml_declaration=True, pretty_print=True)

# Print unique unchanged lines
if unchanged_lines:
    print("\nUnique lines that were not changed:")
    for text, id in unchanged_lines.items():
        print(f"ID: {id}, Text: {text}")
else:
    print("\nAll lines were modified.")