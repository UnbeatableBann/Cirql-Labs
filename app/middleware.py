from app.config import settings
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware


def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_CONNECTION],   # Required for frontend connection
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Restrict allowed hosts
    if getattr(settings, "ALLOWED_HOSTS", None):
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,  # Required for host connection
        )
