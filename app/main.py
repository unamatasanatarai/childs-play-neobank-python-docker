from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth import router as auth_router
from app.banking import router as banking_router
from app.config import settings
from app.banking.router import router as banking_router

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Standard Middleware for Demo UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(banking_router, prefix="/api/v1/banking", tags=["banking"])


@app.get("/health")
async def health_check():
    return {"status": "operational"}
