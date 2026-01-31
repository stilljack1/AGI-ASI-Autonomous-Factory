#!/bin/bash
# ==========================================
# CLAWDBOT DISTRIBUTED ROLE INSTALLER
# ==========================================
ROLE=$1
CONTROL_SERVER=$2 # Your AWS EC2 IP
AUTH_TOKEN=$3     # Your HIVE_SECRET_KEY

if [ -z "$ROLE" ] || [ -z "$CONTROL_SERVER" ] || [ -z "$AUTH_TOKEN" ]; then
  echo "Usage: ./deploy_role.sh ROLE CONTROL_SERVER_URL AUTH_TOKEN"
  exit 1
fi

echo "🚀 Deploying Role: $ROLE..."
mkdir -p ~/clawdbot_role && cd ~/clawdbot_role

# Install Node Logic
cat << 'PYTHON_EOF' > agent_node.py
import asyncio, websockets, json, os, subprocess
import sys

ROLE = sys.argv[1]
URI = f"ws://{sys.argv[2]}:8765"
TOKEN = sys.argv[3]

async def run():
    async with websockets.connect(URI) as ws:
        await ws.send(json.dumps({"token": TOKEN, "role": ROLE}))
        print(f"✅ {ROLE} Connected to Brain.")
        async for msg in ws:
            task = json.loads(msg)
            print(f"📩 Task: {task['instruction']}")
            # Execute Shell logic
            res = subprocess.getoutput(task['instruction'])
            await ws.send(json.dumps({"role": ROLE, "result": res}))

asyncio.run(run(ROLE, sys.argv[2], TOKEN))
PYTHON_EOF

# Standard start command
nohup python3 agent_node.py "$ROLE" "$CONTROL_SERVER" "$AUTH_TOKEN" > agent.log 2>&1 &
echo "✅ $ROLE Agent is live."
