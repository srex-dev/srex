from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class LLMOutput(Base):
    __tablename__ = "llm_outputs"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String, nullable=False)
    input = Column(JSON, nullable=False)
    output = Column(JSON, nullable=False)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=func.utcnow())
    updated_at = Column(DateTime, default=func.utcnow(), onupdate=func.utcnow())

class DriftAnalysis(Base):
    __tablename__ = "drift_analyses"

    id = Column(Integer, primary_key=True, index=True)
    analysis_date = Column(DateTime, default=func.utcnow(), nullable=False)
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
    created_at = Column(DateTime, default=func.utcnow())
    updated_at = Column(DateTime, default=func.utcnow(), onupdate=func.utcnow())
    
    # Index for efficient querying
    __table_args__ = (
        Index('idx_drift_analysis_date', 'analysis_date'),
        Index('idx_drift_analysis_service', 'service_name'),
        Index('idx_drift_analysis_period', 'period_start', 'period_end'),
    ) 