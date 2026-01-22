import pandas as pd

# 1️⃣ Read CSV file
file_path = "data/Amazon_Unlocked_Mobile.csv"   # change path if needed
df = pd.read_csv(file_path)

print("===== INITIAL DATA INFO =====")
print("Total Records:", len(df))
print("\nNull values per column:")
print(df.isnull().sum())

# 2️⃣ Drop rows where main columns are null
main_cols = ['Product Name', 'Brand Name', 'Reviews']

df_before = len(df)
df = df.dropna(subset=main_cols)
df_after = len(df)

print("\n===== AFTER DROPPING MAIN COLUMN NULLS =====")
print(f"Rows dropped: {df_before - df_after}")
print("Total Records after drop:", df_after)

# 3️⃣ Fill null values in other columns with suitable defaults
for col in df.columns:
    if col not in main_cols:
        if df[col].dtype == 'object':  # text columns
            df[col] = df[col].fillna("Unknown")
        else:  # numeric columns
            df[col] = df[col].fillna(0)

# 4️⃣ Final null check
print("\n===== FINAL NULL CHECK =====")
print(df.isnull().sum())

print("\nFinal Total Records:", len(df))

# Optional: Save cleaned data
df.to_csv("Amazon_Cleaned_Data.csv", index=False)
print("\n✅ Cleaned data saved as Amazon_Cleaned_Data.csv")
