# import os
# import uuid
# import psycopg2
# import pandas as pd
# from dotenv import load_dotenv
# from sentence_transformers import SentenceTransformer

# # .env 로드
# load_dotenv()

# # PostgreSQL (Supabase) 연결
# conn = psycopg2.connect(
#     host=os.getenv("DB_HOST"),
#     port=os.getenv("DB_PORT"),
#     dbname=os.getenv("DB_NAME"),
#     user=os.getenv("DB_USER"),
#     password=os.getenv("DB_PASSWORD")
# )
# cur = conn.cursor()

# # 임베딩 모델 로드 (384차원 벡터)
# model = SentenceTransformer("all-MiniLM-L6-v2")

# # 임베딩 후 DB에 저장
# def insert_body_with_embedding(body: str):
#     embedding = model.encode(body).tolist()
#     cur.execute(
#         "INSERT INTO support_bodies (id, body, embedding) VALUES (%s, %s, %s)",
#         (str(uuid.uuid4()), body, embedding)
#     )
#     conn.commit()

# # CSV 파일 로드
# df = pd.read_csv("dataset-tickets-multi-lang3-4k.csv")
# en_bodies = df[df["language"] == "en"]["body"].dropna().reset_index(drop=True)

# # for body in en_bodies[:2]:
# #     insert_body_with_embedding(body)
    
# for body in en_bodies:
#     insert_body_with_embedding(body)
    


# print("✅ Data successfully inserted into Supabase!")

import os
import uuid
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# .env 로드
load_dotenv()

# PostgreSQL (Supabase) 연결
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

# 임베딩 모델 로드 (384차원 벡터)
model = SentenceTransformer("all-MiniLM-L6-v2")

# 임베딩 후 DB에 저장
def insert_body_with_answer(body: str, answer: str):
    embedding = model.encode(body).tolist()
    cur.execute(
        "INSERT INTO support_bodies (id, body, embedding, answer) VALUES (%s, %s, %s, %s)",
        (str(uuid.uuid4()), body, embedding, answer)
    )
    conn.commit()

# CSV 파일 로드
df = pd.read_csv("dataset-tickets-multi-lang3-4k.csv")
en_rows = df[(df["language"] == "en") & df["body"].notna() & df["answer"].notna()].reset_index(drop=True)

for _, row in en_rows.iterrows():
    insert_body_with_answer(row["body"], row["answer"])

print("✅ Questions + Answers successfully inserted into Supabase!")


# import os
# import psycopg2
# import pandas as pd
# from dotenv import load_dotenv

# # .env 로드
# load_dotenv()

# # PostgreSQL 연결
# conn = psycopg2.connect(
#     host=os.getenv("DB_HOST"),
#     port=os.getenv("DB_PORT"),
#     dbname=os.getenv("DB_NAME"),
#     user=os.getenv("DB_USER"),
#     password=os.getenv("DB_PASSWORD")
# )
# cur = conn.cursor()

# # CSV 로드
# df = pd.read_csv("dataset-tickets-multi-lang3-4k.csv")
# en_rows = df[(df["language"] == "en") & df["body"].notna() & df["answer"].notna()].reset_index(drop=True)

# # answer만 업데이트
# updated_count = 0
# for _, row in en_rows.iterrows():
#     body = row["body"]
#     answer = row["answer"]
#     cur.execute(
#         "UPDATE support_bodies SET answer = %s WHERE body = %s",
#         (answer, body)
#     )
#     if cur.rowcount > 0:
#         updated_count += 1

# conn.commit()
# print(f"✅ {updated_count} answers successfully updated in Supabase.")
