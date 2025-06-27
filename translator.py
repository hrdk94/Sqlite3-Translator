import sqlite3
import pandas as pd
import shutil
import time
import random
import sys
import os
from tqdm import tqdm
from deep_translator import GoogleTranslator

# === CLI INPUT ===
if len(sys.argv) < 2:
    print("❌ Usage: python translate.py <your-database-file.db>")
    sys.exit(1)

original_db_path = sys.argv[1]

if not os.path.exists(original_db_path):
    print(f"❌ File not found: {original_db_path}")
    sys.exit(1)

# === GENERATED PATHS ===
base_name = os.path.splitext(original_db_path)[0]
translated_db_path = f"{base_name}_translated.db"
log_file_path = f"{base_name}_log.txt"

# === START ===
shutil.copyfile(original_db_path, translated_db_path)
conn = sqlite3.connect(translated_db_path)
cursor = conn.cursor()

start_time = time.time()
log_entries = []

# === HELPERS ===
def is_chinese(text):
    return any('\u4e00' <= char <= '\u9fff' for char in str(text))

def translate_text(text):
    try:
        if text and isinstance(text, str) and is_chinese(text):
            time.sleep(random.uniform(0.3, 0.5))  # throttle
            return GoogleTranslator(source='auto', target='en').translate(text)
    except Exception as e:
        try:
            time.sleep(random.uniform(0.7, 1.2))  # retry
            return GoogleTranslator(source='auto', target='en').translate(text)
        except Exception as e2:
            log_entries.append(f"❌ Failed: {text} -> {e2}")
    return text

# === TRANSLATE ===
tables_df = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
tables = tables_df['name'].tolist()

for table in tables:
    try:
        print(f"\n🔍 Scanning table: {table}")
        df = pd.read_sql_query(f"SELECT rowid, * FROM {table}", conn)

        text_fields = [col for col in df.columns if df[col].dtype == object and any(df[col].dropna().astype(str).apply(is_chinese))]

        if not text_fields:
            print("⚪ No Chinese fields detected.")
            continue

        log_entries.append(f"✅ Table: {table}, Fields: {', '.join(text_fields)}")
        print(f"🌐 Translating: {', '.join(text_fields)}")

        for field in text_fields:
            df[field] = list(tqdm(
                (translate_text(text) if is_chinese(text) else text for text in df[field]),
                total=len(df),
                desc=f"{table}.{field}"
            ))

        for _, row in df.iterrows():
            update_query = f"UPDATE {table} SET " + ", ".join(f"{field}=?" for field in text_fields) + " WHERE rowid=?"
            values = [row[field] for field in text_fields] + [row["rowid"]]
            cursor.execute(update_query, values)

        conn.commit()

    except Exception as e:
        log_entries.append(f"❌ Error in table {table}: {e}")
        print(f"❌ Error in table {table}: {e}")

# === FINISH ===
with open(log_file_path, "w", encoding="utf-8") as log_file:
    log_file.write("\n".join(log_entries))

conn.close()

print(f"\n✅ All done! Translated DB saved as: {translated_db_path}")
print(f"📝 Log file created: {log_file_path}")
print(f"⏱️ Total time: {round(time.time() - start_time, 2)} seconds.")
