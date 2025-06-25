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

from langgraph_supervisor import create_supervisor

from src.agents.analyst import create_analyst_agent
from src.agents.planner import create_planner_agent
from src.agents.executor import create_executor_agent
from src.llms.gemini import gemini_client
from src.prompts.prompt_supervisor import SUPERVISOR_SYSTEM_PROMPT


def supervisor_agent():
    model = gemini_client()
    run_analyst, run_planner, run_executor = (
        create_analyst_agent(),
        create_planner_agent(),
        create_executor_agent(),
    )
    workflow = create_supervisor(
        [run_analyst, run_planner, run_executor],
        model=model,
        prompt=SUPERVISOR_SYSTEM_PROMPT,
        add_handoff_back_messages=True,
        output_mode="full_history",
    ).compile()
    return workflow


# Compile and run
# app = workflow.compile()
# result = app.invoke({
#     "messages": [
#         {
#             "role": "user",
#             "content": "what's the combined headcount of the FAANG companies in 2024?"
#         }
#     ]
# })

# def generate_final_report(state: WorkflowState) -> WorkflowState:
#     """Bước 5: Tạo báo cáo cuối cùng"""
#     print("📄 Đang tạo báo cáo cuối cùng...")

#     final_report = create_incident_report(
#         alert_data=state.alert_data,
#         analysis_result=state.analysis_result,
#         plan_suggestions=state.plan_suggestions,
#         execution_result=state.execution_result
#     )
#     state.final_report = final_report
#     state.current_step = "completed"

#     print("✅ Hoàn thành báo cáo sự cố!")
#     return state

# def should_execute(state: WorkflowState) -> Literal["execute", "report"]:
#     """Điều kiện để quyết định có thực thi hay không"""
#     if state.user_approval and state.current_step == "approved":
#         return "execute"
#     else:
#         return "report"

# def create_response_workflow() -> CompiledStateGraph:
#     """Tạo workflow chính cho hệ thống phản ứng"""

#     # Tạo workflow graph
#     workflow = StateGraph(WorkflowState)

#     # Thêm các nodes
#     workflow.add_node("analyze", analyze_incident)
#     workflow.add_node("plan", create_remediation_plan)
#     workflow.add_node("approval", await_approval)
#     workflow.add_node("execute", execute_plan)
#     workflow.add_node("report", generate_final_report)

#     # Thiết lập edges
#     workflow.add_edge(START, "analyze")
#     workflow.add_edge("analyze", "plan")
#     workflow.add_edge("plan", "approval")

#     # Conditional edge dựa trên approval
#     workflow.add_conditional_edges(
#         "approval",
#         should_execute,
#         {
#             "execute": "execute",
#             "report": "report"
#         }
#     )

#     workflow.add_edge("execute", "report")
#     workflow.add_edge("report", END)

#     # Compile workflow
#     compiled_workflow = workflow.compile()
#     return compiled_workflow

# def run_incident_response(alert_data: dict) -> dict:
#     """Chạy toàn bộ workflow phản ứng sự cố"""
#     print("\n🚨 BẮT ĐẦU QUÁ TRÌNH PHẢN ỨNG SỰ CỐ")
#     print("=" * 60)

#     # Tạo workflow
#     workflow = create_response_workflow()

#     # Khởi tạo state
#     initial_state = WorkflowState()
#     initial_state.alert_data = alert_data

#     # Chạy workflow
#     final_state = workflow.invoke(initial_state)

#     print("\n🎉 HOÀN THÀNH QUÁ TRÌNH PHẢN ỨNG")
#     print("=" * 60)

#     return final_state.final_report
