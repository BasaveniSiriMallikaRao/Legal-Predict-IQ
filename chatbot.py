import os
import sqlite3
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import shutil
from transformers import BartTokenizer, BartForConditionalGeneration

# Define the database path
DB_PATH = os.path.join("database", "database2.db")

# Load pre-trained BART model and tokenizer
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

# Function to create the database
def create_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            user_id TEXT,
            phone_number TEXT,
            email TEXT,
            profession TEXT,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS Files (
            id INTEGER PRIMARY KEY,
            file_name TEXT,
            file_type TEXT,
            upload_date TEXT,
            file_content TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to register a new user
def register_user(username, user_id, phone_number, email, profession, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO Users (username, user_id, phone_number, email, profession, password)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, user_id, phone_number, email, profession, password))
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Username already exists.")
    finally:
        conn.close()

# Function to authenticate user login
def authenticate_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT password FROM Users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    return result is not None and result[0] == password

# Function to save files to the database
def save_file_to_db(file, file_name=None, file_type=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if isinstance(file, bytes):
        file_content = file.decode('utf-8')
    else:
        file_content = file.read().decode('utf-8')
        file_name = file.name
        file_type = file.type

    c.execute('SELECT id FROM Files WHERE file_name = ?', (file_name,))
    if not c.fetchone():
        c.execute('''
            INSERT INTO Files (file_name, file_type, upload_date, file_content)
            VALUES (?, ?, ?, ?)
        ''', (file_name, file_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), file_content))
        conn.commit()
    conn.close()

# Function to retrieve all files and their contents from the database
def get_all_files():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, file_name, file_type, file_content FROM Files')
    files = c.fetchall()
    conn.close()
    return files

# Function to split text into chunks
def split_text_into_chunks(text, chunk_size=300):
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

# Function to handle user query and search for the most relevant answer
def handle_user_query(query):
    files = get_all_files()

    chunked_contents = []
    chunk_file_map = []
    for file in files:
        file_chunks = split_text_into_chunks(file[3])
        chunked_contents.extend(file_chunks)
        chunk_file_map.extend([file[1]] * len(file_chunks))

    vectorizer = TfidfVectorizer()
    chunk_vectors = vectorizer.fit_transform(chunked_contents)
    query_vector = vectorizer.transform([query])

    cosine_similarities = cosine_similarity(query_vector, chunk_vectors).flatten()
    best_match_idx = cosine_similarities.argmax()
    best_match_score = cosine_similarities[best_match_idx]

    if best_match_score > 0.1:
        best_match_chunk = chunked_contents[best_match_idx]
        best_match_file = chunk_file_map[best_match_idx]

        inputs = tokenizer.encode(f"Question: {query} Context: {best_match_chunk}", return_tensors="pt",
                                  max_length=1024, truncation=True)
        summary_ids = model.generate(inputs, max_length=100, min_length=30, length_penalty=2.0, num_beams=4,
                                     early_stopping=True)
        answer = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        return f"Answer from file '{best_match_file}':\n\n{answer}"
    else:
        return "Sorry, no relevant answer was found in the documents."

# Function to process uploaded zip folder and save each file to the database
def process_zip_folder(uploaded_folder):
    folder_path = "uploaded_folder.zip"
    with open(folder_path, "wb") as f:
        f.write(uploaded_folder.getbuffer())

    shutil.unpack_archive(folder_path, "temp_folder")

    for root, dirs, files in os.walk("temp_folder"):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, "rb") as f:
                file_content = f.read()
                file_name = os.path.basename(file_path)
                if file_name.endswith('.txt'):
                    file_type = 'text/plain'
                elif file_name.endswith('.py'):
                    file_type = 'text/x-python'
                save_file_to_db(file_content, file_name, file_type)

    shutil.rmtree("temp_folder")
    os.remove(folder_path)