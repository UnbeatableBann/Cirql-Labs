from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from scalar_fastapi import get_scalar_api_reference

from app.api import router
from app.middleware import setup_cors
from app.storage import check_db_connection, init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

# Configure CORS middleware
setup_cors(app)

# Include API routers with prefixes and tags for documentation
app.include_router(router, prefix="/api", tags=["Routes"])


@app.get("/", summary="Health check endpoint", description="Check API health and SQLite connectivity.")
async def health_check():
    """
    Simple health check endpoint.

    Returns:
    - {"status": "ok"} if SQLite is connected.
    - {"status": "SQLite not working."} if SQLite is unavailable.
    """
    ping = await check_db_connection()
    if not ping:
        return {"status": "SQLite not working."}
    return {"status": "ok"}


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    """
    Return the Scalar API reference.

    This endpoint is hidden from OpenAPI/Swagger docs (`include_in_schema=False`).
    """
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar"
    )
