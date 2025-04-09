from fastapi import APIRouter
from app.api.endpoints import test_endpoints

api_router = APIRouter()

# Inclusão dos endpoints de teste
api_router.include_router(test_endpoints.router, prefix="/tests", tags=["tests"])
