import pandas as pd
import re
import numpy as np

# Load original raw data
raw_df = pd.read_csv('data/Amazon_Unlocked_Mobile.csv')

print("=" * 100)
print("IMPROVED PRODUCT NAME EXTRACTION WITH QUALITY VALIDATION")
print("=" * 100)

# 1. CLEAN PRODUCT NAMES - Remove obvious non-product descriptions
def clean_product_name(name):
    """Clean product name by removing unwanted descriptions and specifications"""
    if pd.isna(name):
        return None
    
    name = str(name).strip()
    
    # Remove quoted descriptions at start
    name = re.sub(r'^"[^"]*"\s*', '', name)
    
    # Handle asterisk-separated content (take first meaningful part)
    if '*' in name:
        parts = name.split('*')
        # Find first non-spec part
        for part in parts:
            part = part.strip()
            if part and len(part) > 3 and not re.match(r'^[A-Z]{1,3}$', part):
                name = part
                break
    
    # Remove parenthetical descriptions
    name = re.sub(r'\([^)]*\)', ' ', name)
    
    # Remove common unwanted qualifiers
    qualifiers = [
        r'\bunlocked\b', r'\bfactory.unlocked\b', r'\brefurbished\b',
        r'\bused\b', r'\bnew\b', r'\bopen.box\b', r'\bwarranty\b',
        r'\b\[update.*?\]\b'
    ]
    for qualifier in qualifiers:
        name = re.sub(qualifier, '', name, flags=re.IGNORECASE)
    
    # Remove Android version specs
    name = re.sub(r'android\s+\d+\.\d+', '', name, flags=re.IGNORECASE)
    
    # Remove screen size specs at start
    name = re.sub(r'^\d+\.?\d*["\']?\s*', '', name)
    
    # Remove RAM/ROM specs
    name = re.sub(r'\b\d+\s*(GB|MB)\s*(RAM|ROM|VRAM)\b', '', name, flags=re.IGNORECASE)
    
    # Remove processor specs
    name = re.sub(r'\b(Quad|Dual|Octa)\s+Core\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\b(MTK|Snapdragon|Mediatek|Exynos|Kirin)\b', '', name, flags=re.IGNORECASE)
    
    # Remove battery specs
    name = re.sub(r'\d+\s*mAh', '', name, flags=re.IGNORECASE)
    
    # Remove feature-only descriptors
    features = [
        r'\bwaterproof\b', r'\bshockproof\b', r'\brugged\b',
        r'\blong.standby\b', r'\bdual.sim\b', r'\bsingle.sim\b',
        r'\bstand.by\b', r'\bcapacitive\b', r'\btouch\b',
        r'\bscreen\b', r'\bdisplay\b'
    ]
    for feature in features:
        name = re.sub(feature, '', name, flags=re.IGNORECASE)
    
    # Remove software/non-product keywords
    non_products = [
        r'\bsoftware\b', r'\bdownload\b', r'\brecovery\b', r'\bbugged\b',
        r'\bpatch\b', r'\bupdate\b', r'\bplugin\b'
    ]
    for non_prod in non_products:
        name = re.sub(non_prod, '', name, flags=re.IGNORECASE)
    
    # Remove URLs
    name = re.sub(r'https?://\S+|www\.\S+|\.com', '', name, flags=re.IGNORECASE)
    
    # Remove special characters but keep alphanumeric, spaces, hyphens
    name = re.sub(r'[^\w\s\-]', ' ', name)
    
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Remove trailing/leading hyphens
    name = name.strip('-').strip()
    
    return name if name else None


# 2. VALIDATE PRODUCT NAME QUALITY
def validate_product_name(product_name, brand_name):
    """
    Validate if extracted name is a real product, not just specs.
    Returns quality score: 0-100
    """
    if not product_name or len(product_name) < 3:
        return 0
    
    score = 50  # Base score
    
    # Check length (good products are typically 10-80 chars)
    if 10 <= len(product_name) <= 80:
        score += 15
    elif len(product_name) < 5:
        return 0  # Too short = likely spec
    
    # Check for brand name presence
    if pd.notna(brand_name) and str(brand_name).lower() in product_name.lower():
        score += 15
    
    # Check for meaningful words (not just model codes)
    words = product_name.split()
    meaningful_words = 0
    
    # Words that indicate real products
    product_indicators = ['phone', 'mobile', 'smartphone', 'model', 'series', 'plus', 'pro', 'ultra', 'max', 'lite', 'mini']
    
    for word in words:
        # Count words longer than 2 chars that aren't pure specs
        if len(word) > 2:
            meaningful_words += 1
            # Bonus for product indicator words
            if word.lower() in product_indicators:
                score += 5
    
    # Require minimum meaningful words
    if meaningful_words >= 2:
        score += 10
    else:
        score = max(0, score - 20)  # Penalize spec-only names
    
    # Penalty for pure model codes (e.g., "G9006W", "I9220")
    if re.match(r'^[A-Z]\d{4,}$', product_name.replace('(', '').replace(')', '')):
        score = max(0, score - 30)
    
    # Penalty for pure numbers (model numbers)
    if product_name.replace('(', '').replace(')', '').replace(' ', '').isalnum():
        if product_name[0].isdigit():
            score = max(0, score - 25)
    
    # Penalty for screen sizes starting product name
    if re.match(r'^\d+\.?\d*["\']', product_name):
        score = max(0, score - 30)
    
    # Penalty for Android version only
    if re.match(r'^Android', product_name, re.IGNORECASE):
        score = max(0, score - 30)
    
    # Penalty for spec keywords
    spec_keywords = ['capacitive', 'touchscreen', 'standby', 'waterproof', 'shockproof']
    for keyword in spec_keywords:
        if keyword in product_name.lower():
            score = max(0, score - 10)
    
    return min(100, max(0, score))


# 3. PROCESS ALL RECORDS
print("\nProcessing records...")
cleaned_names = []
quality_scores = []
original_names = []
brand_names = []

for idx, row in raw_df.iterrows():
    if (idx + 1) % 50000 == 0:
        print(f"  Processed {idx + 1:,} / {len(raw_df):,}")
    
    original_name = row['Product Name']
    brand_name = row['Brand Name']
    
    # Clean the name
    cleaned = clean_product_name(original_name)
    
    # Validate quality
    if cleaned:
        quality = validate_product_name(cleaned, brand_name)
    else:
        quality = 0
    
    cleaned_names.append(cleaned)
    quality_scores.append(quality)
    original_names.append(original_name)
    brand_names.append(brand_name)

# 4. ADD TO DATAFRAME
raw_df['Cleaned_Product_Name'] = cleaned_names
raw_df['Quality_Score'] = quality_scores

# 5. FILTER BY QUALITY THRESHOLD
quality_threshold = 60  # Only keep scores >= 60

print(f"\nQuality score distribution:")
print(f"  Excellent (80-100): {(raw_df['Quality_Score'] >= 80).sum():,}")
print(f"  Good      (60-79):  {((raw_df['Quality_Score'] >= 60) & (raw_df['Quality_Score'] < 80)).sum():,}")
print(f"  Fair      (40-59):  {((raw_df['Quality_Score'] >= 40) & (raw_df['Quality_Score'] < 60)).sum():,}")
print(f"  Poor      (0-39):   {(raw_df['Quality_Score'] < 40).sum():,}")

# 6. CREATE CLEANED DATASET
filtered_df = raw_df[raw_df['Quality_Score'] >= quality_threshold].copy()

# Remove Quality_Score column before saving (keep for analysis)
quality_analysis_df = raw_df[['Product Name', 'Cleaned_Product_Name', 'Quality_Score', 'Brand Name']].copy()

# Save main dataset
output_df = filtered_df.drop(columns=['Quality_Score', 'Cleaned_Product_Name']).copy()
output_df.to_csv('Amazon_Cleaned_Data.csv', index=False)

print(f"\n" + "=" * 100)
print("RESULTS")
print("=" * 100)
print(f"\nOriginal records:           {len(raw_df):,}")
print(f"Records with quality >= 60: {len(filtered_df):,}")
print(f"Records removed:            {len(raw_df) - len(filtered_df):,} ({(len(raw_df)-len(filtered_df))/len(raw_df)*100:.2f}%)")
print(f"Retention rate:             {len(filtered_df)/len(raw_df)*100:.2f}%")

# 7. CREATE UNIQUE PRODUCT NAMES
unique_products = filtered_df.groupby('Product Name').size().reset_index(name='count')
unique_products = unique_products.sort_values('count', ascending=False)

print(f"\nUnique product names:       {len(unique_products):,}")
print(f"Average records per product: {len(filtered_df) / len(unique_products):.1f}")

# Save unique products
unique_products_df = filtered_df[['Product Name', 'Brand Name', 'Price', 'Rating', 'Reviews']].drop_duplicates('Product Name')
unique_products_df = unique_products_df.sort_values('Product Name')
unique_products_df.to_csv('Amazon_Product_name_Cleaned_Data.csv', index=False)

# 8. SAVE QUALITY ANALYSIS
quality_analysis_df.to_csv('Product_Quality_Analysis.csv', index=False)

print(f"\nFiles saved:")
print(f"  ✓ Amazon_Cleaned_Data.csv ({len(filtered_df):,} records)")
print(f"  ✓ Amazon_Product_name_Cleaned_Data.csv ({len(unique_products_df):,} unique products)")
print(f"  ✓ Product_Quality_Analysis.csv (for review)")

# 9. SHOW EXAMPLES OF REMOVED RECORDS
print(f"\n" + "=" * 100)
print("EXAMPLES OF REMOVED LOW-QUALITY RECORDS")
print("=" * 100)

removed_df = raw_df[raw_df['Quality_Score'] < quality_threshold]
removed_examples = removed_df.nlargest(20, 'Quality_Score')[['Product Name', 'Cleaned_Product_Name', 'Quality_Score', 'Brand Name']]

for idx, row in removed_examples.iterrows():
    print(f"\nOriginal:  {row['Product Name'][:80]}")
    print(f"Cleaned:   {row['Cleaned_Product_Name']}")
    print(f"Score:     {row['Quality_Score']:.0f}/100 (Brand: {row['Brand Name']})")

# 10. SHOW EXAMPLES OF KEPT RECORDS
print(f"\n" + "=" * 100)
print("EXAMPLES OF HIGH-QUALITY KEPT RECORDS")
print("=" * 100)

kept_df = raw_df[raw_df['Quality_Score'] >= quality_threshold]
kept_examples = kept_df.nlargest(20, 'Quality_Score')[['Product Name', 'Cleaned_Product_Name', 'Quality_Score', 'Brand Name']]

for idx, row in kept_examples.iterrows():
    print(f"\nOriginal:  {row['Product Name'][:80]}")
    print(f"Cleaned:   {row['Cleaned_Product_Name']}")
    print(f"Score:     {row['Quality_Score']:.0f}/100 (Brand: {row['Brand Name']})")

print(f"\n" + "=" * 100)
