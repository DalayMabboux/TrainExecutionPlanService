from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_item():
    return {"message": "Welcome to our app"}
