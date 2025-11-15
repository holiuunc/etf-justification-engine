"""FastAPI Server for ETF Justification Engine

Provides API endpoints for:
- Triggering manual analysis
- Checking analysis progress
- Fetching portfolio and analysis data
"""

import logging
import sys
import json
import threading
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="ETF Justification Engine API")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Docker, frontend can access backend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
# server.py is at /app/api/server.py, so .parent.parent gets us to /app
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = Path("/data")
PROGRESS_FILE = DATA_DIR / "analysis_progress.json"
PORTFOLIO_FILE = DATA_DIR / "portfolio" / "current.json"
BACKEND_DIR = PROJECT_ROOT

# Global state for tracking running analysis
analysis_running = False
analysis_thread: Optional[threading.Thread] = None


# ============================================================================
# Pydantic Models
# ============================================================================

class AnalysisStatus(BaseModel):
    running: bool
    progress: float  # 0-100
    message: str
    started_at: Optional[str] = None
    estimated_completion: Optional[str] = None


class StartResponse(BaseModel):
    status: str
    message: str


# ============================================================================
# Helper Functions
# ============================================================================

def get_progress() -> AnalysisStatus:
    """Read current progress from file"""
    try:
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE, 'r') as f:
                data = json.load(f)
                return AnalysisStatus(**data)
        else:
            return AnalysisStatus(
                running=analysis_running,
                progress=0.0,
                message="Idle" if not analysis_running else "Starting..."
            )
    except Exception as e:
        logger.error(f"Error reading progress file: {e}")
        return AnalysisStatus(
            running=analysis_running,
            progress=0.0,
            message="Error reading progress"
        )


def write_progress(progress: float, message: str):
    """Write progress to file"""
    global analysis_running

    try:
        DATA_DIR.mkdir(exist_ok=True)

        data = {
            "running": analysis_running,
            "progress": progress,
            "message": message,
            "started_at": datetime.now().isoformat() if progress == 0 else None,
            "estimated_completion": None  # Could calculate based on progress
        }

        with open(PROGRESS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error writing progress: {e}")


def run_analysis_task():
    """Run the analysis in a separate thread"""
    global analysis_running

    try:
        logger.info("Starting analysis task...")
        analysis_running = True
        write_progress(0, "Starting analysis...")

        # Run main.py as a subprocess
        result = subprocess.run(
            [sys.executable, "main.py"],
            cwd=BACKEND_DIR,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            logger.info("Analysis completed successfully")
            write_progress(100, "Complete!")
        else:
            logger.error(f"Analysis failed: {result.stderr}")
            write_progress(0, f"Error: {result.stderr[:100]}")

    except Exception as e:
        logger.error(f"Error running analysis: {e}")
        write_progress(0, f"Error: {str(e)}")
    finally:
        analysis_running = False


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "name": "ETF Justification Engine API",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.post("/api/analysis/start", response_model=StartResponse)
async def start_analysis(background_tasks: BackgroundTasks):
    """Trigger a new analysis run

    Returns immediately while analysis runs in background.
    Use /api/analysis/progress to check status.
    """
    global analysis_running, analysis_thread

    if analysis_running:
        raise HTTPException(status_code=409, detail="Analysis already running")

    # Start analysis in background thread
    analysis_thread = threading.Thread(target=run_analysis_task, daemon=True)
    analysis_thread.start()

    logger.info("Analysis started in background")

    return StartResponse(
        status="started",
        message="Analysis running in background. Check progress at /api/analysis/progress"
    )


@app.get("/api/analysis/progress", response_model=AnalysisStatus)
async def get_analysis_progress():
    """Get current analysis progress

    Returns progress (0-100) and status message.
    Poll this endpoint to track analysis progress.
    """
    return get_progress()


@app.get("/api/analysis/status")
async def get_analysis_status():
    """Check if analysis is currently running"""
    return {
        "running": analysis_running,
        "last_update": datetime.now().isoformat()
    }


@app.get("/api/portfolio")
async def get_portfolio():
    """Get current portfolio data"""
    try:
        if not PORTFOLIO_FILE.exists():
            raise HTTPException(status_code=404, detail="Portfolio file not found")

        with open(PORTFOLIO_FILE, 'r') as f:
            portfolio_data = json.load(f)

        return portfolio_data
    except Exception as e:
        logger.error(f"Error reading portfolio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analysis/latest")
async def get_latest_analysis():
    """Get most recent analysis results"""
    try:
        analysis_dir = DATA_DIR / "analysis"
        if not analysis_dir.exists():
            raise HTTPException(status_code=404, detail="No analysis found")

        # Find most recent analysis file
        analysis_files = sorted(analysis_dir.glob("*.json"), reverse=True)
        if not analysis_files:
            raise HTTPException(status_code=404, detail="No analysis files found")

        latest_file = analysis_files[0]
        with open(latest_file, 'r') as f:
            analysis_data = json.load(f)

        return analysis_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("ETF Justification Engine API starting...")

    # Ensure data directories exist
    (DATA_DIR / "portfolio").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "analysis").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "transactions").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "cache").mkdir(parents=True, exist_ok=True)

    # Reset progress file
    write_progress(0, "Idle")

    logger.info("API ready at http://localhost:8000")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global analysis_running
    logger.info("Shutting down API...")
    analysis_running = False


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
