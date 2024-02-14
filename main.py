from fastapi import FastAPI

app = FastAPI()

@app.get("/api/")
def read_root():
    return {"Hello": "World 2"}

@app.get("/api/info")
def read_root():
    return {"url": "/api/info"}

@app.get("/api/info/{item_id}")
def read_root(item_id):
    return {"url": "/api/info", "item_id": item_id}
