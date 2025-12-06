import json
import csv
import re


def post_process():
    """Process contacts.json and save unique contacts to CSV."""
    # Read the JSON file
    with open("contacts.json", "r") as f:
        records = json.load(f)
    
    # Store unique phone numbers with their names
    unique_contacts = {}  # phone -> name mapping
    
    for record in records:
        # Each record is a JSON string, parse it
        try:
            # Remove markdown code block if present
            cleaned = record.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            contacts = json.loads(cleaned.strip())
            
            for contact in contacts:
                phone = contact.get("phone")
                name = contact.get("name")
                
                if phone:
                    # Strip +91 if present
                    phone = phone.replace("+91", "")
                    # Remove all spaces
                    phone = phone.replace(" ", "")
                    # Remove any other non-digit characters
                    phone = re.sub(r'\D', '', phone)
                    
                    # Only add if we haven't seen this number
                    if phone and phone not in unique_contacts:
                        unique_contacts[phone] = name if name else ""
                        
        except json.JSONDecodeError as e:
            print(f"Error parsing record: {e}")
            continue
    
    # Write to CSV
    with open("contacts.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Phone"])
        
        for phone, name in unique_contacts.items():
            writer.writerow([name, phone])
    
    print(f"Extracted {len(unique_contacts)} unique phone numbers to contacts.csv")
    return len(unique_contacts)


if __name__ == "__main__":
    post_process()
