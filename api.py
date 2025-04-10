import os
os.environ["TRANSFORMERS_NO_TF"] = "1"

from fastapi import FastAPI, Query
from pydantic import BaseModel
import os
import uuid
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Connect to Supabase (PostgreSQL)
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# FastAPI app
app = FastAPI()

# Optional CORS settings (for frontend to call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

@app.post("/search")
def search_similar_questions(request: QueryRequest):
    embedding = model.encode(request.query).tolist()
    cur.execute(
        """
        SELECT body FROM support_bodies 
        ORDER BY embedding <-> %s 
        LIMIT %s;
        """,
        (embedding, request.top_k)
    )
    results = [row[0] for row in cur.fetchall()]
    return {"query": request.query, "results": results}