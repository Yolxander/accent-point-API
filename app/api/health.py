"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from app.core.config import settings
from app.services.database_service import db_service
import psutil
import os

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "OpenVoice API",
        "version": "1.0.0"
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with system metrics"""
    
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Check if required directories exist
    dirs_status = {
        "temp_dir": os.path.exists(settings.TEMP_DIR),
        "upload_dir": os.path.exists(settings.UPLOAD_DIR),
        "output_dir": os.path.exists(settings.OUTPUT_DIR)
    }
    
    # Check OpenVoice availability
    try:
        import openvoice_cli.__main__ as openvoice_main
        openvoice_available = True
    except ImportError:
        openvoice_available = False
    
    # Check Supabase connectivity
    try:
        supabase_connected = await db_service.test_connection()
    except Exception:
        supabase_connected = False
    
    # Overall health status
    all_checks_passed = all(dirs_status.values()) and openvoice_available and supabase_connected
    status = "healthy" if all_checks_passed else "degraded"
    
    return {
        "status": status,
        "service": "OpenVoice API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2)
        },
        "directories": dirs_status,
        "openvoice_available": openvoice_available,
        "supabase_connected": supabase_connected
    }
