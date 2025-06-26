"""
Tools for Executor Agent - Execution and simulation tools
"""
from langchain.tools import tool
import json
import uuid
from datetime import datetime

@tool
def simulate_kubectl_command(command: str) -> str:
    """
    Simulate kubectl command execution (simulation mode)
    command: The kubectl command to simulate
    """
    timestamp = datetime.now().isoformat()
    
    # Simulation results based on command type
    simulation_results = {
        "get pods": {
            "status": "success",
            "output": "NAME                    READY   STATUS    RESTARTS   AGE\nnginx-deployment-xxx   1/1     Running   0          5m",
            "execution_time": "0.5s"
        },
        "get nodes": {
            "status": "success", 
            "output": "NAME       STATUS   ROLES    AGE   VERSION\nnode-1     Ready    master   10d   v1.28.0",
            "execution_time": "0.3s"
        },
        "describe": {
            "status": "success",
            "output": "Resource description retrieved successfully",
            "execution_time": "1.2s"
        },
        "logs": {
            "status": "success",
            "output": "Application logs retrieved successfully",
            "execution_time": "2.1s"
        },
        "delete": {
            "status": "success",
            "output": "Resource deleted successfully",
            "execution_time": "3.5s"
        },
        "restart": {
            "status": "success",
            "output": "Restart operation completed successfully",
            "execution_time": "25.0s"
        },
        "scale": {
            "status": "success", 
            "output": "Scaling operation completed successfully",
            "execution_time": "12.3s"
        },
        "patch": {
            "status": "success",
            "output": "Patch applied successfully",
            "execution_time": "8.7s"
        },
        "drain": {
            "status": "success",
            "output": "Node drained successfully, pods evicted",
            "execution_time": "45.2s"
        },
        "cordon": {
            "status": "success",
            "output": "Node cordoned successfully",
            "execution_time": "2.1s"
        },
        "uncordon": {
            "status": "success",
            "output": "Node uncordoned successfully",
            "execution_time": "1.8s"
        }
    }
    
    # Find matching command pattern
    result = None
    for pattern, sim_result in simulation_results.items():
        if pattern in command.lower():
            result = sim_result
            break
    
    if not result:
        result = {
            "status": "unknown",
            "output": "Command pattern not recognized in simulation",
            "execution_time": "N/A"
        }
    
    execution_log = {
        "command": command,
        "timestamp": timestamp,
        "simulation_result": result,
        "execution_id": str(uuid.uuid4())[:8]
    }
    
    return json.dumps(execution_log, indent=2)

@tool
def verify_system_state(check_description: str, expected_state: str = "") -> str:
    """
    Check system state after executing action
    check_description: Description of what to check
    expected_state: Expected state after the action (optional)
    """
    timestamp = datetime.now().isoformat()
    
    # Simulation of verification checks
    verification_results = {
        "pod status": {
            "status": "healthy",
            "details": "All pods are running and ready",
            "check_time": "2.1s"
        },
        "node status": {
            "status": "healthy", 
            "details": "Node is ready and schedulable",
            "check_time": "1.5s"
        },
        "deployment status": {
            "status": "healthy",
            "details": "Deployment is available with desired replicas",
            "check_time": "3.2s"
        },
        "service status": {
            "status": "healthy",
            "details": "Service endpoints are ready",
            "check_time": "1.8s"
        },
        "resource utilization": {
            "status": "normal",
            "details": "CPU and memory usage within normal ranges",
            "check_time": "4.5s"
        }
    }
    
    # Find matching verification
    result = None
    for check_type, verify_result in verification_results.items():
        if check_type in check_description.lower():
            result = verify_result
            break
    
    if not result:
        result = {
            "status": "verified",
            "details": f"System state check completed: {check_description}",
            "check_time": "2.0s"
        }
    
    verification_log = {
        "check_description": check_description,
        "expected_state": expected_state,
        "timestamp": timestamp,
        "verification_result": result,
        "verification_id": str(uuid.uuid4())[:8]
    }
    
    return json.dumps(verification_log, indent=2)

@tool
def rollback_action(rollback_command: str, reason: str) -> str:
    """
    Execute rollback action if there's an error
    rollback_command: Command to execute for rollback
    reason: Reason for performing the rollback
    """
    timestamp = datetime.now().isoformat()
    
    # Simulation of rollback operations
    rollback_results = {
        "scale": {
            "status": "success",
            "details": "Deployment scaled back to original replica count",
            "rollback_time": "15.2s"
        },
        "restart": {
            "status": "success", 
            "details": "Rollback completed, service restored",
            "rollback_time": "30.5s"
        },
        "patch": {
            "status": "success",
            "details": "Original configuration restored",
            "rollback_time": "8.9s"
        },
        "uncordon": {
            "status": "success",
            "details": "Node uncordoned, scheduling enabled",
            "rollback_time": "2.1s"
        },
        "apply": {
            "status": "success",
            "details": "Original resource configuration restored from backup",
            "rollback_time": "12.3s"
        }
    }
    
    # Find matching rollback
    result = None
    for rollback_type, rollback_result in rollback_results.items():
        if rollback_type in rollback_command.lower():
            result = rollback_result
            break
    
    if not result:
        result = {
            "status": "completed",
            "details": f"Rollback action executed: {rollback_command}",
            "rollback_time": "10.0s"
        }
    
    rollback_log = {
        "rollback_command": rollback_command,
        "reason": reason,
        "timestamp": timestamp,
        "rollback_result": result,
        "rollback_id": str(uuid.uuid4())[:8]
    }
    
    return json.dumps(rollback_log, indent=2)

@tool
def log_execution_step(step_number: str, action: str, status: str, details: str = "") -> str:
    """
    Log each execution step
    step_number: Step number in the execution plan
    action: Action being performed
    status: Status of the action (success, failed, in_progress)
    details: Additional details about the step (optional)
    """
    timestamp = datetime.now().isoformat()
    
    # Convert step_number to int if it's a string
    try:
        step_num = int(step_number)
    except:
        step_num = 0
    
    log_entry = {
        "step_number": step_num,
        "action": action,
        "status": status,
        "details": details,
        "timestamp": timestamp,
        "log_id": str(uuid.uuid4())[:8]
    }
    
    return json.dumps(log_entry, indent=2)

@tool
def validate_prerequisites(prerequisites: str) -> str:
    """
    Check prerequisites before execution
    prerequisites: List of prerequisites as JSON string or comma-separated text
    """
    timestamp = datetime.now().isoformat()
    
    # Parse prerequisites if it's a JSON string, otherwise split by comma
    try:
        prereq_list = json.loads(prerequisites) if prerequisites.startswith('[') else prerequisites.split(',')
        prereq_list = [prereq.strip() for prereq in prereq_list]
    except:
        prereq_list = prerequisites.split(',')
        prereq_list = [prereq.strip() for prereq in prereq_list]
    
    validation_results = []
    all_valid = True
    
    for prerequisite in prereq_list:
        # Simulate validation
        if "cluster access" in prerequisite.lower():
            validation_results.append({
                "prerequisite": prerequisite,
                "status": "valid",
                "details": "Cluster access confirmed"
            })
        elif "backup" in prerequisite.lower():
            validation_results.append({
                "prerequisite": prerequisite,
                "status": "valid", 
                "details": "Backup created successfully"
            })
        elif "permission" in prerequisite.lower():
            validation_results.append({
                "prerequisite": prerequisite,
                "status": "valid",
                "details": "Required permissions verified"
            })
        else:
            validation_results.append({
                "prerequisite": prerequisite,
                "status": "valid",
                "details": "Prerequisite check passed"
            })
    
    validation_log = {
        "prerequisites_checked": len(prereq_list),
        "all_valid": all_valid,
        "timestamp": timestamp,
        "validation_results": validation_results,
        "validation_id": str(uuid.uuid4())[:8]
    }
    
    return json.dumps(validation_log, indent=2)

def get_executor_tools():
    """Return list of tools for Executor agent"""
    return [
        simulate_kubectl_command,
        verify_system_state,
        rollback_action,
        log_execution_step,
        validate_prerequisites
    ]
