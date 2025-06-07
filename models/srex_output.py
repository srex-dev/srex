# models/srex_output.py

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class SrexOutput(Base):
    __tablename__ = 'srex_outputs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    context_type = Column(String, nullable=False)
    service_name = Column(String, nullable=False)
    data = Column(JSONB, nullable=False)
