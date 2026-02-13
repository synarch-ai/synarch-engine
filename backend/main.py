from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI(title="Pantheon AI Backend", version="1.0.0")

# CORS (Allow Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.api.server import router
app.include_router(router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "pantheon-backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
