from typing import Dict, Any, List
import json

from langchain_core.language_models import BaseLLM

from agents.base_agent import BaseAgent
from models import Incident, IncidentState, RemediationPlan, RemediationStep


class PlannerAgent(BaseAgent):
    """The Planner agent creates remediation plans based on root cause analysis."""

    def __init__(self, llm: BaseLLM):
        system_prompt = """
        You are the Planner, a strategic thinker specialized in Kubernetes remediation.
        Your role is to develop detailed, safe remediation plans for Kubernetes incidents.
        
        Your responsibilities:
        1. Understand the root cause identified by the Analyst
        2. Develop one or more specific remediation plans
        3. Detail each step that must be taken to resolve the issue
        4. Evaluate risks and provide rollback options
        
        Your plans must be detailed enough that they can be executed without additional context.
        Include specific kubectl commands or other commands that would be needed.
        Always consider the risk level and potential side effects of your recommendations.
        """
        super().__init__(llm, system_prompt)
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Create remediation plans for an incident."""
        incident = inputs.get("incident")
        
        if not incident:
            return {"error": "No incident provided for planning"}
        
        if not incident.root_cause_analysis:
            return {"error": "No root cause analysis available for planning"}
        
        # Update incident state
        incident.update_state(IncidentState.PLANNING)
        
        # Generate remediation plans
        feedback = inputs.get("feedback", "")
        plans = self._generate_remediation_plans(incident, feedback)
        
        # Update the incident with the plans
        incident.remediation_plans = plans
        
        return {
            "incident": incident,
            "remediation_plans": plans
        }
    
    def _generate_remediation_plans(self, incident: Incident, feedback: str = "") -> List[RemediationPlan]:
        """Generate one or more remediation plans for the incident."""
        alert = incident.alert.alerts[0]
        root_cause = incident.root_cause_analysis
        
        # Prepare a prompt for the LLM to generate remediation plans
        prompt = f"""
        Based on the following information about a Kubernetes incident, create detailed remediation plans.
        
        ALERT:
        Name: {alert.labels.alertname}
        Description: {alert.annotations.description}
        Severity: {alert.labels.severity}
        
        ROOT CAUSE ANALYSIS:
        Component: {root_cause.component}
        Description: {root_cause.description}
        Evidence: {', '.join(root_cause.evidence)}
        Confidence: {root_cause.confidence}
        
        {f'FEEDBACK FROM PREVIOUS PLAN: {feedback}' if feedback else ''}
        
        Generate 1-2 remediation plans that address the root cause of this incident.
        Each plan should include:
        
        1. A title and description of the approach
        2. An assessment of the potential impact
        3. A detailed list of steps with commands to execute
        4. Estimated time to implement
        5. A rollback plan in case of failure
        
        Format your response as a JSON array with the following structure:
        [
            {{
                "title": "Plan Title",
                "description": "Description of the approach",
                "impact_assessment": "Assessment of potential impact",
                "estimated_time": "Estimated implementation time (e.g., '5 minutes')",
                "steps": [
                    {{
                        "description": "Step description",
                        "command": "command to execute (if applicable)",
                        "expected_outcome": "What should happen after this step",
                        "risk_level": "low/medium/high"
                    }}
                ],
                "rollback_plan": [
                    {{
                        "description": "Rollback step",
                        "command": "command to execute",
                        "expected_outcome": "Expected outcome",
                        "risk_level": "low/medium/high"
                    }}
                ]
            }}
        ]
        """
        
        # Get remediation plans from LLM
        response = self._get_llm_response(prompt)
        
        # Parse the response
        try:
            plans_data = json.loads(response)
            
            plans = []
            for plan_data in plans_data:
                steps = [
                    RemediationStep(**step)
                    for step in plan_data.pop("steps", [])
                ]
                
                rollback_steps = None
                if "rollback_plan" in plan_data:
                    rollback_steps = [
                        RemediationStep(**step)
                        for step in plan_data.pop("rollback_plan", [])
                    ]
                
                plan = RemediationPlan(
                    **plan_data,
                    steps=steps,
                    rollback_plan=rollback_steps
                )
                plans.append(plan)
            
            return plans
            
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback if parsing fails
            step = RemediationStep(
                description="Contact Kubernetes administrator for manual intervention",
                command=None,
                expected_outcome="Manual resolution of the issue",
                risk_level="low"
            )
            
            fallback_plan = RemediationPlan(
                title="Fallback Plan: Manual Intervention",
                description="Automated planning failed. Manual intervention required.",
                impact_assessment="Unknown, requires human assessment",
                steps=[step],
                estimated_time="Unknown, depends on human availability",
                rollback_plan=None
            )
            
            return [fallback_plan]
