"""
Health check endpoints
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from ..schemas.health import HealthResponse

# Optional dependency on the DB package
try:
    from db import DatabaseService, get_db_service
except ImportError:
    # DB package not available during some local dev flows
    DatabaseService = None
    get_db_service = None

# Capture API service startup time
API_START_TIME = datetime.now(UTC)

router = APIRouter()


@router.get('/', response_model=list[HealthResponse])
async def health_check(
    db_service: DatabaseService | None = Depends(get_db_service)
    if get_db_service
    else None,
) -> list[HealthResponse]:
    """Health check endpoint with dependency injection"""
    api_response = HealthResponse(
        name='API',
        status='healthy',
        message='API is running',
        version='0.0.0',
        start_time=API_START_TIME.isoformat(),
    )

    # Get database health using dependency injection
    responses = [api_response]
    if db_service:
        db_health = await db_service.health_check()
        db_response = HealthResponse(**db_health)
        responses.append(db_response)

    return responses
