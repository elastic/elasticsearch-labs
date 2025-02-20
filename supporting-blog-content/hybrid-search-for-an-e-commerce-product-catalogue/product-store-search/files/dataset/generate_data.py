import csv
import json

desired_fields = [
    "id",
    "brand",
    "name",
    "price",
    "price_sign",
    "currency",
    "image_link",
    "description",
    "rating",
    "category",
    "product_type",
    "tag_list",
]

input_file = "dataset_products.csv"  # Replace with your actual filename
output_file = "products.json"

# Open CSV file
with open(input_file, "r") as csvfile:
    # Read CSV data using DictReader
    csv_reader = csv.DictReader(csvfile)

    # Create empty list to store JSON data
    json_data = []

    # Loop through each row in CSV
    for row in csv_reader:
        # Create a new dictionary with desired fields only
        product_data = {field: row[field] for field in desired_fields}

        # Try converting price to float (optional)
        try:
            product_data["price"] = float(product_data["price"])
        except ValueError:
            pass  # Ignore conversion error

        # Convert tag_list string to list (optional)
        try:
            product_data["tag_list"] = eval(product_data["tag_list"])
        except SyntaxError:
            pass  # Ignore conversion error for invalid JSON strings

        # Append product data to JSON list
        json_data.append(product_data)

# Open JSON file for writing
with open(output_file, "w") as jsonfile:
    # Write JSON data to file with indentation
    json.dump(json_data, jsonfile, indent=4)

print(f"Converted CSV data to JSON and saved to {output_file}")
