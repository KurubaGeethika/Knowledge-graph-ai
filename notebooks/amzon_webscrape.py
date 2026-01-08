from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

# Setup Chrome driver using webdriver-manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Replace with the URL of the Amazon mobile product you want to scrape
product_url = "https://www.amazon.in/dp/B08XYZ1234"  # Example ASIN
driver.get(product_url)
time.sleep(5)  # wait for page to load

# Scroll down to Q&A section (adjust scroll value as needed)
driver.execute_script("window.scrollTo(0, 2000);")
time.sleep(2)

qna_data = []

# Find all question elements (selectors may vary depending on Amazon page layout)
questions = driver.find_elements(By.CSS_SELECTOR, "div.askTeaserQuestions div.a-fixed-left-grid")

for q in questions:
    try:
        question_text = q.find_element(By.CSS_SELECTOR, "a.askQuestionsLink").text
        answer_text = q.find_element(By.CSS_SELECTOR, "span.a-declarative + div").text
        qna_data.append({"question": question_text, "answer": answer_text})
    except Exception as e:
        continue

# Save to JSON
with open("amazon_mobile_qna.json", "w", encoding="utf-8") as f:
    json.dump(qna_data, f, indent=2)

print(f"Saved {len(qna_data)} Q&A pairs to amazon_mobile_qna.json")

driver.quit()
