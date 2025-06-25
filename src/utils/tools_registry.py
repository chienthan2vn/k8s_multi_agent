"""
Tools tổng hợp cho hệ thống Multi-Agent
"""

from .search_tool import get_analysis_tools
from .planner_tools import get_planner_tools
from .executor_tools import get_executor_tools


def get_all_tools():
    """Lấy tất cả tools trong hệ thống"""
    return {
        "analyst_tools": get_analysis_tools(),
        "planner_tools": get_planner_tools(),
        "executor_tools": get_executor_tools(),
    }


def get_tools_by_agent(agent_type: str):
    """Lấy tools theo loại agent"""
    tools_mapping = {
        "analyst": get_analysis_tools(),
        "planner": get_planner_tools(),
        "executor": get_executor_tools(),
    }
    return tools_mapping.get(agent_type, [])


def list_available_tools():
    """Liệt kê tất cả tools có sẵn"""
    all_tools = get_all_tools()

    tool_summary = {}
    for agent_type, tools in all_tools.items():
        tool_summary[agent_type] = []
        for tool in tools:
            tool_summary[agent_type].append(
                {"name": tool.name, "description": tool.description}
            )

    return tool_summary
