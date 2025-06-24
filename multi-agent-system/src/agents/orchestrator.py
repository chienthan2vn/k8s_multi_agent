"""
Orchestrator Agent - Trưởng nhóm / Bác sĩ Trực
"""
import os
import sys
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.prompts.prompt_orchestrator import ORCHESTRATOR_SYSTEM_PROMPT, ORCHESTRATOR_SUMMARY_PROMPT
from src.config import LLM_CONFIG

def create_orchestrator_llm():
    """Tạo LLM cho orchestrator"""
    return ChatGoogleGenerativeAI(
        model=LLM_CONFIG["model"],
        temperature=0.3,  # Moderate temperature cho creative summary
        max_output_tokens=LLM_CONFIG["max_tokens"]
    )

def run_orchestrator_summary(
    alert_data: dict,
    analysis_result: dict = None,
    plan_suggestions: dict = None, 
    execution_result: dict = None,
    current_step: str = "completed"
) -> str:
    """Tạo báo cáo tổng hợp từ orchestrator"""
    
    llm = create_orchestrator_llm()
    
    # Chuẩn bị dữ liệu cho prompt
    prompt_data = {
        "alert_data": json.dumps(alert_data, indent=2, ensure_ascii=False),
        "analysis_result": json.dumps(analysis_result, indent=2, ensure_ascii=False) if analysis_result else "Chưa thực hiện",
        "plan_suggestions": json.dumps(plan_suggestions, indent=2, ensure_ascii=False) if plan_suggestions else "Chưa có kế hoạch",
        "execution_result": json.dumps(execution_result, indent=2, ensure_ascii=False) if execution_result else "Chưa thực thi",
        "current_step": current_step
    }
    
    # Tạo messages
    messages = [
        SystemMessage(content=ORCHESTRATOR_SYSTEM_PROMPT),
        HumanMessage(content=ORCHESTRATOR_SUMMARY_PROMPT.format(**prompt_data))
    ]
    
    # Gọi LLM
    response = llm.invoke(messages)
    
    return response.content

def create_incident_report(
    alert_data: dict,
    analysis_result: dict,
    plan_suggestions: dict,
    execution_result: dict = None
) -> dict:
    """Tạo báo cáo sự cố hoàn chỉnh"""
    
    # Tạo summary từ orchestrator
    summary = run_orchestrator_summary(
        alert_data=alert_data,
        analysis_result=analysis_result,
        plan_suggestions=plan_suggestions,
        execution_result=execution_result,
        current_step="plan_ready" if not execution_result else "completed"
    )
    
    # Tạo structured report
    report = {
        "incident_id": f"INC-{alert_data.get('alerts', [{}])[0].get('labels', {}).get('alertname', 'unknown')}",
        "timestamp": alert_data.get('alerts', [{}])[0].get('startsAt', 'unknown'),
        "alert_summary": {
            "name": alert_data.get('alerts', [{}])[0].get('labels', {}).get('alertname'),
            "severity": alert_data.get('alerts', [{}])[0].get('labels', {}).get('severity'),
            "description": alert_data.get('alerts', [{}])[0].get('annotations', {}).get('description')
        },
        "diagnosis": analysis_result,
        "remediation_plan": plan_suggestions,
        "execution_result": execution_result,
        "orchestrator_summary": summary,
        "status": "plan_ready" if not execution_result else "resolved"
    }
    
    return report
