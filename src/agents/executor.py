"""
Executor Agent - Robot Phẫu thuật
"""
import os
import sys
import json
import uuid
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage

from src.utils.parsers import get_execution_format_instructions, execution_parser
from src.utils.executor_tools import get_executor_tools
from src.prompts.prompt_executor import EXECUTOR_SYSTEM_PROMPT

def create_executor_agent():
    """Tạo Executor agent với ReAct pattern"""
    
    # Khởi tạo LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.1,  # Rất thấp cho executor để đảm bảo tính nhất quán
        # max_output_tokens=LLM_CONFIG["max_tokens"]
    )
    
    # Lấy tools cho execution
    tools = get_executor_tools()
    
    # Tạo system prompt với format instructions
    system_prompt = EXECUTOR_SYSTEM_PROMPT
    
    # Tạo agent với create_react_agent
    agent = create_react_agent(
        llm, 
        tools,
        prompt=system_prompt,
        name="executor_agent",
        # debug=True,
    )
    
    return agent

# def run_executor(approved_plan: dict, alert_data: dict, analysis_result: dict) -> dict:
#     """Chạy executor agent với kế hoạch đã được phê duyệt"""
    
#     agent = create_executor_agent()
    
#     # Chuẩn bị input message
#     human_prompt = EXECUTOR_HUMAN_PROMPT.format(
#         approved_plan=json.dumps(approved_plan, indent=2, ensure_ascii=False),
#         alert_data=json.dumps(alert_data, indent=2, ensure_ascii=False),
#         analysis_result=json.dumps(analysis_result, indent=2, ensure_ascii=False)
#     )
    
#     # Chạy agent
#     result = agent.invoke({
#         "messages": [{"role": "user", "content": human_prompt}]
#     })
    
#     # Parse kết quả
#     try:
#         # Lấy nội dung cuối cùng từ result
#         last_message = result["messages"][-1].content
#         parsed_result = execution_parser.parse(last_message)
        
#         # Thêm execution ID nếu chưa có
#         result_dict = parsed_result
#         if not result_dict.get("execution_id"):
#             result_dict["execution_id"] = str(uuid.uuid4())
            
#         return result_dict
#     except Exception as e:
#         return {
#             "error": f"Lỗi parse kết quả executor: {str(e)}",
#             "raw_result": str(result),
#             "execution_id": str(uuid.uuid4())
#         }
