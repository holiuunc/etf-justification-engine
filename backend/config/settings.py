"""Environment Settings Configuration

Loads environment variables and provides application-wide settings.
Uses pydantic-settings for type-safe configuration management.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Keys
    newsapi_key: str
    gemini_api_key: str

    # GitHub Configuration (for data storage)
    github_repo: str = "username/etf-justification-engine"
    github_raw_base: str = "https://raw.githubusercontent.com/username/etf-justification-engine/main/data"

    # Portfolio Configuration
    initial_capital: float = 100000.00
    portfolio_start_date: str = "2025-09-29"

    # Market Data Configuration
    market_data_period: str = "90d"
    vix_ticker: str = "^VIX"
    benchmark_ticker: str = "SPY"

    # API Rate Limiting
    rate_limit_delay: float = 1.0        # Seconds between API calls
    max_retries: int = 3
    retry_delay: float = 2.0

    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "analysis.log"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # File Paths (relative to project root)
    # settings.py is at /app/config/settings.py, so .parent.parent gets us to /app
    project_root: Path = Path(__file__).parent.parent
    data_dir: Path = Path("/data")
    portfolio_dir: Path = data_dir / "portfolio"
    analysis_dir: Path = data_dir / "analysis"
    transactions_dir: Path = data_dir / "transactions"
    cache_dir: Path = data_dir / "cache"

    # Analysis Timing
    analysis_timezone: str = "America/New_York"
    analysis_time: str = "16:30"  # 4:30 PM ET

    # Feature Flags
    enable_news_analysis: bool = True
    enable_llm_analysis: bool = True
    enable_prospectus_generation: bool = True

    # Model configuration for pydantic-settings v2
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create data directories if they don't exist
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist"""
        directories = [
            self.data_dir,
            self.portfolio_dir,
            self.analysis_dir,
            self.transactions_dir,
            self.cache_dir,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @property
    def portfolio_file(self) -> Path:
        """Path to current portfolio state file"""
        return self.portfolio_dir / "current.json"

    @property
    def transactions_file(self) -> Path:
        """Path to transaction history file"""
        return self.transactions_dir / "history.json"

    @property
    def etf_metadata_file(self) -> Path:
        """Path to ETF metadata cache file"""
        return self.cache_dir / "etf_metadata.json"

    def get_analysis_file(self, date_str: str) -> Path:
        """Get path to analysis file for a specific date

        Args:
            date_str: Date string in YYYY-MM-DD format

        Returns:
            Path to analysis file
        """
        return self.analysis_dir / f"{date_str}.json"

    @property
    def newsapi_available(self) -> bool:
        """Check if NewsAPI key is configured"""
        return bool(self.newsapi_key)

    @property
    def gemini_available(self) -> bool:
        """Check if Gemini API key is configured"""
        return bool(self.gemini_api_key)

    def validate_configuration(self) -> tuple[bool, list[str]]:
        """Validate that required configuration is present

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        if not self.newsapi_key:
            errors.append("NEWSAPI_KEY not configured")

        if not self.gemini_api_key:
            errors.append("GEMINI_API_KEY not configured")

        if not self.data_dir.exists():
            errors.append(f"Data directory does not exist: {self.data_dir}")

        return len(errors) == 0, errors


# Global settings instance
settings = Settings()


# Export commonly used paths
PROJECT_ROOT = settings.project_root
DATA_DIR = settings.data_dir
PORTFOLIO_FILE = settings.portfolio_file
TRANSACTIONS_FILE = settings.transactions_file
ETF_METADATA_FILE = settings.etf_metadata_file
