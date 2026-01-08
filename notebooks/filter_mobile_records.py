import gzip
import json

gz_file = "qa_Cell_Phones_and_Accessories.json.gz"
json_file = "mobile_qa.json"

mobile_keywords = ["phone", "iPhone", "Samsung", "Galaxy", "Pixel", "mobile"]

mobile_data = []

with gzip.open(gz_file, 'rt', encoding='utf-8', errors='ignore') as f_in:
    for line in f_in:
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)  # try parsing line as JSON
        except json.JSONDecodeError:
            # Some files wrap the JSON in a single dict
            try:
                record = eval(line)  # fallback: parse Python-style dict safely
                # convert keys to string if needed
                record = {str(k): v for k, v in record.items()}
            except Exception:
                continue  # skip malformed lines
        # Filter mobile-related QA
        question = record.get('question', '')
        answer = record.get('answer', '')
        if any(k.lower() in (question + answer).lower() for k in mobile_keywords):
            mobile_data.append(record)

# Save filtered mobile records
with open(json_file, 'w', encoding='utf-8') as f_out:
    json.dump(mobile_data, f_out, indent=2)

print(f"Saved {len(mobile_data)} mobile QA entries to {json_file}")
