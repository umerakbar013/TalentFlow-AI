from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class ApplicationStage(str, Enum):
    VALIDATION = "VALIDATION"
    CONSENT_GATE = "CONSENT_GATE"
    SCREENING = "SCREENING"
    INTERVIEW = "INTERVIEW"
    NEGOTIATION = "NEGOTIATION"
    OFFER_ISSUED = "OFFER_ISSUED"
    REJECTED = "REJECTED"

class ComplianceConsent(BaseModel):
    consent_given: bool = False
    timestamp: str = ""