"""Storage Operations Module

Handles all file I/O operations for portfolio state, analysis results,
and transaction history using JSON files stored in the data/ directory.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from config.settings import settings
from data.models import (
    PortfolioState, DailyAnalysis, Transaction, TransactionHistory
)

logger = logging.getLogger(__name__)


# ============================================================================
# Portfolio State Operations
# ============================================================================

class PortfolioStorage:
    """Handles portfolio state persistence"""

    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or settings.portfolio_file

    def load(self) -> Optional[PortfolioState]:
        """Load current portfolio state from JSON

        Returns:
            PortfolioState model or None if file doesn't exist
        """
        if not self.file_path.exists():
            logger.warning(f"Portfolio file not found: {self.file_path}")
            return None

        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)

            portfolio = PortfolioState.model_validate(data)
            logger.info(f"Loaded portfolio state (value: ${portfolio.total_value:,.2f})")
            return portfolio

        except Exception as e:
            logger.error(f"Error loading portfolio state: {e}")
            return None

    def save(self, portfolio: PortfolioState) -> bool:
        """Save portfolio state to JSON

        Args:
            portfolio: PortfolioState model to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            # Serialize to JSON
            data = portfolio.model_dump(mode='json')

            # Write to file
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Saved portfolio state to: {self.file_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving portfolio state: {e}")
            return False

    def backup(self, suffix: Optional[str] = None) -> bool:
        """Create a backup of the current portfolio state

        Args:
            suffix: Optional suffix for backup filename (default: timestamp)

        Returns:
            True if successful, False otherwise
        """
        if not self.file_path.exists():
            logger.warning("No portfolio file to backup")
            return False

        try:
            suffix = suffix or datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = self.file_path.with_name(f"current_backup_{suffix}.json")

            with open(self.file_path, 'r') as src:
                data = json.load(src)

            with open(backup_path, 'w') as dst:
                json.dump(data, dst, indent=2)

            logger.info(f"Created portfolio backup: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating portfolio backup: {e}")
            return False


# ============================================================================
# Daily Analysis Operations
# ============================================================================

class AnalysisStorage:
    """Handles daily analysis persistence"""

    def __init__(self, analysis_dir: Optional[Path] = None):
        self.analysis_dir = analysis_dir or settings.analysis_dir

    def save(self, analysis: DailyAnalysis) -> bool:
        """Save daily analysis to JSON file

        Args:
            analysis: DailyAnalysis model to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            self.analysis_dir.mkdir(parents=True, exist_ok=True)

            # Create filename from date
            file_path = self.analysis_dir / f"{analysis.date}.json"

            # Serialize to JSON
            data = analysis.model_dump(mode='json')

            # Write to file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Saved daily analysis to: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving daily analysis: {e}")
            return False

    def load(self, date_str: str) -> Optional[DailyAnalysis]:
        """Load daily analysis for a specific date

        Args:
            date_str: Date string in YYYY-MM-DD format

        Returns:
            DailyAnalysis model or None if not found
        """
        file_path = self.analysis_dir / f"{date_str}.json"

        if not file_path.exists():
            logger.warning(f"Analysis file not found: {file_path}")
            return None

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            analysis = DailyAnalysis.model_validate(data)
            logger.info(f"Loaded daily analysis for {date_str}")
            return analysis

        except Exception as e:
            logger.error(f"Error loading daily analysis: {e}")
            return None

    def load_latest(self) -> Optional[DailyAnalysis]:
        """Load the most recent daily analysis

        Returns:
            DailyAnalysis model or None if no analyses exist
        """
        try:
            # Get all analysis files
            files = sorted(self.analysis_dir.glob("*.json"), reverse=True)

            if not files:
                logger.warning("No analysis files found")
                return None

            # Load most recent
            with open(files[0], 'r') as f:
                data = json.load(f)

            analysis = DailyAnalysis.model_validate(data)
            logger.info(f"Loaded latest analysis: {analysis.date}")
            return analysis

        except Exception as e:
            logger.error(f"Error loading latest analysis: {e}")
            return None

    def load_range(
        self,
        start_date: str,
        end_date: str
    ) -> List[DailyAnalysis]:
        """Load daily analyses within a date range

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of DailyAnalysis models
        """
        analyses = []

        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')

            # Get all files in range
            for file_path in sorted(self.analysis_dir.glob("*.json")):
                date_str = file_path.stem
                try:
                    file_date = datetime.strptime(date_str, '%Y-%m-%d')
                    if start <= file_date <= end:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                        analysis = DailyAnalysis.model_validate(data)
                        analyses.append(analysis)
                except ValueError:
                    continue  # Skip files with invalid date format

            logger.info(f"Loaded {len(analyses)} analyses from {start_date} to {end_date}")
            return analyses

        except Exception as e:
            logger.error(f"Error loading analysis range: {e}")
            return []

    def get_available_dates(self) -> List[str]:
        """Get list of dates with available analyses

        Returns:
            List of date strings (YYYY-MM-DD)
        """
        try:
            dates = []
            for file_path in sorted(self.analysis_dir.glob("*.json")):
                date_str = file_path.stem
                try:
                    # Validate date format
                    datetime.strptime(date_str, '%Y-%m-%d')
                    dates.append(date_str)
                except ValueError:
                    continue

            return dates

        except Exception as e:
            logger.error(f"Error getting available dates: {e}")
            return []


# ============================================================================
# Transaction History Operations
# ============================================================================

class TransactionStorage:
    """Handles transaction history persistence"""

    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or settings.transactions_file

    def load(self) -> Optional[TransactionHistory]:
        """Load transaction history from JSON

        Returns:
            TransactionHistory model or None if file doesn't exist
        """
        if not self.file_path.exists():
            logger.warning(f"Transaction file not found: {self.file_path}")
            return TransactionHistory(transactions=[], summary={})

        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)

            history = TransactionHistory.model_validate(data)
            logger.info(f"Loaded transaction history ({len(history.transactions)} transactions)")
            return history

        except Exception as e:
            logger.error(f"Error loading transaction history: {e}")
            return TransactionHistory(transactions=[], summary={})

    def save(self, history: TransactionHistory) -> bool:
        """Save transaction history to JSON

        Args:
            history: TransactionHistory model to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            # Serialize to JSON
            data = history.model_dump(mode='json')

            # Write to file
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Saved transaction history to: {self.file_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving transaction history: {e}")
            return False

    def append_transaction(self, transaction: Transaction) -> bool:
        """Append a single transaction to history

        Args:
            transaction: Transaction model to append

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing history
            history = self.load()

            # Add new transaction
            history.add_transaction(transaction)

            # Save updated history
            return self.save(history)

        except Exception as e:
            logger.error(f"Error appending transaction: {e}")
            return False

    def get_transactions_by_ticker(self, ticker: str) -> List[Transaction]:
        """Get all transactions for a specific ticker

        Args:
            ticker: ETF ticker symbol

        Returns:
            List of Transaction models
        """
        history = self.load()
        if history is None:
            return []

        return [txn for txn in history.transactions if txn.ticker == ticker]

    def get_transactions_by_date_range(
        self,
        start_date: str,
        end_date: str
    ) -> List[Transaction]:
        """Get transactions within a date range

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of Transaction models
        """
        history = self.load()
        if history is None:
            return []

        return [
            txn for txn in history.transactions
            if start_date <= txn.date <= end_date
        ]


# ============================================================================
# Cache Operations
# ============================================================================

class CacheStorage:
    """Handles cache file operations"""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or settings.cache_dir

    def save_json(self, filename: str, data: Dict) -> bool:
        """Save data to cache as JSON

        Args:
            filename: Name of cache file
            data: Data to cache

        Returns:
            True if successful, False otherwise
        """
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            file_path = self.cache_dir / filename

            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            logger.debug(f"Saved cache: {filename}")
            return True

        except Exception as e:
            logger.error(f"Error saving cache {filename}: {e}")
            return False

    def load_json(self, filename: str) -> Optional[Dict]:
        """Load data from cache

        Args:
            filename: Name of cache file

        Returns:
            Cached data or None if not found
        """
        file_path = self.cache_dir / filename

        if not file_path.exists():
            logger.debug(f"Cache not found: {filename}")
            return None

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            logger.debug(f"Loaded cache: {filename}")
            return data

        except Exception as e:
            logger.error(f"Error loading cache {filename}: {e}")
            return None


# ============================================================================
# Convenience Functions
# ============================================================================

# Global storage instances
portfolio_storage = PortfolioStorage()
analysis_storage = AnalysisStorage()
transaction_storage = TransactionStorage()
cache_storage = CacheStorage()
