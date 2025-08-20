from fastapi import FastAPI

app = FastAPI(
    title="Simple Test API",
    description="Basic test server to verify setup",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)