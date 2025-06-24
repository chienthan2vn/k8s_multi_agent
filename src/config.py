"""
Cấu hình hệ thống multi-agent
"""
import os
from typing import Dict, Any

# Cấu hình LLM
LLM_CONFIG = {
    "model": "gemini-2.0-flash",
    "temperature": 0.6,
    "max_tokens": 4000
}

# Cấu hình API Keys
GOOGLE_API_KEY = os.getenv("AIzaSyDgAlnEdV-wwLc41VtAvD3p4NvmmVrJIro")
TAVILY_API_KEY = os.getenv("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")

# Cấu hình agents
AGENT_CONFIG = {
    "max_iterations": 5,
    "verbose": True
}

# State schema cho workflow
class AgentState:
    """State chung cho tất cả agents"""
    def __init__(self):
        self.alert_data: Dict[str, Any] = {}
        self.analysis_result: str = ""
        self.plan_suggestions: list = []
        self.selected_plan: Dict[str, Any] = {}
        self.execution_result: str = ""
        self.final_response: str = ""
        self.current_step: str = "received"
        self.messages: list = []
