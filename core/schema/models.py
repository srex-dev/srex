from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class SLIInput(BaseModel):
    """SLI input data."""
    component: str
    sli_type: str
    value: float
    unit: str
    query: str
    source: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class ServiceInput(BaseModel):
    """Service input data."""
    service: str
    service_name: Optional[str] = None
    sli_inputs: List[SLIInput] = Field(default_factory=list)
    temperature: Optional[float] = None

class SLIDefinition(BaseModel):
    """SLI definition."""
    name: str
    description: str
    type: str
    target: float
    unit: str
    window: str
    query: str
    source: str
    metadata: Optional[Dict[str, Any]] = None

class SLODefinition(BaseModel):
    """SLO definition."""
    name: str
    description: str
    target: float
    window: str
    slis: List[str]
    metadata: Optional[Dict[str, Any]] = None

class AlertDefinition(BaseModel):
    """Alert definition."""
    name: str
    description: str
    condition: str
    severity: str
    slo: str
    metadata: Optional[Dict[str, Any]] = None

class LLMSuggestion(BaseModel):
    """LLM suggestion."""
    type: str
    description: str
    priority: str
    action: str
    metadata: Optional[Dict[str, Any]] = None

class OutputSchema(BaseModel):
    """Output schema."""
    sli: List[SLIDefinition] = Field(default_factory=list)
    slo: List[SLODefinition] = Field(default_factory=list)
    alerts: List[AlertDefinition] = Field(default_factory=list)
    explanation: str
    llm_suggestions: List[LLMSuggestion] = Field(default_factory=list)
    ai_model: str
    temperature: float
    ai_confidence: float
    metadata: Optional[Dict[str, Any]] = None 