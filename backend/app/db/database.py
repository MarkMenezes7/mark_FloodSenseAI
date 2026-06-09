import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

_pool = None

async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL)
    return _pool

async def get_db():
    pool = await get_pool()
    async with pool.acquire() as connection:
        yield connection

async def create_tables():
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Enable pgvector extension for RAG embeddings
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Alert subscriptions table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS alert_subscriptions (
                id SERIAL PRIMARY KEY,
                phone_number VARCHAR(20) UNIQUE NOT NULL,
                latitude FLOAT,
                longitude FLOAT,
                location_name VARCHAR(200),
                risk_threshold INTEGER DEFAULT 60,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)

        # Flood risk predictions log
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS risk_predictions (
                id SERIAL PRIMARY KEY,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                location_name VARCHAR(200),
                risk_score FLOAT NOT NULL,
                risk_level VARCHAR(20) NOT NULL,
                rainfall FLOAT,
                humidity FLOAT,
                temperature FLOAT,
                wind_speed FLOAT,
                predicted_at TIMESTAMP DEFAULT NOW()
            );
        """)

        print("✅ Database tables created successfully")
