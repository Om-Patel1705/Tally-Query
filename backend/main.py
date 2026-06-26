from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
import logging.config
from app.core.middleware import add_cors
from app.routers import upload, query, session, health
from app.session.store import start_cleanup_task

# Configure logging
logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout"
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["default"]
    },
    "loggers": {
        "app": {
            "level": "DEBUG",
            "handlers": ["default"],
            "propagate": False
        }
    }
})

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background cleanup task
    logger.info("Starting TallyQuery API...")
    start_cleanup_task()
    yield
    logger.info("Shutting down TallyQuery API...")


app = FastAPI(title="TallyQuery API", lifespan=lifespan)

# Add CORS middleware
add_cors(app)

# Register routers
app.include_router(upload.router, prefix="/upload", tags=["upload"])
app.include_router(query.router, prefix="/query", tags=["query"])
app.include_router(session.router, prefix="/session", tags=["session"])
app.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
