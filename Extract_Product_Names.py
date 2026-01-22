import pandas as pd
import re

# Read the cleaned data
df = pd.read_csv("Amazon_Cleaned_Data.csv")

print("===== PRODUCT NAME EXTRACTION =====")
print(f"Total Records: {len(df)}")

# Function to extract clean product name
def extract_product_name(name):
    """
    Extracts product name by intelligently removing:
    - Quoted descriptions at the beginning
    - Features listed after asterisks (*)
    - Specifications in parentheses
    - Common feature keywords
    """
    if pd.isna(name):
        return name
    
    name = str(name).strip()
    
    # Step 1: Remove quoted descriptions at the beginning
    name = re.sub(r'^"[^"]*"\s*', '', name)
    
    # Step 2: Remove text in parentheses at start if looks like condition codes
    name = re.sub(r'^\([A-Z\s]+\)\s*', '', name)
    
    # Step 3: Handle asterisks - split and take longest meaningful part
    if '*' in name:
        parts = [p.strip() for p in name.split('*')]
        # Find the longest part that's likely the product name
        parts = [p for p in parts if p and len(p) > 3]
        name = parts[0] if parts else name
    
    # Step 4: Remove specification patterns at the end
    # Pattern: followed by numbers/specs
    spec_patterns = [
        r'\s+\d+\.?\d*\s*(GB|MB|MP|GHz|mAh|"|inch|inches|pixels?)\b.*$',
        r'\s+\d+\*\d+.*$',  # resolution like 1280*720
        r'\s+Android\s+\d+.*$',
        r'\s+MTK\d+.*$',
        r'\s+MT\d+.*$',
    ]
    
    for pattern in spec_patterns:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    
    # Step 5: Remove trailing specs in parentheses but keep color info
    # Remove (specs) at end but preserve actual model info
    name = re.sub(r'\s*\([^)]*(?:GB|RAM|ROM|Android|MTK|Core|Screen|MP|mAh)[^)]*\)\s*$', '', name)
    
    # Step 6: Remove trailing color info in parentheses if it's at very end
    # Pattern: (Single Color Word) at the very end - only if alone
    match = re.search(r'\s*\(([A-Za-z\s]+)\)\s*$', name)
    if match:
        color_candidate = match.group(1).strip()
        # List of common colors and minimal words
        if color_candidate.lower() in ['black', 'white', 'silver', 'gold', 'red', 'blue', 'green', 'gray', 'grey', 'rose gold']:
            name = name[:match.start()].strip()
    
    # Step 7: Remove trailing common generic words that are pure specs
    name = re.sub(r'\s+(?:Phone|Smartphone|Cellphone|Mobile|Device)$', '', name, flags=re.IGNORECASE)
    
    # Step 8: Remove "unlocked", "factory unlocked" and other qualifiers
    # These describe the product condition, not the model
    name = re.sub(r'\s*(factory\s+)?unlocked\s*', ' ', name, flags=re.IGNORECASE)
    
    # Remove common qualifiers that describe condition/warranty
    qualifiers = ['refurbished', 'sealed', 'new', 'retail', 'box', 'with box', 
                  'no contract', 'carrier unlocked', 'international version', 'international']
    for qualifier in qualifiers:
        name = re.sub(rf'\s+(?:{re.escape(qualifier)}).*$', '', name, flags=re.IGNORECASE)
    
    # Step 9: Remove long trailing descriptions (if more than 5 words and mostly common words)
    words = name.split()
    if len(words) > 8:
        # Common non-product words that indicate specs/features
        non_product_words = {'with', 'for', 'and', 'or', 'the', 'a', 'an', 'to', 'in', 
                            'from', 'by', 'of', 'at', 'as', 'is', 'are', 'be', 'been',
                            'unlocked', 'factory', 'dual', 'quad', 'core', 'sim', 'card',
                            '3g', '4g', 'lte', 'gsm', 'cdma', 'wcdma', 'android', 'phone',
                            'smartphone', 'cellphone', 'mobile', 'device', 'screen', 'display'}
        
        # Find where product description ends (usually after brand + model)
        # Keep first 5-6 meaningful words
        meaningful_words = []
        for word in words:
            if word.lower() not in non_product_words or len(meaningful_words) < 3:
                meaningful_words.append(word)
            if len(meaningful_words) >= 6:
                break
        
        if meaningful_words:
            name = ' '.join(meaningful_words)
    
    # Step 10: Clean up multiple spaces
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name if name and len(name) > 2 else "Unknown"

# Apply the extraction function
print("\nExtracting product names...")
df['Product Name'] = df['Product Name'].apply(extract_product_name)

# Show some examples
print("\nSample cleaned product names:")
print(df['Product Name'].head(10))

# Check unique product names
unique_count = df['Product Name'].nunique()
print(f"\nTotal distinct product names: {unique_count}")

# Save the updated dataframe
df.to_csv("Amazon_Cleaned_Data.csv", index=False)
print("\n✅ Product names cleaned and saved to Amazon_Cleaned_Data.csv")

# Also save a CSV with only unique product names for review
product_names_only = df[['Product Name']].drop_duplicates().sort_values('Product Name')
product_names_only.to_csv("Amazon_Product_name_Cleaned_Data.csv", index=False)
print("✅ Unique product names saved to Amazon_Product_name_Cleaned_Data.csv")
