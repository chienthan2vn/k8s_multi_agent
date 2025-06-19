import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from langchain_core.language_models import BaseLLM

from agents.base_agent import BaseAgent
from models import Incident, IncidentState, AlertGroup, RemediationPlan


class OrchestratorAgent(BaseAgent):
    """The Orchestrator agent manages the overall incident resolution workflow."""

    def __init__(self, llm: BaseLLM):
        system_prompt = """
        You are the Orchestrator, the project manager of a Kubernetes incident response team.
        Your role is to manage the workflow of incident resolution by delegating tasks to specialist agents
        and making decisions about the next steps to take.
        
        Your responsibilities:
        1. Receive alert notifications and create incidents
        2. Delegate investigation to the Analyst agent
        3. Request remediation plans from the Planner agent
        4. Present plans to human operators for approval
        5. Instruct the Executor agent to implement approved plans
        6. Track and report on the status of incidents
        
        You do not perform technical analysis or create remediation plans yourself.
        You are an expert at workflow management, clear communication, and knowing when to involve each specialist.
        """
        super().__init__(llm, system_prompt)
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process the current state and determine the next actions."""
        incident = inputs.get("incident")
        action = inputs.get("action", "process")
        
        if action == "create_incident" and not incident:
            return self._create_incident(inputs["alert_data"])
        
        if not incident:
            return {"error": "No incident provided for processing"}
        
        # Handle different incident states
        if incident.state == IncidentState.RECEIVED:
            return {"next_step": "investigate", "agent": "analyst", "incident": incident}
        
        elif incident.state == IncidentState.ANALYZED:
            return {"next_step": "plan", "agent": "planner", "incident": incident}
        
        elif incident.state == IncidentState.PLANNING:
            # Need human approval for the plan
            incident.update_state(IncidentState.APPROVAL_PENDING)
            return self._generate_approval_request(incident)
        
        elif incident.state == IncidentState.APPROVAL_PENDING:
            if inputs.get("approved"):
                incident.approved_plan_index = inputs.get("plan_index", 0)
                return {"next_step": "execute", "agent": "executor", "incident": incident}
            else:
                # Plan rejected, go back to planning with feedback
                incident.update_state(IncidentState.PLANNING)
                return {"next_step": "plan", "agent": "planner", "incident": incident, "feedback": inputs.get("feedback", "")}
        
        elif incident.state == IncidentState.EXECUTING:
            # If execution is complete, update the incident state
            if inputs.get("execution_complete"):
                if inputs.get("success"):
                    incident.update_state(IncidentState.RESOLVED)
                    incident.resolution_summary = inputs.get("summary", "Incident resolved successfully.")
                else:
                    incident.update_state(IncidentState.FAILED)
                    incident.resolution_summary = inputs.get("summary", "Incident resolution failed.")
            
            return {"incident": incident}
        
        # Default response for other states
        return {"incident": incident}
    
    def _create_incident(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new incident from an alert."""
        try:
            # Parse alert data
            if isinstance(alert_data, str):
                alert_data = json.loads(alert_data)
                
            alert_group = AlertGroup.model_validate(alert_data)
            
            # Create a new incident
            incident_id = f"INC-{uuid.uuid4().hex[:8]}"
            now = datetime.now()
            
            incident = Incident(
                id=incident_id,
                state=IncidentState.RECEIVED,
                alert=alert_group,
                creation_time=now,
                last_updated=now
            )
            
            return {
                "incident": incident,
                "message": f"Created new incident {incident_id} for alert {alert_group.alerts[0].labels.alertname}"
            }
            
        except Exception as e:
            return {"error": f"Failed to create incident: {str(e)}"}
    
    def _generate_approval_request(self, incident: Incident) -> Dict[str, Any]:
        """Generate a human-friendly approval request for remediation plans."""
        if not incident.remediation_plans:
            return {
                "incident": incident,
                "error": "No remediation plans available for approval"
            }
        
        # Format the plans for human review
        alert = incident.alert.alerts[0]
        
        prompt = f"""
        You need to create a clear, concise approval request for human operators.
        
        INCIDENT DETAILS:
        ID: {incident.id}
        Alert: {alert.labels.alertname}
        Description: {alert.annotations.description}
        Component: {incident.root_cause_analysis.component if incident.root_cause_analysis else "Unknown"}
        
        ROOT CAUSE:
        {incident.root_cause_analysis.description if incident.root_cause_analysis else "Not determined"}
        
        PROPOSED REMEDIATION PLAN(S):
        """
        
        for i, plan in enumerate(incident.remediation_plans):
            prompt += f"""
            PLAN #{i+1}: {plan.title}
            Description: {plan.description}
            Impact: {plan.impact_assessment}
            Estimated time: {plan.estimated_time}
            Risk level: {plan.steps[0].risk_level if plan.steps else "Unknown"}
            
            Steps:
            """
            
            for j, step in enumerate(plan.steps):
                prompt += f"  {j+1}. {step.description}"
                if step.command:
                    prompt += f" (Command: {step.command})"
                prompt += "\n"
        
        approval_message = self._get_llm_response(prompt)
        
        return {
            "incident": incident,
            "approval_request": approval_message,
            "plans": incident.remediation_plans
        }
