# keep_alive.py
from threading import Thread
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "bot is running"}

def run():
    uvicorn.run(app, host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()
