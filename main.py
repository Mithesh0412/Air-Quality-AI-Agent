from fastapi import FastAPI
from agent import ask_agent

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Agent is online and running"}

@app.post("/query")
def query_agent(prompt: str):
    return {"response": ask_agent(prompt)}
