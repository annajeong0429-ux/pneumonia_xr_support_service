from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class AiAnalysisResponse(BaseModel):
    id: int
    record_id: int
    is_pneumonia: bool
    confidence: Decimal
    heatmap_url: str | None
    ai_model: str
    created_at: datetime

    model_config = {"from_attributes": True}
