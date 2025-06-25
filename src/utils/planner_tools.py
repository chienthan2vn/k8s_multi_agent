"""
Tools cho Planner Agent - Các công cụ lập kế hoạch khắc phục
"""

from langchain.tools import tool
import json


@tool
def get_kubectl_commands(resource_type: str) -> str:
    """Lấy danh sách lệnh kubectl phổ biến cho resource type"""
    commands = {
        "pod": [
            "kubectl get pods",
            "kubectl describe pod <pod-name>",
            "kubectl logs <pod-name>",
            "kubectl delete pod <pod-name>",
            "kubectl exec -it <pod-name> -- /bin/bash",
            "kubectl restart pod <pod-name>",
        ],
        "deployment": [
            "kubectl get deployments",
            "kubectl describe deployment <deployment-name>",
            "kubectl scale deployment <deployment-name> --replicas=<number>",
            "kubectl rollout restart deployment <deployment-name>",
            "kubectl rollout undo deployment <deployment-name>",
            "kubectl rollout status deployment <deployment-name>",
        ],
        "service": [
            "kubectl get services",
            "kubectl describe service <service-name>",
            "kubectl patch service <service-name> -p '<patch>'",
            "kubectl edit service <service-name>",
        ],
        "node": [
            "kubectl get nodes",
            "kubectl describe node <node-name>",
            "kubectl cordon <node-name>",
            "kubectl drain <node-name>",
            "kubectl uncordon <node-name>",
            "kubectl top node <node-name>",
        ],
        "namespace": [
            "kubectl get namespaces",
            "kubectl describe namespace <namespace-name>",
            "kubectl delete namespace <namespace-name>",
        ],
        "configmap": [
            "kubectl get configmaps",
            "kubectl describe configmap <configmap-name>",
            "kubectl edit configmap <configmap-name>",
        ],
        "secret": [
            "kubectl get secrets",
            "kubectl describe secret <secret-name>",
            "kubectl delete secret <secret-name>",
        ],
    }
    return json.dumps(
        commands.get(resource_type, ["Resource type not found"]), indent=2
    )


@tool
def estimate_risk_level(action_list: list) -> str:
    """Đánh giá mức độ rủi ro của các hành động"""
    high_risk_actions = [
        "delete",
        "drain",
        "cordon",
        "scale down",
        "restart",
        "undo",
        "remove",
    ]
    medium_risk_actions = ["scale up", "patch", "update", "edit", "restart deployment"]
    low_risk_actions = ["get", "describe", "logs", "top", "status"]

    risk_score = 0
    risk_details = []

    for action in action_list:
        action_lower = action.lower()
        if any(hr in action_lower for hr in high_risk_actions):
            risk_score += 3
            risk_details.append(f"HIGH RISK: {action}")
        elif any(mr in action_lower for mr in medium_risk_actions):
            risk_score += 2
            risk_details.append(f"MEDIUM RISK: {action}")
        elif any(lr in action_lower for lr in low_risk_actions):
            risk_score += 1
            risk_details.append(f"LOW RISK: {action}")
        else:
            risk_score += 2
            risk_details.append(f"UNKNOWN RISK: {action}")

    if risk_score >= 6:
        level = "high"
    elif risk_score >= 3:
        level = "medium"
    else:
        level = "low"

    return json.dumps(
        {"risk_level": level, "risk_score": risk_score, "details": risk_details},
        indent=2,
    )


@tool
def get_rollback_commands(resource_type: str, action: str) -> str:
    """Lấy lệnh rollback tương ứng với action"""
    rollback_mapping = {
        "pod": {
            "delete": "kubectl apply -f <backup-yaml>",
            "restart": "# Pod sẽ tự restart nếu có deployment",
        },
        "deployment": {
            "scale": "kubectl scale deployment <deployment-name> --replicas=<original-replicas>",
            "restart": "# Deployment sẽ rollback tự động nếu fail",
            "update": "kubectl rollout undo deployment <deployment-name>",
            "delete": "kubectl apply -f <backup-yaml>",
        },
        "service": {
            "patch": "kubectl patch service <service-name> -p '<original-patch>'",
            "edit": "kubectl apply -f <backup-yaml>",
            "delete": "kubectl apply -f <backup-yaml>",
        },
        "node": {
            "cordon": "kubectl uncordon <node-name>",
            "drain": "kubectl uncordon <node-name>",
        },
    }

    result = rollback_mapping.get(resource_type, {}).get(
        action, "Manual rollback required"
    )
    return json.dumps({"rollback_command": result}, indent=2)


@tool
def estimate_execution_time(steps: list) -> str:
    """Ước tính thời gian thực hiện kế hoạch"""
    time_mapping = {
        "get": 1,
        "describe": 2,
        "logs": 3,
        "delete": 5,
        "restart": 30,
        "scale": 15,
        "patch": 10,
        "drain": 300,  # 5 minutes
        "cordon": 5,
        "uncordon": 5,
    }

    total_time = 0
    step_details = []

    for i, step in enumerate(steps, 1):
        step_lower = step.lower()
        step_time = 10  # default time

        for action, time_seconds in time_mapping.items():
            if action in step_lower:
                step_time = time_seconds
                break

        total_time += step_time
        step_details.append(f"Step {i}: {step_time}s - {step}")

    # Thêm buffer time
    total_time = int(total_time * 1.2)  # 20% buffer

    return json.dumps(
        {
            "total_time_seconds": total_time,
            "total_time_formatted": f"{total_time // 60}m {total_time % 60}s",
            "step_breakdown": step_details,
        },
        indent=2,
    )


def get_planner_tools():
    """Trả về danh sách tools cho Planner agent"""
    return [
        get_kubectl_commands,
        estimate_risk_level,
        get_rollback_commands,
        estimate_execution_time,
    ]
