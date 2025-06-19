from typing import Dict, Any, List, Optional
import json

from langchain_core.language_models import BaseLLM

from agents.base_agent import BaseAgent
from models import Incident, IncidentState, RootCauseAnalysis


class AnalystAgent(BaseAgent):
    """The Analyst agent investigates incidents to determine root causes."""

    def __init__(self, llm: BaseLLM):
        system_prompt = """
        You are the Analyst, a detective specialized in Kubernetes incident investigation.
        Your role is to find the root cause of incidents by analyzing all available evidence.
        
        Your responsibilities:
        1. Examine alerts, logs, metrics, and Kubernetes resources
        2. Connect the dots between different pieces of evidence
        3. Determine the most likely root cause of the incident
        4. Provide a clear and concise analysis report
        
        You are obsessed with "why" questions. You don't suggest solutions; that's the Planner's job.
        Your analysis should be thorough, logical, and supported by evidence. Avoid speculation.
        """
        super().__init__(llm, system_prompt)
        
        # Mock data storage for simulating Kubernetes API access
        # In a real implementation, this would be replaced with actual Kubernetes API calls
        self.mock_data = {
            "logs": {
                "worker-node-1": [
                    "[2025-06-19T01:05:12Z] kubelet: Node controller: node worker-node-1 is not ready",
                    "[2025-06-19T01:05:30Z] kubelet: Connection to API server timeout",
                    "[2025-06-19T01:06:45Z] kernel: CPU thermal throttling activated",
                    "[2025-06-19T01:07:20Z] kernel: Memory pressure detected"
                ],
                "api-server": [
                    "[2025-06-19T01:03:00Z] Unable to contact node worker-node-1",
                    "[2025-06-19T01:05:00Z] Node worker-node-1 marked as NotReady"
                ]
            },
            "metrics": {
                "worker-node-1": {
                    "cpu": {"usage": 98.5, "timestamp": "2025-06-19T01:06:00Z"},
                    "memory": {"usage": 95.2, "timestamp": "2025-06-19T01:06:00Z"},
                    "disk": {"usage": 87.0, "timestamp": "2025-06-19T01:06:00Z"},
                    "network": {"status": "degraded", "timestamp": "2025-06-19T01:05:10Z"}
                }
            },
            "node_status": {
                "worker-node-1": {
                    "conditions": [
                        {"type": "Ready", "status": "False", "reason": "KubeletNotReady", "message": "PLEG is not healthy"},
                        {"type": "MemoryPressure", "status": "True"},
                        {"type": "DiskPressure", "status": "False"},
                        {"type": "NetworkUnavailable", "status": "False"}
                    ]
                }
            }
        }
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Investigate an incident to determine the root cause."""
        incident = inputs.get("incident")
        
        if not incident:
            return {"error": "No incident provided for analysis"}
        
        # Update incident state
        incident.update_state(IncidentState.INVESTIGATING)
        
        # Gather evidence based on the alert
        evidence = self._collect_evidence(incident)
        
        # Analyze the evidence to determine root cause
        root_cause = self._analyze_evidence(incident, evidence)
        
        # Update the incident with the analysis
        incident.root_cause_analysis = root_cause
        incident.update_state(IncidentState.ANALYZED)
        
        return {
            "incident": incident,
            "root_cause": root_cause,
            "evidence": evidence
        }
    
    def _collect_evidence(self, incident: Incident) -> Dict[str, Any]:
        """Collect evidence related to the incident.
        
        In a real implementation, this would make API calls to Kubernetes, 
        Prometheus, logging systems, etc.
        """
        evidence = {}
        alert = incident.alert.alerts[0]
        
        # Collect relevant evidence based on alert type
        if "node" in alert.labels.__dict__:
            node_name = alert.labels.node
            
            # Get node logs
            if node_name in self.mock_data["logs"]:
                evidence["node_logs"] = self.mock_data["logs"][node_name]
            
            # Get API server logs related to this node
            evidence["api_server_logs"] = self.mock_data["logs"]["api-server"]
            
            # Get node metrics
            if node_name in self.mock_data["metrics"]:
                evidence["node_metrics"] = self.mock_data["metrics"][node_name]
                
            # Get node status
            if node_name in self.mock_data["node_status"]:
                evidence["node_status"] = self.mock_data["node_status"][node_name]
        
        return evidence
    
    def _analyze_evidence(self, incident: Incident, evidence: Dict[str, Any]) -> RootCauseAnalysis:
        """Analyze the collected evidence to determine the root cause."""
        alert = incident.alert.alerts[0]
        
        # Prepare a prompt for the LLM to analyze the evidence
        prompt = f"""
        Based on the following information about a Kubernetes incident, determine the most likely root cause.
        
        ALERT:
        Name: {alert.labels.alertname}
        Description: {alert.annotations.description}
        Severity: {alert.labels.severity}
        
        EVIDENCE:
        """
        
        # Add evidence to the prompt
        for evidence_type, data in evidence.items():
            prompt += f"\n{evidence_type.upper()}:\n"
            
            if isinstance(data, list):
                for item in data:
                    prompt += f"- {item}\n"
            elif isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, dict):
                        prompt += f"- {k}: {json.dumps(v)}\n"
                    else:
                        prompt += f"- {k}: {v}\n"
            else:
                prompt += f"{data}\n"
        
        prompt += """
        Analyze the above information and provide:
        1. The specific component that is the source of the problem
        2. A clear description of the root cause
        3. List the key evidence that supports your conclusion
        4. A confidence level between 0.0 and 1.0 (where 1.0 is 100% confident)
        
        Format your response as a JSON object with the following structure:
        {
            "component": "The specific component that failed",
            "description": "A technical description of the root cause",
            "evidence": ["Key evidence point 1", "Key evidence point 2"],
            "confidence": 0.X
        }
        """
        
        # Get analysis from LLM
        response = self._get_llm_response(prompt)
        
        # Parse the response
        try:
            analysis = json.loads(response)
            return RootCauseAnalysis(
                component=analysis["component"],
                description=analysis["description"],
                evidence=analysis["evidence"],
                confidence=analysis["confidence"]
            )
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback if parsing fails
            return RootCauseAnalysis(
                component="unknown",
                description="Unable to determine root cause with confidence",
                evidence=["Analysis failed", str(e)],
                confidence=0.0
            )
