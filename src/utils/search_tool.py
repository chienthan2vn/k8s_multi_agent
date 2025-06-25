"""
Công cụ tìm kiếm cho việc phân tích và chẩn đoán sự cố Kubernetes
"""

import os
import json
from langchain_tavily import TavilySearch
from langchain.tools import tool

# Thiết lập API key
if not os.environ.get("TAVILY_API_KEY"):
    os.environ["TAVILY_API_KEY"] = "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"


@tool
def search_k8s_docs(query: str) -> str:
    """Tìm kiếm tài liệu Kubernetes và best practices"""
    search_tool = TavilySearch(max_results=3)
    k8s_query = f"Kubernetes {query} troubleshooting documentation official"
    results = search_tool.invoke(k8s_query)
    return json.dumps(results, indent=2)


@tool
def search_alert_solutions(alert_name: str, description: str) -> str:
    """Tìm kiếm giải pháp cho alert cụ thể"""
    search_tool = TavilySearch(max_results=3)
    query = f"{alert_name} {description} kubernetes solution fix remediation"
    results = search_tool.invoke(query)
    return json.dumps(results, indent=2)


@tool
def kubectl_help(command: str) -> str:
    """Tìm kiếm thông tin về lệnh kubectl"""
    search_tool = TavilySearch(max_results=2)
    query = f"kubectl {command} kubernetes command documentation examples usage"
    results = search_tool.invoke(query)
    return json.dumps(results, indent=2)


@tool
def search_error_patterns(error_message: str) -> str:
    """Tìm kiếm patterns và nguyên nhân của error message"""
    search_tool = TavilySearch(max_results=4)
    query = f"kubernetes error '{error_message}' troubleshooting root cause"
    results = search_tool.invoke(query)
    return json.dumps(results, indent=2)


@tool
def search_performance_metrics(metric_name: str, threshold: str) -> str:
    """Tìm kiếm thông tin về metrics và threshold"""
    search_tool = TavilySearch(max_results=3)
    query = f"kubernetes {metric_name} {threshold} performance monitoring alerting"
    results = search_tool.invoke(query)
    return json.dumps(results, indent=2)


@tool
def search_component_health(component: str) -> str:
    """Tìm kiếm thông tin về health check của component"""
    search_tool = TavilySearch(max_results=3)
    query = f"kubernetes {component} health check monitoring troubleshooting"
    results = search_tool.invoke(query)
    return json.dumps(results, indent=2)


@tool
def analyze_alert_severity(alert_labels: dict, annotations: dict) -> str:
    """Phân tích mức độ nghiêm trọng của alert dựa trên labels và annotations"""

    severity_keywords = {
        "critical": ["down", "failed", "unavailable", "crash", "error", "critical"],
        "warning": ["high", "latency", "slow", "degraded", "warning"],
        "info": ["info", "notice", "low"],
    }

    # Lấy severity từ labels
    severity = alert_labels.get("severity", "unknown").lower()

    # Phân tích description và summary
    description = annotations.get("description", "").lower()
    summary = annotations.get("summary", "").lower()
    text_to_analyze = f"{description} {summary}"

    severity_scores = {}
    for level, keywords in severity_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text_to_analyze)
        severity_scores[level] = score

    # Xác định severity dựa trên analysis
    analyzed_severity = (
        max(severity_scores, key=severity_scores.get)
        if any(severity_scores.values())
        else "unknown"
    )

    analysis_result = {
        "original_severity": severity,
        "analyzed_severity": analyzed_severity,
        "severity_scores": severity_scores,
        "confidence": max(severity_scores.values())
        / len(severity_keywords[analyzed_severity])
        if analyzed_severity != "unknown"
        else 0,
        "analysis_text": text_to_analyze[:200],  # First 200 chars
    }

    return json.dumps(analysis_result, indent=2)


def get_analysis_tools():
    """Trả về danh sách tools cho Analyst agent"""
    return [
        search_k8s_docs,
        search_alert_solutions,
        kubectl_help,
        search_error_patterns,
        search_performance_metrics,
        search_component_health,
        analyze_alert_severity,
    ]
