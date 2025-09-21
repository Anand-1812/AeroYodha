from fastapi import FastAPI
from database import engine, Base
from modles import UAV

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "UAV Traffic Management System", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
