from fastapi import FastAPI
from agent import ask_agent

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Agent is online and running"}

@app.post("/query")
def query_agent(prompt: str):
    return {"response": ask_agent(prompt)}
