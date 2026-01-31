import asyncio
import websockets
import json
import os
import datetime

# CONFIGURATION
PORT = 8765
AUTH_TOKEN = os.getenv("HIVE_SECRET_KEY", "default_secret_key")
active_agents = {}

# THE DNA (Role Definitions)
ROLE_DEFINITIONS = {
    "backend_engineer": "You are a Senior Backend Engineer. Infrastructure: Render. Stack: Python/FastAPI.",
    "frontend_engineer": "You are a Lead Frontend Engineer. Infrastructure: Railway. Stack: React/TypeScript.",
    "data_scientist": "You are a Data Scientist. Infrastructure: AWS DynamoDB. Focus: Predictive modeling.",
    "project_manager": "You are a Technical PM. Infrastructure: GitHub. Focus: Agile workflows.",
    "ceo_proxy": "You are the acting CEO. Focus: High-level strategy, revenue growth.",
    "chief_of_staff": "You are the Chief of Staff. Monitor agent logs and enforce deadlines.",
    "customer_rep": "You are a Customer Rep. Solve user problems fast.",
    "cyber_security": "You are Cyber Security. Enforce Zero-Trust and monitor anomalies."
}

async def register_agent(websocket, role):
    active_agents[role] = websocket
    print(f"✅ [REGISTERED] Agent '{role}' connected from {websocket.remote_address}")
    await websocket.send(json.dumps({
        "type": "HANDSHAKE",
        "status": "ACCEPTED",
        "system_prompt": ROLE_DEFINITIONS.get(role, "You are a helpful AI assistant.")
    }))

async def handler(websocket):
    try:
        init_data = await websocket.recv()
        data = json.loads(init_data)
        
        if data.get("token") != AUTH_TOKEN:
            print("❌ Authentication failed.")
            await websocket.close()
            return
            
        role = data.get("role")
        await register_agent(websocket, role)

        async for message in websocket:
            msg_data = json.loads(message)
            print(f"📩 [{role.upper()}] Report: {msg_data.get('result')}")

    except websockets.exceptions.ConnectionClosed:
        print(f"❌ [DISCONNECTED] Agent '{role}' went offline.")
        if role in active_agents:
            del active_agents[role]

async def admin_console():
    print("\n💻 ORCHESTRATOR CONSOLE READY. Type 'role: instruction' to command agents.")
    while True:
        cmd = await asyncio.to_thread(input, "")
        if ":" in cmd:
            target, instruction = cmd.split(":", 1)
            target = target.strip()
            instruction = instruction.strip()
            
            if target in active_agents:
                await active_agents[target].send(json.dumps({"type": "EXECUTE", "instruction": instruction}))
                print(f"🚀 Command sent to {target}")
            elif target == "all":
                for role, ws in active_agents.items():
                    await ws.send(json.dumps({"type": "EXECUTE", "instruction": instruction}))
                print("🚀 Broadcast sent to all agents.")
            else:
                print(f"⚠️ Agent '{target}' is not connected.")
        else:
            print("Usage: <role>: <instruction>")

async def main():
    server = await websockets.serve(handler, "0.0.0.0", PORT)
    print(f"🏰 HIVE MIND ORCHESTRATOR running on port {PORT}")
    await asyncio.gather(server.wait_closed(), admin_console())

if __name__ == "__main__":
    asyncio.run(main())
