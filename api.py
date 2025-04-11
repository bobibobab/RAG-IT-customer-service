import json
import os
os.environ["TRANSFORMERS_NO_TF"] = "1"

from fastapi import FastAPI, Query, HTTPException, Depends
from pydantic import BaseModel
import os
import uuid
from openai import OpenAI
import psycopg2
from psycopg2.extras import Json
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware
import traceback
from pgvector.psycopg2 import register_vector 

# Load environment variables
load_dotenv()

# Database connection variables
conn = None
cur = None
db_connected = False
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Try to connect to Supabase (PostgreSQL)
try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    register_vector(conn)
    cur = conn.cursor()
    db_connected = True
    print("Database connection successful")
except Exception as e:
    print(f"Database connection error: {str(e)}")
    print("API will start in limited mode without database features")

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# FastAPI app
app = FastAPI()

# Optional CORS settings (for frontend to call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5000", "http://127.0.0.1:5000", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3
@app.post("/search")
def search_similar_questions(request: QueryRequest):
    if not db_connected:
        return {
            "query": request.query,
            "results": [],
            "error": "Database connection is not available. Please check your environment variables."
        }
    
    try:
        query_embedding = np.array(model.encode(request.query))

        vector_str = "[" + ",".join([str(x) for x in query_embedding]) + "]"

        cur.execute(
            """
            SELECT body, embedding, answer
            FROM support_bodies
            ORDER BY embedding <-> %s::vector
            LIMIT %s;
            """,
            (vector_str, request.top_k)
        )

        
        results = []
        for row in cur.fetchall():
            body, embedding, answer = row
            embedding_np = np.array(embedding, dtype=np.float32)
            cosine_similarity = np.dot(query_embedding, embedding_np) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding_np)
            )

            if cosine_similarity >= 0.3:
                results.append({
                    "question": body,
                    "similarity": round(float(cosine_similarity), 4),
                    "answer": answer
                })

            if len(results) >= request.top_k:
                break
        
        context = "The following are previous similar questions, their similarity scores, and the answers given:\n\n"
        for item in results:
            context += f"Question: {item['question']}\n"
            context += f"Similarity Score: {item['similarity']}\n"
            context += f"Answer: {item['answer']}\n\n"


        prompt = f"""
            You are an IT customer support assistant.

            Based on the previous similar questions and answers below, generate a helpful answer for the current user's question.

            Please respond in this exact JSON format (without truncation or incomplete data):
            {{
            "summary": "final helpful answer to the user",
            "source_questions": ["..."],
            "source_answers": ["..."]
            }}

            {context}
            User's question: {request.query}

            Respond only in the exact JSON format above (do not truncate the response, ensure proper closure of the JSON structure):
            """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 또는 "gpt-4" 도 가능
            messages=[
                {"role": "system", "content": "You are an IT customer support assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        try:
            gpt_text = response.choices[0].message.content.strip()
            print("GPT Response: ", gpt_text)
            parsed_json = json.loads(gpt_text)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse GPT response: {str(e)}")
        
        # Step 5: Final return value
        return {
            "query": request.query,
            "results": results,
            "gpt_answer": parsed_json  
        }


    except Exception as e:
        print(f"Search error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))



# Simple test endpoint
@app.get("/gptAnswer")
def health_check():
    return {
        "status": "ok", 
        "db_connected": db_connected
    }