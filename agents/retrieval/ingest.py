import os
import re
import glob
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

conn = psycopg2.connect(
    host=os.environ.get("DB_HOST"),
    port=os.environ.get("DB_PORT"),
    dbname=os.environ.get("DB_NAME"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS policy_chunks (
        id SERIAL PRIMARY KEY,
        source_file TEXT,
        chunk_text TEXT,
        embedding vector(384)
    );
""")
conn.commit()

embedder = SentenceTransformer('all-MiniLM-L6-v2')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
policy_files = glob.glob(os.path.join(SCRIPT_DIR, "../../data/policies/*.md"))


for filepath in policy_files:
    filename = os.path.basename(filepath)
    with open(filepath, "r") as f:
        content = f.read()

    raw_sections = re.split(r'\n## ', content)
    for i, section in enumerate(raw_sections):
        text = section.strip()
        if not text:
            continue
        if i > 0:
            text = "## " + text

        vector = embedder.encode(text).tolist()
        cur.execute(
            "INSERT INTO policy_chunks (source_file, chunk_text, embedding) VALUES (%s, %s, %s);",
            (filename, text, vector)
        )

conn.commit()
cur.execute("SELECT COUNT(*) FROM policy_chunks;")
print(f"Total chunks in database: {cur.fetchone()[0]}")
