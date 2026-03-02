from fastapi import FastAPI
import json

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Autonomous Factory Online", "roles_loaded": 30}

@app.get("/roles")
def get_roles():
    with open("role_library.json", "r") as f:
        return json.load(f)
