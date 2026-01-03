import json
from datetime import datetime, timedelta
import random

# Logical mapping of topic → theme
topic_theme_map = {
    "Battery": "Hardware",
    "Charging": "Hardware",
    "Apple Silicon": "Performance",
    "Thermal": "Performance",
    "Privacy": "Security"
}

# Sample topics
topics = list(topic_theme_map.keys())
regions = ["United States", "India", "EU", "UK", "Canada"]
models = ["ChatGPT", "Gemini", "Copilot"]

# Sample citations by topic
citations_map = {
    "Battery": ["Apple Support: Battery Guide", "iFixit: iPhone Battery Tips"],
    "Charging": ["Apple Support: Charging Guidelines", "MacRumors: iPhone Charging Issues"],
    "Apple Silicon": ["Apple Developer: M1/M2 Overview", "AnandTech: Apple Silicon Review"],
    "Thermal": ["Apple Support: Device Temperature", "iFixit: iPhone Repair Guides"],
    "Privacy": ["Apple Privacy Whitepaper", "TechCrunch: iOS Privacy Features"]
}

# Sample enriched responses by topic
response_templates = {
    "Battery": [
        "Battery may drain faster due to background apps, high screen brightness, or aging battery.",
        "Battery performance can be impacted by multiple apps running in the background and location services."
    ],
    "Charging": [
        "Charging issues can occur due to faulty cables, non-certified adapters, or outdated iOS versions.",
        "Slow charging may result from high usage while charging or device temperature."
    ],
    "Apple Silicon": [
        "Apple Silicon improves performance by integrating CPU, GPU, and memory on a single chip.",
        "Energy efficiency is enhanced in Apple Silicon thanks to optimized cores and unified memory."
    ],
    "Thermal": [
        "Overheating occurs during heavy CPU/GPU tasks like gaming or video rendering.",
        "Device temperature rises when using power-intensive apps or high ambient heat."
    ],
    "Privacy": [
        "Privacy issues can happen if location services or app tracking are enabled.",
        "iOS features like App Tracking Transparency help protect user privacy."
    ]
}

# Base timestamp
base_time = datetime(2024, 8, 1, 9, 0, 0)

records = []

for i in range(1, 1001):
    topic = topics[i % len(topics)]
    theme = topic_theme_map[topic]
    region = regions[i % len(regions)]
    model = models[i % len(models)]
    mentions = f"iPhone {12 + (i % 6)}"  # iPhone 12–17
    response = random.choice(response_templates[topic])
    citation = random.choice(citations_map[topic])
    
    record = {
        "run_id": f"r{i:04}",
        "created_at": (base_time + timedelta(minutes=i)).isoformat() + "Z",
        "prompt_id": f"p{i:04}",
        "prompt": f"Why does iPhone have issue related to {topic}?",
        "mentions": [mentions],
        "prompt_type": "open-ended",
        "response": response,
        "citations": [citation],
        "themes": [theme],
        "topics": [topic],
        "region": region,
        "model": model,
        "tags": ["apple", topic.lower(), theme.lower()]
    }
    
    records.append(record)

# Write JSONL file
with open("apple_prompt_response_1000_realistic.jsonl", "w") as f:
    for r in records:
        f.write(json.dumps(r) + "\n")

print("✅ 1,000 realistic records generated in 'apple_prompt_response_1000_realistic.jsonl'")
