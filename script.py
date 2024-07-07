import os
import requests
import xml.etree.ElementTree as ET
import resend

# Set your Resend API key
resend.api_key = "re_KBfh7Xe6_CYET3ex5CRxjyPgB9tbqGKHj"

# Define replacements
replacements = {
    "Ιατρείο>Αναλώσιμα Ιατρείου>Γάντια": "TEST>Ιατρείο>Αναλώσιμα Ιατρείου>Γάντια",
    "Μέσα Ατομικής Προστασίας - Covid -19": "TEST>Μέσα Ατομικής Προστασίας - Covid -19"
    # Add more replacements as needed
}

# Download the XML file from the provided URL
url = "https://novalisvita.gr/export/export.xml"
response = requests.get(url)
xml_data = response.content

# Parse the XML data
root = ET.fromstring(xml_data)

# Initialize a list to store unreplaced categories
unreplaced_categories = []

# Iterate through the product categories
for product in root.findall(".//product_category"):
    category = product.text
    if category in replacements:
        product.text = replacements[category]
    else:
        unreplaced_categories.append(category)

# Check if any categories were not replaced
if unreplaced_categories:
    # Prepare email content
    email_content = "<strong>These categories have not been replaced:</strong> <br> <p>"
    email_content += "<br>".join(unreplaced_categories)
    email_content += "</p>"

    # Prepare email parameters
    params = {
        "from": "resend@a89.gr",
        "to": ["ar.foulidis@gmail.com"],
        "subject": "Unreplaced Categories in XML",
        "html": email_content,
        "headers": {"X-Entity-Ref-ID": "123456789"},
    }

    # Send email notification
    email = resend.Emails.send(params)
    print(email)
else:
    print("All categories were replaced successfully.")