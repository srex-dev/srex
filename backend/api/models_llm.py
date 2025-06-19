from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, DateTime, Float, JSON, Integer, Index
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

class DriftAnalysis(Base):
    __tablename__ = "drift_analyses"

    id = Column(Integer, primary_key=True, index=True)
    analysis_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    period_days = Column(Integer, nullable=False)
    service_name = Column(String, nullable=True)  # NULL for all services
    total_analyses = Column(Integer, nullable=False)
    
    # Confidence Drift
    confidence_status = Column(String, nullable=False)
    recent_avg_confidence = Column(Float, nullable=True)
    older_avg_confidence = Column(Float, nullable=True)
    confidence_drift_percentage = Column(Float, nullable=True)
    confidence_drift_direction = Column(String, nullable=True)
    confidence_trend = Column(String, nullable=True)
    
    # Output Consistency
    consistency_percentage = Column(Float, nullable=False)
    consistent_structure_count = Column(Integer, nullable=False)
    structure_variations_count = Column(Integer, nullable=False)
    missing_fields_sli = Column(Integer, nullable=False, default=0)
    missing_fields_slo = Column(Integer, nullable=False, default=0)
    missing_fields_alerts = Column(Integer, nullable=False, default=0)
    missing_fields_suggestions = Column(Integer, nullable=False, default=0)
    
    # Coverage Drift
    coverage_status = Column(String, nullable=False)
    recent_avg_slis = Column(Float, nullable=True)
    recent_avg_slos = Column(Float, nullable=True)
    recent_avg_alerts = Column(Float, nullable=True)
    recent_avg_suggestions = Column(Float, nullable=True)
    older_avg_slis = Column(Float, nullable=True)
    older_avg_slos = Column(Float, nullable=True)
    older_avg_alerts = Column(Float, nullable=True)
    older_avg_suggestions = Column(Float, nullable=True)
    slis_change = Column(Float, nullable=True)
    slis_percentage_change = Column(Float, nullable=True)
    slos_change = Column(Float, nullable=True)
    slos_percentage_change = Column(Float, nullable=True)
    alerts_change = Column(Float, nullable=True)
    alerts_percentage_change = Column(Float, nullable=True)
    suggestions_change = Column(Float, nullable=True)
    suggestions_percentage_change = Column(Float, nullable=True)
    
    # Quality Drift
    avg_quality_score = Column(Float, nullable=False)
    validation_present_count = Column(Integer, nullable=False)
    complete_outputs_count = Column(Integer, nullable=False)
    validation_percentage = Column(Float, nullable=False)
    completeness_percentage = Column(Float, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Index for efficient querying
    __table_args__ = (
        Index('idx_drift_analysis_date', 'analysis_date'),
        Index('idx_drift_analysis_service', 'service_name'),
        Index('idx_drift_analysis_period', 'period_start', 'period_end'),
    ) 