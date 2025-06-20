from typing import Dict, Any, List
import subprocess
import json
import time

from langchain_core.language_models import BaseLLM

from agents.base_agent import BaseAgent
from models import Incident, IncidentState, RemediationPlan, ExecutionResult


class ExecutorAgent(BaseAgent):
    """The Executor agent implements remediation plans safely and precisely."""

    def __init__(self, llm: BaseLLM):
        system_prompt = """
        You are the Executor, a deployment specialist for Kubernetes incident remediation.
        Your role is to implement approved remediation plans with precision and care.
        
        Your responsibilities:
        1. Execute commands from approved remediation plans
        2. Monitor the outcomes of each step
        3. Verify that the remediation has resolved the incident
        4. Report on the execution results
        
        You only execute actions that have been explicitly approved by human operators.
        Safety is your top priority - carefully validate each command before execution and
        be prepared to stop if unexpected issues arise.
        """
        super().__init__(llm, system_prompt)
        
        # Flag to control whether commands are actually executed
        # In production, this would be True
        self.execute_commands = False
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an approved remediation plan."""
        incident = inputs.get("incident")
        
        if not incident:
            return {"error": "No incident provided for execution"}
        
        if incident.approved_plan_index is None:
            return {"error": "No approved plan available for execution"}
        
        # Update incident state
        incident.update_state(IncidentState.EXECUTING)
        
        # Get the approved plan
        plan_index = incident.approved_plan_index
        if plan_index >= len(incident.remediation_plans):
            return {"error": f"Invalid plan index: {plan_index}"}
        
        plan = incident.remediation_plans[plan_index]
        
        # Execute each step in the plan
        execution_results = []
        overall_success = True
        
        for i, step in enumerate(plan.steps):
            result = self._execute_step(step, i)
            execution_results.append(result)
            incident.execution_results.append(result)
            
            if not result.success:
                overall_success = False
                break
        
        # Verify the resolution if all steps were successful
        resolution_verified = False
        verification_output = ""
        
        if overall_success:
            resolution_verified, verification_output = self._verify_resolution(incident)
            overall_success = resolution_verified
        
        # Create a summary of the execution
        summary = self._create_execution_summary(incident, execution_results, resolution_verified, verification_output)
        
        return {
            "incident": incident,
            "execution_results": execution_results,
            "success": overall_success,
            "summary": summary,
            "execution_complete": True
        }
    
    def _execute_step(self, step, step_index: int) -> ExecutionResult:
        """Execute a single step from the remediation plan."""
        print(f"Executing step {step_index + 1}: {step.description}")
        
        if not step.command:
            # If there's no command, mark as successful (might be a manual step)
            return ExecutionResult(
                step_index=step_index,
                step_description=step.description,
                command=None,
                success=True,
                output="No command to execute - marked as completed",
                error=None
            )
        
        print(f"Command: {step.command}")
        
        try:
            # Only execute if allowed, otherwise simulate
            if self.execute_commands:
                # Execute the command
                result = subprocess.run(
                    step.command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5-minute timeout
                )
                
                success = result.returncode == 0
                output = result.stdout
                error = result.stderr if result.stderr else None
                
            else:
                # Simulate execution
                print("[SIMULATED] Command would be executed here")
                time.sleep(1)  # Simulate some execution time
                success = True
                output = f"[SIMULATED] Command executed successfully: {step.command}"
                error = None
            
            return ExecutionResult(
                step_index=step_index,
                step_description=step.description,
                command=step.command,
                success=success,
                output=output,
                error=error
            )
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                step_index=step_index,
                step_description=step.description,
                command=step.command,
                success=False,
                output="",
                error="Command timed out after 5 minutes"
            )
        except Exception as e:
            return ExecutionResult(
                step_index=step_index,
                step_description=step.description,
                command=step.command,
                success=False,
                output="",
                error=str(e)
            )
    
    def _verify_resolution(self, incident: Incident) -> tuple[bool, str]:
        """Verify that the incident has been resolved."""
        # In a real implementation, this would check the alert source
        # to confirm the alert is no longer firing
        
        alert = incident.alert.alerts[0]
        alert_name = alert.labels.alertname
        
        print(f"Verifying resolution for alert: {alert_name}")
        
        # Simulate verification based on alert type
        if alert_name == "KubeNodeNotReady" and "node" in alert.labels.__dict__:
            node_name = alert.labels.node
            
            # Simulate checking node status
            if self.execute_commands:
                try:
                    result = subprocess.run(
                        f"kubectl get node {node_name} -o jsonpath='{{.status.conditions[?(@.type==\"Ready\")].status}}'",
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0 and result.stdout.strip() == "True":
                        return True, f"Node {node_name} is now Ready"
                    else:
                        return False, f"Node {node_name} is still NotReady: {result.stderr}"
                except Exception as e:
                    return False, f"Failed to verify node status: {str(e)}"
            else:
                # Simulate successful verification
                return True, f"[SIMULATED] Node {node_name} is now Ready"
        
        # Generic verification for other alert types
        return True, f"[SIMULATED] Alert {alert_name} is no longer firing"
    
    def _create_execution_summary(
        self, 
        incident: Incident, 
        execution_results: List[ExecutionResult],
        resolution_verified: bool,
        verification_output: str
    ) -> str:
        """Create a summary of the execution results."""
        alert = incident.alert.alerts[0]
        plan = incident.remediation_plans[incident.approved_plan_index]
        
        # Create a prompt for the LLM to generate a summary
        prompt = f"""
        Create a concise summary of the execution of a Kubernetes incident remediation plan.
        
        INCIDENT:
        ID: {incident.id}
        Alert: {alert.labels.alertname}
        Description: {alert.annotations.description}
        
        REMEDIATION PLAN:
        Title: {plan.title}
        
        EXECUTION RESULTS:
        """
        
        for result in execution_results:
            status = "✅ Success" if result.success else "❌ Failed"
            prompt += f"\nStep {result.step_index + 1}: {status} - {result.step_description}"
            if not result.success and result.error:
                prompt += f"\n   Error: {result.error}"
        
        prompt += f"\n\nVERIFICATION: {'✅ Resolved' if resolution_verified else '❌ Not resolved'}"
        prompt += f"\n{verification_output}"
        
        prompt += """
        Please provide a concise summary (3-5 sentences) that:
        1. States whether the remediation was successful or not
        2. Highlights key steps that were performed
        3. Mentions any issues encountered
        4. Confirms whether the original alert condition has been resolved
        
        Write this as a concise technical report for an operations team.
        """
        
        # Get summary from LLM
        return self._get_llm_response(prompt)
