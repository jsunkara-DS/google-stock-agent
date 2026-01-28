import logging
from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class StorageService:
    """Handle data persistence for stock analysis results."""

    def __init__(self, use_firestore: bool = False, credentials_path: Optional[str] = None):
        self.use_firestore = use_firestore
        self.credentials_path = credentials_path
        self.firebase_app = None
        self.db = None
        
        # Local storage fallback
        self.local_storage_dir = Path("data")
        self.local_storage_dir.mkdir(exist_ok=True)
        
        if use_firestore and credentials_path:
            self._init_firestore()
        else:
            logger.info("Using local file storage (Firestore not configured)")

    def _init_firestore(self):
        """Initialize Firebase/Firestore connection."""
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore

            if not firebase_admin._apps:
                cred = credentials.Certificate(self.credentials_path)
                self.firebase_app = firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            logger.info("Firestore initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore: {e}")
            logger.info("Falling back to local storage")
            self.use_firestore = False

    def save_analysis(self, analysis_data: Dict) -> bool:
        """
        Save analysis results.
        
        Args:
            analysis_data: Dict containing symbol, price, change, analysis text, etc.
            
        Returns:
            True if successful, False otherwise
        """
        if self.use_firestore and self.db:
            return self._save_to_firestore(analysis_data)
        else:
            return self._save_to_local_storage(analysis_data)

    def _save_to_firestore(self, analysis_data: Dict) -> bool:
        """Save to Firestore."""
        try:
            symbol = analysis_data.get("symbol")
            if not symbol:
                logger.error("Cannot save: missing symbol")
                return False

            # Create a new document with timestamp
            doc_ref = self.db.collection("stock_analysis").document(
                f"{symbol}_{datetime.now().isoformat()}"
            )
            doc_ref.set(analysis_data)
            
            logger.info(f"Saved {symbol} analysis to Firestore")
            return True
        except Exception as e:
            logger.error(f"Failed to save to Firestore: {e}")
            return False

    def _save_to_local_storage(self, analysis_data: Dict) -> bool:
        """Save to local JSON file."""
        try:
            symbol = analysis_data.get("symbol")
            if not symbol:
                logger.error("Cannot save: missing symbol")
                return False

            # Create symbol directory
            symbol_dir = self.local_storage_dir / symbol
            symbol_dir.mkdir(exist_ok=True)

            # Save with timestamp
            timestamp = datetime.now().isoformat().replace(":", "-")
            file_path = symbol_dir / f"analysis_{timestamp}.json"

            with open(file_path, "w") as f:
                json.dump(analysis_data, f, indent=2, default=str)

            logger.info(f"Saved {symbol} analysis to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save to local storage: {e}")
            return False

    def save_batch_analysis(self, batch_results: Dict[str, Dict]) -> int:
        """
        Save multiple analysis results.
        
        Args:
            batch_results: Dict mapping symbol to analysis data
            
        Returns:
            Number of successfully saved analyses
        """
        saved_count = 0
        for symbol, analysis_data in batch_results.items():
            if self.save_analysis(analysis_data):
                saved_count += 1
        
        logger.info(f"Saved {saved_count}/{len(batch_results)} analyses")
        return saved_count

    def get_latest_analysis(self, symbol: str) -> Optional[Dict]:
        """Retrieve the latest analysis for a symbol."""
        if self.use_firestore and self.db:
            return self._get_from_firestore(symbol)
        else:
            return self._get_from_local_storage(symbol)

    def _get_from_firestore(self, symbol: str) -> Optional[Dict]:
        """Get latest analysis from Firestore."""
        try:
            query = (
                self.db.collection("stock_analysis")
                .where("symbol", "==", symbol)
                .order_by("timestamp", direction="DESCENDING")
                .limit(1)
            )
            docs = query.stream()
            for doc in docs:
                return doc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve from Firestore: {e}")
            return None

    def _get_from_local_storage(self, symbol: str) -> Optional[Dict]:
        """Get latest analysis from local storage."""
        try:
            symbol_dir = self.local_storage_dir / symbol
            if not symbol_dir.exists():
                return None

            # Get the most recent file
            files = sorted(symbol_dir.glob("analysis_*.json"), reverse=True)
            if not files:
                return None

            with open(files[0], "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to retrieve from local storage: {e}")
            return None

    def list_all_analyses(self, limit: int = 10) -> List[Dict]:
        """List recent analyses across all symbols."""
        if self.use_firestore and self.db:
            return self._list_from_firestore(limit)
        else:
            return self._list_from_local_storage(limit)

    def _list_from_firestore(self, limit: int) -> List[Dict]:
        """List from Firestore."""
        try:
            query = (
                self.db.collection("stock_analysis")
                .order_by("timestamp", direction="DESCENDING")
                .limit(limit)
            )
            return [doc.to_dict() for doc in query.stream()]
        except Exception as e:
            logger.error(f"Failed to list from Firestore: {e}")
            return []

    def _list_from_local_storage(self, limit: int) -> List[Dict]:
        """List from local storage."""
        try:
            all_files = []
            for symbol_dir in self.local_storage_dir.glob("*/"):
                all_files.extend(symbol_dir.glob("analysis_*.json"))

            # Sort by modification time, newest first
            all_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            results = []
            for file_path in all_files[:limit]:
                try:
                    with open(file_path, "r") as f:
                        results.append(json.load(f))
                except Exception as e:
                    logger.warning(f"Failed to read {file_path}: {e}")

            return results
        except Exception as e:
            logger.error(f"Failed to list from local storage: {e}")
            return []
