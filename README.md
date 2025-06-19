# Kubernetes Multi-Agent Incident Response System

A sophisticated multi-agent system designed to automate the incident response process for Kubernetes clusters. When alerts are triggered, the system activates a team of specialized AI agents that work together to analyze, plan, and remediate issues.

## Architecture: Digital Incident War Room

This system implements a "Digital Incident War Room" architecture with four specialized agents:

1. **The Orchestrator** - Project manager role that coordinates workflow and interaction
2. **The Analyst** - Detective/investigator that determines the root cause of incidents
3. **The Planner** - Strategic thinker that designs detailed remediation plans
4. **The Executor** - Deployment specialist that safely implements approved plans

## Workflow

1. An alert is received by the Orchestrator
2. The Orchestrator creates an incident and delegates to the Analyst
3. The Analyst investigates and identifies the root cause
4. The Orchestrator sends the analysis to the Planner
5. The Planner develops detailed remediation plans
6. The Orchestrator presents plans for human approval
7. Once approved, the Executor implements the chosen plan
8. The Executor verifies resolution and reports back
9. The Orchestrator completes the incident lifecycle

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/k8s_multi_agent.git
cd k8s_multi_agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export GEMINI_API_KEY="your_gemini_api_key"
```

## Usage

Run the system with a sample alert:

```bash
python main.py examples/alerts/node-down.json
```

Or use your own alert file:

```bash
python main.py path/to/your/alert.json
```

## Configuration

The system can be configured via environment variables:

- `GEMINI_API_KEY` - Your API key for the Gemini Language Model
- `GEMINI_BASE_URL` - The base URL for the Gemini API (optional)
- `DEBUG_MODE` - Set to "true" to enable debug logging

## Alert Format

Alerts should follow this JSON format:

```json
{
  "receiver": "team-name",
  "status": "firing",
  "alerts": [
    {
      "status": "firing",
      "labels": {
        "alertname": "KubeNodeNotReady",
        "node": "worker-node-1", 
        "severity": "critical"
      },
      "annotations": {
        "summary": "Summary of the alert",
        "description": "Detailed description of the problem"
      },
      "startsAt": "2025-06-19T01:10:00Z",
      "generatorURL": "http://prometheus.example.com/graph?g0.expr=..."
    }
  ]
}
```

## Project Structure

- `main.py` - Main entry point and workflow orchestration
- `config.py` - Configuration management
- `models.py` - Data models for incidents, alerts, and plans
- `mcp_client.py` - Model Context Protocol client for LLM interaction
- `agents/` - Individual agent implementations
- `examples/alerts/` - Sample alert files for testing

## Human-in-the-loop

The system incorporates human oversight by default. After remediation plans are generated, a human operator must review and approve them before any actions are taken.

## Extending the System

### Adding New Agent Types

1. Create a new agent class that inherits from `BaseAgent`
2. Implement the `run()` method
3. Update the workflow graph in `main.py`

### Customizing Agent Prompts

Each agent has a system prompt that defines its role and behavior. These can be customized in the agent initialization.