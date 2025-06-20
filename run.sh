#!/bin/bash

# Run the Kubernetes Multi-Agent Incident Response System
# Usage: ./run.sh [path/to/alert.json]

# Activate the conda environment
conda activate k8s_agent

# Set the default alert file if not provided
ALERT_FILE=${1:-"examples/alerts/node-down.json"}

# Run the main script
python main.py $ALERT_FILE
