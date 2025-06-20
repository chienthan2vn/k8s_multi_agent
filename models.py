from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from enum import Enum


class AlertStatus(str, Enum):
    FIRING = "firing"
    RESOLVED = "resolved"
    

class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AlertLabels(BaseModel):
    alertname: str
    severity: AlertSeverity
    node: Optional[str] = None
    namespace: Optional[str] = None
    pod: Optional[str] = None
    container: Optional[str] = None
    service: Optional[str] = None
    deployment: Optional[str] = None
    
    def __getitem__(self, key):
        return getattr(self, key)


class AlertAnnotations(BaseModel):
    summary: str
    description: str


class Alert(BaseModel):
    status: AlertStatus
    labels: AlertLabels
    annotations: AlertAnnotations
    startsAt: datetime
    endsAt: Optional[datetime] = None
    generatorURL: str


class AlertGroup(BaseModel):
    receiver: str
    status: AlertStatus
    alerts: List[Alert]
    groupLabels: Dict[str, str] = Field(default_factory=dict)


class IncidentState(str, Enum):
    RECEIVED = "received"
    INVESTIGATING = "investigating"
    ANALYZED = "analyzed"
    PLANNING = "planning"
    APPROVAL_PENDING = "approval_pending"
    EXECUTING = "executing"
    RESOLVED = "resolved"
    FAILED = "failed"


class RootCauseAnalysis(BaseModel):
    component: str
    description: str
    evidence: List[str]
    confidence: float = Field(ge=0.0, le=1.0)


class RemediationStep(BaseModel):
    description: str
    command: Optional[str] = None
    expected_outcome: str
    risk_level: Literal["low", "medium", "high"]


class RemediationPlan(BaseModel):
    title: str
    description: str
    impact_assessment: str
    steps: List[RemediationStep]
    estimated_time: str
    rollback_plan: Optional[List[RemediationStep]] = None


class ExecutionResult(BaseModel):
    step_index: int
    step_description: str
    command: Optional[str] = None
    success: bool
    output: str
    error: Optional[str] = None


class Incident(BaseModel):
    id: str
    state: IncidentState
    alert: AlertGroup
    creation_time: datetime
    last_updated: datetime
    root_cause_analysis: Optional[RootCauseAnalysis] = None
    remediation_plans: List[RemediationPlan] = Field(default_factory=list)
    approved_plan_index: Optional[int] = None
    execution_results: List[ExecutionResult] = Field(default_factory=list)
    resolution_summary: Optional[str] = None
    
    def update_state(self, new_state: IncidentState):
        self.state = new_state
        self.last_updated = datetime.now()
