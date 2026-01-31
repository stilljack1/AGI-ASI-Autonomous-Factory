# 🏭 AGI / ASI Autonomous Factory
**Distributed "Hive Mind" Architecture for Autonomous AI Agents**

## 🧠 Components
1. **Orchestrator (`orchestrator.py`):** The central brain running on AWS EC2. It manages connections and routes prompts.
2. **Agent Node (`agent_node.py`):** The generic runtime that lives on Render, Railway, Hostinger, etc.
3. **Installer (`install_agent.sh`):** A one-line script to deploy an agent anywhere.

## 🚀 How to Start the Factory
1. **Run the Brain:** `python3 orchestrator.py`
2. **Deploy a Limb:** `./install_agent.sh backend_engineer localhost default_secret_key`
