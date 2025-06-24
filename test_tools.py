#!/usr/bin/env python3
"""
Demo script để test các tools của hệ thống
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_analysis_tools():
    """Test tools của Analyst agent"""
    print("🔍 Testing Analyst Tools...")
    
    from src.utils.search_tool import get_analysis_tools
    
    tools = get_analysis_tools()
    print(f"Available tools: {len(tools)}")
    
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    
    # Test một vài tools
    print("\n📋 Testing search tools...")
    
    try:
        from src.utils.search_tool import analyze_alert_severity
        
        # Test alert severity analysis
        test_labels = {"severity": "warning", "alertname": "HighLatency"}
        test_annotations = {
            "description": "API server latency is high over 1 second",
            "summary": "High latency detected"
        }
        
        result = analyze_alert_severity.invoke({
            "alert_labels": test_labels,
            "annotations": test_annotations
        })
        print(f"Severity analysis result: {result}")
        
    except Exception as e:
        print(f"Error testing analysis tools: {e}")

def test_planner_tools():
    """Test tools của Planner agent"""
    print("\n📋 Testing Planner Tools...")
    
    from src.utils.planner_tools import get_planner_tools
    
    tools = get_planner_tools()
    print(f"Available tools: {len(tools)}")
    
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    
    # Test một vài tools
    print("\n🔧 Testing planner tools...")
    
    try:
        from src.utils.planner_tools import get_kubectl_commands, estimate_risk_level
        
        # Test kubectl commands
        result = get_kubectl_commands.invoke({"resource_type": "pod"})
        print(f"Kubectl commands for pod: {result[:100]}...")
        
        # Test risk level estimation
        test_actions = ["kubectl delete pod", "kubectl get pods", "kubectl drain node"]
        result = estimate_risk_level.invoke({"action_list": test_actions})
        print(f"Risk level estimation: {result}")
        
    except Exception as e:
        print(f"Error testing planner tools: {e}")

def test_executor_tools():
    """Test tools của Executor agent"""
    print("\n⚙️ Testing Executor Tools...")
    
    from src.utils.executor_tools import get_executor_tools
    
    tools = get_executor_tools()
    print(f"Available tools: {len(tools)}")
    
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    
    # Test một vài tools
    print("\n🔧 Testing executor tools...")
    
    try:
        from src.utils.executor_tools import simulate_kubectl_command, verify_system_state
        
        # Test kubectl simulation
        result = simulate_kubectl_command.invoke({"command": "kubectl get pods"})
        print(f"Kubectl simulation: {result[:150]}...")
        
        # Test system verification
        result = verify_system_state.invoke({
            "check_description": "pod status",
            "expected_state": "running"
        })
        print(f"System verification: {result[:150]}...")
        
    except Exception as e:
        print(f"Error testing executor tools: {e}")

def test_tools_registry():
    """Test tools registry"""
    print("\n📚 Testing Tools Registry...")
    
    try:
        from src.utils.tools_registry import list_available_tools, get_tools_by_agent
        
        # List all tools
        all_tools = list_available_tools()
        print("All available tools:")
        for agent_type, tools in all_tools.items():
            print(f"\n{agent_type.upper()}:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description'][:60]}...")
        
        # Test getting tools by agent
        analyst_tools = get_tools_by_agent("analyst")
        print(f"\nAnalyst has {len(analyst_tools)} tools")
        
    except Exception as e:
        print(f"Error testing tools registry: {e}")

def main():
    """Main function"""
    print("🚀 DEMO: Testing Multi-Agent Tools")
    print("=" * 50)
    
    # Set up environment
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDgAlnEdV-wwLc41VtAvD3p4NvmmVrJIro"
    os.environ["TAVILY_API_KEY"] = "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"
    
    test_analysis_tools()
    test_planner_tools() 
    test_executor_tools()
    test_tools_registry()
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    main()
