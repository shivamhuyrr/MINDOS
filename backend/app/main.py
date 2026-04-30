"""
MindOS AI - FastAPI Application Entry Point
Initializes all services and mounts routers.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.APP_DEBUG else logging.WARNING,
    format="%(asctime)s | %(name)-25s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mindos")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("=" * 60)
    logger.info("  MindOS AI — Starting up...")
    logger.info("=" * 60)

    # Initialize database
    from app.models.database import init_database
    await init_database(settings.DATABASE_URL)
    logger.info("✓ Database initialized")

    # Initialize services
    from app.services.stt_service import init_stt
    from app.services.llm_service import init_llm
    from app.services.tts_service import init_tts
    from app.services.memory_service import init_memory
    from app.services.emotion_service import init_emotion
    from app.services.crisis_service import init_crisis

    init_stt(api_key=settings.OPENAI_API_KEY, model=settings.WHISPER_MODEL)
    logger.info(f"✓ STT Service ({'active' if settings.has_openai else 'mock mode'})")

    init_llm(api_key=settings.OPENAI_API_KEY, model=settings.GPT_MODEL)
    logger.info(f"✓ LLM Service ({'active' if settings.has_openai else 'mock mode'})")

    init_tts(api_key=settings.ELEVENLABS_API_KEY, voice_id=settings.ELEVENLABS_VOICE_ID)
    logger.info(f"✓ TTS Service ({'active' if settings.has_elevenlabs else 'text-only mode'})")

    init_memory(
        pc_key=settings.PINECONE_API_KEY,
        oai_key=settings.OPENAI_API_KEY,
        index=settings.PINECONE_INDEX_NAME,
        model=settings.EMBEDDING_MODEL,
        dims=settings.EMBEDDING_DIMENSIONS,
    )
    logger.info(f"✓ Memory Service ({'Pinecone' if settings.has_pinecone else 'in-memory'})")

    # Emotion model loading can be slow; use keyword fallback in dev
    use_model = settings.APP_ENV != "development"
    init_emotion(use_model=use_model)
    logger.info(f"✓ Emotion Service ({'model' if use_model else 'keyword-based'})")

    init_crisis()
    logger.info("✓ Crisis Service")

    logger.info("=" * 60)
    logger.info("  MindOS AI — Ready! 🧠")
    logger.info(f"  API: http://localhost:8000")
    logger.info(f"  Docs: http://localhost:8000/docs")
    logger.info("=" * 60)

    yield

    # Shutdown
    from app.models.database import close_database
    await close_database()
    logger.info("MindOS AI — Shut down.")


# Create FastAPI app
app = FastAPI(
    title="MindOS AI",
    description="Multimodal AI Mental Health Companion — Voice, Text, Memory, Emotion",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
from app.routers import health, chat, mood, voice

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(mood.router)
app.include_router(voice.router)


@app.get("/")
async def root():
    return {
        "name": "MindOS AI",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }
