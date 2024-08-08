import requests
from lxml import etree
import json
from collections import OrderedDict
import resend
import os

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

# Read replacements from the specified location
replacements_file = "/home/pharmacydev/webapps/novalisvitaxml/replacements.txt"
replacements = read_replacements(replacements_file)

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
    replacements_made = False
    categories_to_remove = []
    
    for category in product_category.xpath("category"):
        original_text = category.text if category.text else ""
        modified_text = apply_replacements(original_text)
        
        if original_text != modified_text:
            category.text = etree.CDATA(modified_text)
            replacements_made = True
        else:
            unchanged_lines[original_text] = category.get('id')
            categories_to_remove.append(category)
    
    if not replacements_made:
        # Remove all categories if no replacements were made
        for category in product_category:
            product_category.remove(category)
    else:
        # Remove only unchanged categories
        for category in categories_to_remove:
            product_category.remove(category)

# Save the modified XML file
tree.write("modified_export.xml", encoding="utf-8", xml_declaration=True, pretty_print=True)

# Send email only if there are unchanged lines
if unchanged_lines:
    # Prepare email content
    email_content = "<strong>Κατηγορίες που δεν έχουν καταχωρηθεί στο αρχείο replacements:</strong><ul>"
    for text, id in unchanged_lines.items():
        email_content += f"<li>ID: {id}, Text: '{text}'</li>"
    email_content += "</ul>"

    # Read API key
    api_key = read_api_key("resend_api_key.txt")

    # Initialize Resend
    resend.api_key = api_key

    # Prepare email parameters
    params = {
        "from": "resend@send2.resendcom.a89.gr",
        "to": ["ar.foulidis@gmail.com"],
        "subject": "Κατηγορίες XML novalisvita",
        "html": email_content,
    }

    # Send email notification
    try:
        email = resend.Emails.send(params)
        print("Email sent successfully. ID:", email["id"])
    except Exception as e:
        print("Failed to send email:", str(e))
else:
    print("All categories were replaced. No email sent.")

print("Script execution completed. Modified XML saved as 'modified_export.xml'.")