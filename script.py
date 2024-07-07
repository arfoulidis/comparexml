import os
import xml.etree.ElementTree as ET

# Set the path to the XML file
xml_file_path = "path/to/your/xml/file.xml"

# Define replacements
replacements = {
    "Ιατρείο>Αναλώσιμα Ιατρείου>Γάντια": "TEST>Ιατρείο>Αναλώσιμα Ιατρείου>Γάντια",
    "Μέσα Ατομικής Προστασίας - Covid -19": "TEST>Μέσα Ατομικής Προστασίας - Covid -19"
    # Add more replacements as needed
}

# Check if the XML file exists
if os.path.exists(xml_file_path):
    # Parse the XML data
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Initialize a list to store unreplaced categories
    unreplaced_categories = []

    # Iterate through the product categories
    for product in root.findall(".//product"):
        category_element = product.find(".//category/text()")
        if category_element is not None:
            category_name = category_element.strip()  # Remove leading/trailing whitespace
            if category_name in replacements:
                # Replace the category name with the corresponding replacement
                category_element.getparent().text = replacements[category_name]
            else:
                unreplaced_categories.append(f"<product_category>{category_name}</product_category>")

    # Print the unreplaced categories
    if unreplaced_categories:
        print("Unreplaced categories:")
        for category in unreplaced_categories:
            print(category)
    else:
        print("All categories were replaced successfully.")
else:
    print(f"The XML file '{xml_file_path}' does not exist.")