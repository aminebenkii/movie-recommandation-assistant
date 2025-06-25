from fastapi import FastAPI
from api.router import router
from fastapi.middleware.cors import CORSMiddleware

# Create app
app = FastAPI(
    title="Movies You Didn't Watch",
    description="A Conversationnal movie recommender chatbot",
    version="1.0.0"
)

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# mount all routes
app.include_router(router) 


# Health Check Route
@app.get("/health")
def health_check():
    return {"message": "app is live"}

