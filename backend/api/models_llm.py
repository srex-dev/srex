from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, DateTime, Float, JSON
from datetime import datetime
import uuid

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/srex"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

class LLMOutput(Base):
    __tablename__ = "llm_outputs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    task = Column(String)
    input = Column(JSON)
    output = Column(JSON)
    confidence = Column(Float)
    explanation = Column(String) 