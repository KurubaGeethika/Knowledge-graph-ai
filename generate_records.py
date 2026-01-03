import json
from datetime import datetime, timedelta

# Rotation lists
themes = ["Hardware", "Security", "AI", "Performance", "Health"]
topics = ["Battery", "Privacy", "Apple Silicon", "Thermal", "Charging"]
regions = ["United States", "India", "EU", "UK", "Canada"]
models = ["ChatGPT", "Gemini", "Copilot"]

# Base timestamp
base_time = datetime(2024, 8, 1, 9, 0, 0)

records = []

for i in range(1, 1001):
    record = {
        "run_id": f"r{i:04}",  # padded to 4 digits for clarity
        "created_at": (base_time + timedelta(minutes=i)).isoformat() + "Z",
        "prompt_id": f"p{i:04}",
        "prompt": f"Why does iPhone have issue related to {topics[i % len(topics)]}?",
        "mentions": [f"iPhone {12 + (i % 8)}"],  # cycles iPhone 12–19
        "prompt_type": "open-ended",
        "response": f"This issue can be caused by factors related to {topics[i % len(topics)].lower()}.",
        "citations": [f"https://site{i % 50 + 1}.com"],  # 50 fake sites
        "themes": [themes[i % len(themes)]],
        "topics": [topics[i % len(topics)]],
        "region": regions[i % len(regions)],
        "model": models[i % len(models)],
        "tags": ["apple", "branded"]
    }
    records.append(record)

# Write to JSONL file
with open("apple_prompt_response_1000.jsonl", "w") as f:
    for r in records:
        f.write(json.dumps(r) + "\n")

print("✅ 1,000 records generated in 'apple_prompt_response_1000.jsonl'")
