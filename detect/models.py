from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any

class Alert(BaseModel):
    id: str
    rule_id: str
    rule_name: str
    severity: str
    risk_score: int
    created_at: datetime
    details: Dict[str, Any]
    