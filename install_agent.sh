#!/bin/bash
# USAGE: ./install_agent.sh <ROLE_NAME> <ORCHESTRATOR_IP> <TOKEN>

ROLE=$1
ORCHESTRATOR_IP=$2
TOKEN=$3

if [ -z "$ROLE" ] || [ -z "$ORCHESTRATOR_IP" ]; then
  echo "Usage: ./install_agent.sh <ROLE_NAME> <ORCHESTRATOR_IP> <TOKEN>"
  exit 1
fi

echo "🚀 Installing Clawdbot Agent: $ROLE..."
pip install websockets asyncio

# Run in background
nohup python3 agent_node.py "$ROLE" "$ORCHESTRATOR_IP" "$TOKEN" > agent.log 2>&1 &
echo "✅ Agent is running in background. Check agent.log for output."
