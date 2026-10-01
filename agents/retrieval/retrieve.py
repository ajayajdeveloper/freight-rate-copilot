import os
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

embedder = SentenceTransformer('all-MiniLM-L6-v2')

def retrieve(question, top_k=3):
    question_vector = embedder.encode(question).tolist()

    cur.execute("""
        SELECT chunk_text, source_file,
               1 - (embedding <=> %s::vector) AS semantic_score,
               ts_rank(to_tsvector('english', chunk_text), plainto_tsquery('english', %s)) AS keyword_score
        FROM policy_chunks
        ORDER BY (0.6 * (1 - (embedding <=> %s::vector))) + (0.4 * ts_rank(to_tsvector('english', chunk_text), plainto_tsquery('english', %s))) DESC
        LIMIT %s;
    """, (question_vector, question, question_vector, question, top_k))

    return cur.fetchall()

if __name__ == "__main__":
    question = input("Ask a rate/policy question: ")
    results = retrieve(question)
    for chunk_text, source_file, semantic_score, keyword_score in results:
        print(f"--- {source_file} (semantic={semantic_score:.3f}, keyword={keyword_score:.3f}) ---")
        print(chunk_text[:200])
        print()
