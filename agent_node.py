import asyncio
import websockets
import json
import sys
import os

# Usage: python3 agent_node.py <ROLE> <ORCHESTRATOR_IP> <TOKEN>
ROLE = sys.argv[1] if len(sys.argv) > 1 else "unknown_agent"
URI = f"ws://{sys.argv[2]}:8765" if len(sys.argv) > 2 else "ws://localhost:8765"
TOKEN = sys.argv[3] if len(sys.argv) > 3 else "default_secret_key"

async def run_agent():
    print(f"🔌 Connecting to Hive Mind at {URI} as {ROLE}...")
    async with websockets.connect(URI) as websocket:
        # Handshake
        await websocket.send(json.dumps({"token": TOKEN, "role": ROLE}))
        
        while True:
            msg = await websocket.recv()
            data = json.loads(msg)
            
            if data['type'] == 'HANDSHAKE':
                print(f"✅ LINK ESTABLISHED. Orders: {data['system_prompt']}")
                
            elif data['type'] == 'EXECUTE':
                instruction = data['instruction']
                print(f"⚡ EXECUTING DIRECTIVE: {instruction}")
                
                # --- SIMULATED AI WORK ---
                # In production, this calls OpenAI/Gemini APIs or runs local scripts
                result = f"Completed task: {instruction} (Simulated)"
                
                await websocket.send(json.dumps({"role": ROLE, "result": result}))

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(run_agent())
        except Exception as e:
            print(f"❌ Connection lost. Retrying in 5s... ({e})")
            import time; time.sleep(5)
