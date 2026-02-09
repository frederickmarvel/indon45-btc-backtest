import json
import csv
import os

def convert_to_csv(filename, output_name):
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return

    with open(filename, 'r') as f:
        raw = json.load(f)
    
    data = raw.get('data', [])
    
    with open(output_name, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['price_date', 'price_value'])
        
        for row in data:
            writer.writerow([row['price_date'], row['price_value']])

    print(f"Done: {output_name} ({len(data)} rows)")

convert_to_csv('indonprice.json', 'indonprice.csv')
convert_to_csv('indonyield.json', 'indonyield.csv')