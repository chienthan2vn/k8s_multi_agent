"""
Planner Agent - Chuyên gia Lên phác đồ Điều trị
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from src.utils.parsers import get_plan_format_instructions
from src.utils.planner_tools import get_planner_tools
from src.utils.search_tool import search_k8s_docs, kubectl_help
from src.prompts.prompt_planner import PLANNER_SYSTEM_PROMPT


def create_planner_agent():
    """Tạo Planner agent với ReAct pattern"""

    # Khởi tạo LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.6,
        # max_output_tokens=LLM_CONFIG["max_tokens"]
    )

    # Lấy tools cho planning (kết hợp planning tools và search tools)
    tools = get_planner_tools() + [search_k8s_docs, kubectl_help]

    # Tạo system prompt với format instructions
    system_prompt = PLANNER_SYSTEM_PROMPT.format(
        format_instructions=get_plan_format_instructions()
    )

    # Tạo agent với create_react_agent
    agent = create_react_agent(
        llm,
        tools,
        prompt=system_prompt,
        name="planner_agent",
    )

    return agent


# def run_planner(analysis_result: dict, alert_data: dict) -> dict:
#     """Chạy planner agent với kết quả phân tích"""

#     agent = create_planner_agent()

#     # Chuẩn bị input message
#     human_prompt = PLANNER_HUMAN_PROMPT.format(
#         analysis_result=json.dumps(analysis_result, indent=2, ensure_ascii=False),
#         alert_data=json.dumps(alert_data, indent=2, ensure_ascii=False)
#     )

#     # Chạy agent
#     result = agent.invoke({
#         "messages": [{"role": "user", "content": human_prompt}]
#     })

#     # Parse kết quả
#     try:
#         # Lấy nội dung cuối cùng từ result
#         last_message = result["messages"][-1].content
#         parsed_result = plan_parser.parse(last_message)
#         return parsed_result
#     except Exception as e:
#         return {
#             "error": f"Lỗi parse kết quả planner: {str(e)}",
#             "raw_result": str(result)
#         }
