from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def first_example():
      return "Hello world"
