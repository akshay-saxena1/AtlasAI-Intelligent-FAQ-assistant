"""
FastAPI application entry point for the CodeAlpha FAQ Chatbot.

Configures CORS, lifespan events (database initialization, NLP model
loading, search engine fitting), and mounts all API route modules.

Author: CodeAlpha Intern | Registration ID: Akshay Saxena
"""
import uvicorn
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.database import init_database
from backend.nlp.search_engine import initialize_search_engine
from backend.routes import chat, admin, analytics, bookmarks


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events.

    Startup sequence:
        1. Initialize SQLite database schema
        2. Load SpaCy NLP model
        3. Load Sentence Transformer model onto CUDA
        4. Fit the hybrid search engine on all FAQs

    Yields control to the application, then performs cleanup on shutdown.

    Args:
        app: The FastAPI application instance.

    Yields:
        None: Control is yielded to the running application.

    Time Complexity: O(N × L + M) where N=FAQs, L=avg length, M=model size
    Space Complexity: O(N × (V + D) + M)
    """
    settings = get_settings()
    print("=" * 60)
    print(f"  {settings.app_name} v{settings.app_version}")
    print(f"  Registration ID: {settings.registration_id}")
    print("=" * 60)

    # Stage 1: Initialize database schema
    print("\n[STARTUP] Stage 1/3: Initializing database...")
    init_database()

    # Stage 2: Initialize NLP models & search engine
    print("\n[STARTUP] Stage 2/3: Loading NLP models...")
    print("[STARTUP] Stage 3/3: Fitting search engine on FAQ corpus...")
    initialize_search_engine()

    print("\n" + "=" * 60)
    print("  ✅ All systems operational. Ready for queries.")
    print("=" * 60 + "\n")

    yield

    # Shutdown
    print("\n[SHUTDOWN] Cleaning up resources...")
    print("[SHUTDOWN] Goodbye! 👋")


# ============================================================
# Application Factory
# ============================================================

settings = get_settings()

app: FastAPI = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "A production-grade, CUDA-accelerated FAQ chatbot with a hybrid "
        "TF-IDF + Sentence Transformer search engine. Built for the "
        f"CodeAlpha internship. Registration ID: {settings.registration_id}"
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount route modules
app.include_router(chat.router)
app.include_router(admin.router)
app.include_router(analytics.router)
app.include_router(bookmarks.router)


@app.get("/", tags=["Health"])
async def root() -> dict[str, str]:
    """Health check endpoint.

    Returns application metadata for monitoring and provenance.

    Returns:
        dict: Application name, version, status, and registration ID.

    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "registration_id": settings.registration_id,
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Detailed health check for load balancers and orchestrators.

    Returns:
        dict: Status indicator for infrastructure monitoring.

    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    return {"status": "healthy", "service": settings.app_name}
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)