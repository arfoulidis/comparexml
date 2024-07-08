import requests
from lxml import etree
import json
from collections import OrderedDict
import resend

# Function to read replacements from file
def read_replacements(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
        content = "{" + content.strip().rstrip(',') + "}"
        return json.loads(content)

# Function to read API key from file
def read_api_key(filename):
    with open(filename, 'r') as file:
        return file.read().strip()

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

# OrderedDict to store unique unchanged lines
unchanged_lines = OrderedDict()

# Process product categories
for product_category in root.xpath("//product_category"):
    for category in product_category.xpath("category"):
        original_text = category.text if category.text else ""
        modified_text = apply_replacements(original_text)
        
        if original_text != modified_text:
            category.text = etree.CDATA(modified_text)
        else:
            unchanged_lines[original_text] = category.get('id')

# Save the modified XML file
tree.write("modified_export.xml", encoding="utf-8", xml_declaration=True, pretty_print=True)

# Prepare email content
if unchanged_lines:
    email_content = "<h2>Unique lines that were not changed:</h2><ul>"
    for text, id in unchanged_lines.items():
        email_content += f"<li>ID: {id}, Text: '{text}'</li>"
    email_content += "</ul>"
else:
    email_content = "<p>All lines were modified.</p>"

# Read API key
api_key = read_api_key("resend_api_key.txt")

# Initialize Resend
resend.api_key = api_key

# Prepare email parameters
params = {
    "from": "resend@resendcom.a89.gr",
    "to": ["ar.foulidis@gmail.com"],
    "subject": "Unreplaced Categories in XML",
    "html": email_content,
    "headers": {"X-Entity-Ref-ID": "123456789"},
}

# Send email notification
try:
    email = resend.Emails.send(params)
    print("Email sent successfully. ID:", email["id"])
except Exception as e:
    print("Failed to send email:", str(e))

print("Script execution completed. Modified XML saved as 'modified_export.xml'.")