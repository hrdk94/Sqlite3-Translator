# Sqlite3-Translator
# SQLite Chinese-to-English Translator

A Python script that scans an entire SQLite database for Chinese text and translates it into English using the [deep-translator](https://github.com/nidhaloff/deep-translator) library (Google Translate backend).

---

## 🧠 Features

- Scans all tables in a `.db` file
- Automatically detects Chinese text fields
- Translates using Google Translate
- Creates a full translated copy of the database
- Generates a log of what was translated

---

## 🔧 Requirements

- Python 3.7+
- Internet connection (Google Translate API via `deep-translator`)

Install dependencies with:

```bash
pip install -r requirements.txt
