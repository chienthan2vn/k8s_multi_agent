"""
Search tools for Kubernetes analysis and troubleshooting
"""
import os
import json
from typing import Dict, Any, List
from langchain_tavily import TavilySearch
from langchain.tools import tool

# Set up API key
if not os.environ.get("TAVILY_API_KEY"):
    os.environ["TAVILY_API_KEY"] = "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"

@tool
def search_k8s_docs(query: str) -> str:
    """
    Search Kubernetes documentation and best practices
    query: Search query for Kubernetes documentation
    """
    search_tool = TavilySearch(max_results=3)
    k8s_query = f"Kubernetes {query} troubleshooting documentation official"
    results = search_tool.invoke(k8s_query)
    return json.dumps(results, indent=2)

@tool  
def search_alert_solutions(alert_name: str, description: str) -> str:
    """
    Search solutions for specific alerts
    alert_name: Name of the alert
    description: Description of the alert
    """
    search_tool = TavilySearch(max_results=3)
    query = f"{alert_name} {description} kubernetes solution fix remediation"
    results = search_tool.invoke(query)
    return json.dumps(results, indent=2)

@tool
def kubectl_help(command: str) -> str:
    """
    Search information about kubectl commands
    command: The kubectl command to search for
    """
    search_tool = TavilySearch(max_results=2)
    query = f"kubectl {command} kubernetes command documentation examples usage"
    results = search_tool.invoke(query)
    return json.dumps(results, indent=2)

@tool
def search_error_patterns(error_message: str) -> str:
    """
    Search patterns and root causes of error messages
    error_message: The error message to analyze
    """
    search_tool = TavilySearch(max_results=4)
    query = f"kubernetes error '{error_message}' troubleshooting root cause"
    results = search_tool.invoke(query)
    return json.dumps(results, indent=2)

@tool
def search_performance_metrics(metric_name: str, threshold: str) -> str:
    """
    Search information about metrics and thresholds
    metric_name: Name of the performance metric
    threshold: Threshold value for the metric
    """
    search_tool = TavilySearch(max_results=3)
    query = f"kubernetes {metric_name} {threshold} performance monitoring alerting"
    results = search_tool.invoke(query)
    return json.dumps(results, indent=2)

@tool
def search_component_health(component: str) -> str:
    """
    Search information about component health checks
    component: Name of the Kubernetes component
    """
    search_tool = TavilySearch(max_results=3)
    query = f"kubernetes {component} health check monitoring troubleshooting"
    results = search_tool.invoke(query)
    return json.dumps(results, indent=2)

@tool
def analyze_alert_severity(alert_labels: str, annotations: str) -> str:
    """
    Analyze alert severity based on labels and annotations
    alert_labels: Alert labels as JSON string
    annotations: Alert annotations as JSON string
    """
    # Parse JSON strings to dictionaries
    try:
        labels_dict = json.loads(alert_labels) if isinstance(alert_labels, str) else alert_labels
    except:
        labels_dict = {}
    
    try:
        annotations_dict = json.loads(annotations) if isinstance(annotations, str) else annotations
    except:
        annotations_dict = {}
    
    severity_keywords = {
        "critical": ["down", "failed", "unavailable", "crash", "error", "critical"],
        "warning": ["high", "latency", "slow", "degraded", "warning"],
        "info": ["info", "notice", "low"]
    }
    
    # Get severity from labels
    severity = labels_dict.get("severity", "unknown").lower()
    
    # Analyze description and summary
    description = annotations_dict.get("description", "").lower()
    summary = annotations_dict.get("summary", "").lower()
    text_to_analyze = f"{description} {summary}"
    
    severity_scores = {}
    for level, keywords in severity_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text_to_analyze)
        severity_scores[level] = score
    
    # Determine severity based on analysis
    analyzed_severity = max(severity_scores, key=severity_scores.get) if any(severity_scores.values()) else "unknown"
    
    analysis_result = {
        "original_severity": severity,
        "analyzed_severity": analyzed_severity,
        "severity_scores": severity_scores,
        "confidence": max(severity_scores.values()) / len(severity_keywords[analyzed_severity]) if analyzed_severity != "unknown" else 0,
        "analysis_text": text_to_analyze[:200]  # First 200 chars
    }
    
    return json.dumps(analysis_result, indent=2)

def get_analysis_tools():
    """Return list of tools for Analyst agent"""
    return [
        search_k8s_docs, 
        search_alert_solutions, 
        kubectl_help,
        search_error_patterns,
        search_performance_metrics,
        search_component_health,
        analyze_alert_severity
    ]