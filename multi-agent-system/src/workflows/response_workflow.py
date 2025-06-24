"""
Workflow chính cho hệ thống Multi-Agent phản ứng nhanh Kubernetes

Quy trình làm việc của Đội:
1. Tiếp nhận: Một "ca cấp cứu" đến, Trưởng nhóm mở hồ sơ  
2. Chẩn đoán: Chuyên gia Chẩn đoán vào cuộc tìm nguyên nhân
3. Lên phác đồ: Chuyên gia Lên phác đồ đề xuất các phương án
4. Hội chẩn: Trưởng nhóm trình bày phác đồ cho kỹ sư để xin phê duyệt
5. Can thiệp: Robot Phẫu thuật thực hiện kế hoạch đã được duyệt
6. Báo cáo: Trưởng nhóm xác nhận sự cố đã được giải quyết và đóng hồ sơ
"""

import os
import sys
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from src.agents.analyst import run_analyst
from src.agents.planner import run_planner
from src.agents.executor import run_executor
from src.agents.orchestrator import create_incident_report, run_orchestrator_summary

class WorkflowState:
    """State object cho workflow"""
    def __init__(self):
        self.alert_data: Dict[str, Any] = {}
        self.analysis_result: Dict[str, Any] = {}
        self.plan_suggestions: Dict[str, Any] = {}
        self.execution_result: Dict[str, Any] = {}
        self.final_report: Dict[str, Any] = {}
        self.current_step: str = "received"
        self.user_approval: bool = False

def analyze_incident(state: WorkflowState) -> WorkflowState:
    """Bước 1: Chẩn đoán sự cố bằng Analyst agent"""
    print("🔍 Bắt đầu chẩn đoán sự cố...")
    
    analysis_result = run_analyst(state.alert_data)
    state.analysis_result = analysis_result
    state.current_step = "analyzed"
    
    print(f"✅ Hoàn thành chẩn đoán. Nguyên nhân: {analysis_result.get('root_cause', 'Không xác định')}")
    return state

def create_remediation_plan(state: WorkflowState) -> WorkflowState:
    """Bước 2: Lên kế hoạch khắc phục bằng Planner agent"""
    print("📋 Đang lập kế hoạch khắc phục...")
    
    plan_result = run_planner(state.analysis_result, state.alert_data)
    state.plan_suggestions = plan_result
    state.current_step = "planned"
    
    print(f"✅ Hoàn thành lập kế hoạch: {plan_result.get('plan_name', 'Không có tên')}")
    return state

def await_approval(state: WorkflowState) -> WorkflowState:
    """Bước 3: Chờ phê duyệt từ kỹ sư"""
    print("⏳ Chờ phê duyệt kế hoạch từ kỹ sư...")
    
    # Tạo báo cáo để trình bày cho kỹ sư
    summary = run_orchestrator_summary(
        alert_data=state.alert_data,
        analysis_result=state.analysis_result,
        plan_suggestions=state.plan_suggestions,
        current_step="awaiting_approval"
    )
    
    print("📋 TRÌNH BÁY KẾ HOẠCH CHO KỸ SƯ:")
    print("=" * 50)
    print(summary)
    print("=" * 50)
    
    # Trong thực tế, đây sẽ là input từ user interface
    # Hiện tại mô phỏng auto-approve cho demo
    response = input("\n🤔 Bạn có muốn phê duyệt kế hoạch này? (y/n): ")
    state.user_approval = response.lower() in ['y', 'yes', 'đồng ý']
    
    if state.user_approval:
        state.current_step = "approved"
        print("✅ Kế hoạch đã được phê duyệt!")
    else:
        state.current_step = "rejected"
        print("❌ Kế hoạch bị từ chối!")
    
    return state

def execute_plan(state: WorkflowState) -> WorkflowState:
    """Bước 4: Thực thi kế hoạch bằng Executor agent"""
    print("⚙️ Bắt đầu thực thi kế hoạch...")
    
    execution_result = run_executor(
        state.plan_suggestions, 
        state.alert_data, 
        state.analysis_result
    )
    state.execution_result = execution_result
    state.current_step = "executed"
    
    print(f"✅ Hoàn thành thực thi. Trạng thái: {execution_result.get('status', 'Không xác định')}")
    return state

def generate_final_report(state: WorkflowState) -> WorkflowState:
    """Bước 5: Tạo báo cáo cuối cùng"""
    print("📄 Đang tạo báo cáo cuối cùng...")
    
    final_report = create_incident_report(
        alert_data=state.alert_data,
        analysis_result=state.analysis_result,
        plan_suggestions=state.plan_suggestions,
        execution_result=state.execution_result
    )
    state.final_report = final_report
    state.current_step = "completed"
    
    print("✅ Hoàn thành báo cáo sự cố!")
    return state

def should_execute(state: WorkflowState) -> Literal["execute", "report"]:
    """Điều kiện để quyết định có thực thi hay không"""
    if state.user_approval and state.current_step == "approved":
        return "execute"
    else:
        return "report"

def create_response_workflow() -> CompiledStateGraph:
    """Tạo workflow chính cho hệ thống phản ứng"""
    
    # Tạo workflow graph
    workflow = StateGraph(WorkflowState)
    
    # Thêm các nodes
    workflow.add_node("analyze", analyze_incident)
    workflow.add_node("plan", create_remediation_plan)
    workflow.add_node("approval", await_approval)
    workflow.add_node("execute", execute_plan)
    workflow.add_node("report", generate_final_report)
    
    # Thiết lập edges
    workflow.add_edge(START, "analyze")
    workflow.add_edge("analyze", "plan")
    workflow.add_edge("plan", "approval")
    
    # Conditional edge dựa trên approval
    workflow.add_conditional_edges(
        "approval",
        should_execute,
        {
            "execute": "execute",
            "report": "report"
        }
    )
    
    workflow.add_edge("execute", "report")
    workflow.add_edge("report", END)
    
    # Compile workflow
    compiled_workflow = workflow.compile()
    return compiled_workflow

def run_incident_response(alert_data: dict) -> dict:
    """Chạy toàn bộ workflow phản ứng sự cố"""
    print("\n🚨 BẮT ĐẦU QUÁ TRÌNH PHẢN ỨNG SỰ CỐ")
    print("=" * 60)
    
    # Tạo workflow
    workflow = create_response_workflow()
    
    # Khởi tạo state
    initial_state = WorkflowState()
    initial_state.alert_data = alert_data
    
    # Chạy workflow
    final_state = workflow.invoke(initial_state)
    
    print("\n🎉 HOÀN THÀNH QUÁ TRÌNH PHẢN ỨNG")
    print("=" * 60)
    
    return final_state.final_report
