from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def root():
    return {"status": "Mobility analytics API is running"}

@app.post("/ask")
def ask_question(body: QueryRequest):
    return {
        "question": body.question,
        "answer": "This is a local API placeholder for the GenAI insights assistant.",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
