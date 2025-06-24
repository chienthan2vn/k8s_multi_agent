"""
Unit tests cho các agent
"""

import unittest
import os
import json
from pathlib import Path

# Setup environment for testing
os.environ["GOOGLE_API_KEY"] = "test-key"
os.environ["TAVILY_API_KEY"] = "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"

class TestAgents(unittest.TestCase):
    
    def setUp(self):
        """Setup test data"""
        self.sample_alert = {
            "receiver": "platform-alerts",
            "status": "firing",
            "alerts": [
                {
                    "status": "firing",
                    "labels": {
                        "alertname": "KubeAPILatencyHigh",
                        "severity": "warning",
                        "job": "apiserver"
                    },
                    "annotations": {
                        "summary": "High latency for Kubernetes API server",
                        "description": "The 99th percentile latency for Kubernetes API server is over 1s for the last 5 minutes."
                    },
                    "startsAt": "2025-06-19T04:00:00Z"
                }
            ]
        }
    
    def test_analyst_structure(self):
        """Test Analyst agent structure"""
        from src.agents.analyst import create_analyst_agent
        
        # Test agent creation
        agent = create_analyst_agent()
        self.assertIsNotNone(agent)
        
    def test_planner_structure(self):
        """Test Planner agent structure"""
        from src.agents.planner import create_planner_agent
        
        # Test agent creation
        agent = create_planner_agent()
        self.assertIsNotNone(agent)
        
    def test_executor_structure(self):
        """Test Executor agent structure"""
        from src.agents.executor import create_executor_agent
        
        # Test agent creation
        agent = create_executor_agent()
        self.assertIsNotNone(agent)
        
    def test_workflow_structure(self):
        """Test workflow structure"""
        from src.workflows.response_workflow import create_response_workflow
        
        # Test workflow creation
        workflow = create_response_workflow()
        self.assertIsNotNone(workflow)
        
    def test_parsers(self):
        """Test output parsers"""
        from src.utils.parsers import (
            get_analysis_format_instructions,
            get_plan_format_instructions,
            get_execution_format_instructions
        )
        
        # Test format instructions are strings
        self.assertIsInstance(get_analysis_format_instructions(), str)
        self.assertIsInstance(get_plan_format_instructions(), str)
        self.assertIsInstance(get_execution_format_instructions(), str)
        
    def test_search_tools(self):
        """Test search tools"""
        from src.utils.search_tool import get_analysis_tools
        
        # Test tools list
        tools = get_analysis_tools()
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)

if __name__ == "__main__":
    unittest.main()
