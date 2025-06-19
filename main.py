from typing import Dict, Any, List, Tuple, Annotated, TypedDict
import os
import json
import uuid
from datetime import datetime

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import tool
from langgraph.graph import StateGraph, END

from config import config
from models import Incident, IncidentState, AlertGroup
from agents.orchestrator_agent import OrchestratorAgent
from agents.analyst_agent import AnalystAgent
from agents.planner_agent import PlannerAgent
from agents.executor_agent import ExecutorAgent
from mcp_client import MCPClient


class IncidentState(TypedDict):
    """State for the incident workflow graph."""
    incident: Incident
    action: str
    agent: str
    error: str
    approved: bool
    plan_index: int
    feedback: str
    execution_complete: bool
    success: bool
    summary: str


def create_llm():
    """Create a language model instance."""
    settings = config.get_llm_settings()
    
    # Use the Gemini API via the OpenAI client
    return ChatOpenAI(
        api_key=settings["api_key"],
        base_url=settings["base_url"],
        temperature=settings["temperature"],
        model="gemini-pro"  # This is ignored but required by the OpenAI client
    )


def create_k8s_incident_graph() -> StateGraph:
    """Create the incident management workflow graph."""
    # Initialize the LLM and agents
    llm = create_llm()
    
    orchestrator = OrchestratorAgent(llm)
    analyst = AnalystAgent(llm)
    planner = PlannerAgent(llm)
    executor = ExecutorAgent(llm)
    
    # Define the graph
    workflow = StateGraph(IncidentState)
    
    # Add nodes for each agent
    workflow.add_node("orchestrator", lambda state: orchestrator_node(orchestrator, state))
    workflow.add_node("analyst", lambda state: analyst_node(analyst, state))
    workflow.add_node("planner", lambda state: planner_node(planner, state))
    workflow.add_node("human_approval", human_approval_node)
    workflow.add_node("executor", lambda state: executor_node(executor, state))
    
    # Define the edges
    workflow.add_edge("orchestrator", "analyst", should_investigate)
    workflow.add_edge("analyst", "orchestrator", lambda _: True)
    workflow.add_edge("orchestrator", "planner", should_plan)
    workflow.add_edge("planner", "orchestrator", lambda _: True)
    workflow.add_edge("orchestrator", "human_approval", should_approve)
    workflow.add_edge("human_approval", "orchestrator", lambda _: True)
    workflow.add_edge("orchestrator", "executor", should_execute)
    workflow.add_edge("executor", "orchestrator", lambda _: True)
    
    # Add conditional end states
    workflow.add_conditional_edges(
        "orchestrator",
        is_incident_resolved,
        {
            True: END,
            False: "orchestrator"
        }
    )
    
    # Set the entry point
    workflow.set_entry_point("orchestrator")
    
    return workflow


# Node functions

def orchestrator_node(agent: OrchestratorAgent, state: IncidentState) -> IncidentState:
    """Process the current state using the orchestrator agent."""
    print(f"[Orchestrator] Processing incident in state: {state.get('incident', {}).get('state', 'UNKNOWN')}")
    
    result = agent.run(state)
    
    return {
        **state,
        **result
    }


def analyst_node(agent: AnalystAgent, state: IncidentState) -> IncidentState:
    """Analyze the incident using the analyst agent."""
    print(f"[Analyst] Investigating incident: {state['incident'].id}")
    
    result = agent.run(state)
    
    return {
        **state,
        **result,
        "agent": "orchestrator"  # Return control to orchestrator
    }


def planner_node(agent: PlannerAgent, state: IncidentState) -> IncidentState:
    """Create remediation plans using the planner agent."""
    print(f"[Planner] Creating remediation plan for incident: {state['incident'].id}")
    
    result = agent.run(state)
    
    return {
        **state,
        **result,
        "agent": "orchestrator"  # Return control to orchestrator
    }


def human_approval_node(state: IncidentState) -> IncidentState:
    """Simulate human approval of remediation plans."""
    incident = state["incident"]
    print(f"[Human] Reviewing remediation plans for incident: {incident.id}")
    
    # In a real system, this would pause execution and wait for human input
    # For now, we'll simulate automatic approval of the first plan
    
    # Get approval request if it exists
    approval_request = state.get("approval_request", "")
    if approval_request:
        print(f"\n{approval_request}\n")
    
    # Print available plans
    print("\nAvailable remediation plans:")
    for i, plan in enumerate(incident.remediation_plans):
        print(f"Plan #{i+1}: {plan.title}")
        print(f"Description: {plan.description}")
        print(f"Impact: {plan.impact_assessment}")
        print(f"Steps: {len(plan.steps)}")
        print()
    
    # Simulate human input
    print("Simulating human approval of the first plan...")
    approved = True
    plan_index = 0
    feedback = ""
    
    return {
        **state,
        "agent": "orchestrator",
        "approved": approved,
        "plan_index": plan_index,
        "feedback": feedback
    }


def executor_node(agent: ExecutorAgent, state: IncidentState) -> IncidentState:
    """Execute remediation plan using the executor agent."""
    print(f"[Executor] Executing remediation plan for incident: {state['incident'].id}")
    
    result = agent.run(state)
    
    return {
        **state,
        **result,
        "agent": "orchestrator"  # Return control to orchestrator
    }


# Edge condition functions

def should_investigate(state: IncidentState) -> bool:
    """Check if the incident needs investigation."""
    return state.get("next_step") == "investigate" and state.get("agent") == "analyst"


def should_plan(state: IncidentState) -> bool:
    """Check if remediation planning is needed."""
    return state.get("next_step") == "plan" and state.get("agent") == "planner"


def should_approve(state: IncidentState) -> bool:
    """Check if human approval is needed."""
    incident = state.get("incident")
    return (
        incident and
        incident.state == IncidentState.APPROVAL_PENDING and
        incident.remediation_plans and
        len(incident.remediation_plans) > 0
    )


def should_execute(state: IncidentState) -> bool:
    """Check if plan execution is needed."""
    return state.get("next_step") == "execute" and state.get("agent") == "executor"


def is_incident_resolved(state: IncidentState) -> bool:
    """Check if the incident is resolved or failed."""
    incident = state.get("incident")
    if not incident:
        return False
        
    return incident.state in [IncidentState.RESOLVED, IncidentState.FAILED]


# Utility functions for the main workflow

def load_alert_from_file(file_path: str) -> Dict[str, Any]:
    """Load an alert from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def process_incident(alert_data: Dict[str, Any]) -> Incident:
    """Process an incident through the entire workflow."""
    # Initialize the graph
    workflow = create_k8s_incident_graph()
    
    # Create a compiled graph for execution
    app = workflow.compile()
    
    # Initialize the state with the alert
    state = {
        "incident": None,
        "action": "create_incident",
        "agent": "orchestrator",
        "error": "",
        "alert_data": alert_data,
        "approved": False,
        "plan_index": 0,
        "feedback": "",
        "execution_complete": False,
        "success": False,
        "summary": ""
    }
    
    # Execute the workflow
    for output in app.stream(state):
        # The workflow streams each state transition
        current_state = output.values[0]
        
        # Check for errors
        if current_state.get("error"):
            print(f"Error: {current_state['error']}")
    
    # Return the final incident
    final_state = output.values[0]
    return final_state.get("incident")


def main():
    """Main entry point for the application."""
    # Check for command line arguments
    import sys
    
    if len(sys.argv) > 1:
        # Use provided alert file
        alert_file = sys.argv[1]
    else:
        # Use default alert file
        alert_file = "examples/alerts/node-down.json"
    
    print(f"Processing alert from file: {alert_file}")
    
    # Load the alert
    alert_data = load_alert_from_file(alert_file)
    
    # Process the incident
    incident = process_incident(alert_data)
    
    # Print the final summary
    print("\n" + "="*80)
    print(f"Incident {incident.id} - Final State: {incident.state}")
    
    if incident.resolution_summary:
        print("\nResolution Summary:")
        print(incident.resolution_summary)
        
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
