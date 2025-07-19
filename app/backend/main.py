from fastapi import FastAPI
from app.backend.api.router import api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Movies You Didn't Watch",
    description="A Conversational movie recommender chatbot",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
)

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount all routes
app.include_router(api_router)


# Health Check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
