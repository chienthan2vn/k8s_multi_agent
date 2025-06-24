"""
Analyst Agent - Chuyên gia Chẩn đoán
"""
import os
import sys
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage

from src.utils.search_tool import get_analysis_tools
from src.utils.parsers import get_analysis_format_instructions, analysis_parser
from src.prompts.prompt_analyst import ANALYST_SYSTEM_PROMPT, ANALYST_HUMAN_PROMPT

def create_analyst_agent():
    """Tạo Analyst agent với ReAct pattern"""
    
    # Khởi tạo LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.6,
        # max_output_tokens=LLM_CONFIG["max_tokens"] if "max_tokens" in LLM_CONFIG else None
    )
    
    # Lấy tools cho analysis
    tools = get_analysis_tools()
    
    # Tạo system prompt với format instructions
    system_prompt = ANALYST_SYSTEM_PROMPT.format(
        format_instructions=get_analysis_format_instructions()
    )
    
    # Tạo agent với create_react_agent
    agent = create_react_agent(
        llm, 
        tools,
        prompt=system_prompt,
        name="analyst_agent",
    )
    
    return agent

# def run_analyst(alert_data: dict) -> dict:
#     """Chạy analyst agent với alert data"""
    
#     agent = create_analyst_agent()
    
#     # Chuẩn bị input message
#     human_prompt = ANALYST_HUMAN_PROMPT.format(
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
#         parsed_result = analysis_parser.parse(last_message)
#         return parsed_result
#     except Exception as e:
#         return {
#             "error": f"Lỗi parse kết quả analyst: {str(e)}",
#             "raw_result": str(result)
#         }