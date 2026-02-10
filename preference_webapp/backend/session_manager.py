"""
Session manager for persisting active learning sessions.

Handles saving, loading, and managing multiple preference learning sessions.
"""

import logging
import pickle
import uuid
from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages persistence of active learning sessions.

    Attributes:
        sessions_dir: Directory to store session files
    """

    def __init__(self, sessions_dir: str = "data/sessions"):
        """
        Initialize session manager.

        Args:
            sessions_dir: Directory to store session files
        """
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"SessionManager initialized with directory: {self.sessions_dir}")

    def create_session(self, config: Dict[str, Any]) -> str:
        """
        Create a new session with unique ID.

        Args:
            config: Session configuration dictionary

        Returns:
            Session ID string

        Example:
            >>> manager = SessionManager()
            >>> config = {'period': 'bronze_age', 'n_masks': 100}
            >>> session_id = manager.create_session(config)
            >>> print(f"Created session: {session_id}")
        """
        # Generate unique ID with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = config.get('session_prefix', 'session')
        session_id = f"{prefix}_{timestamp}"

        # Create session dictionary
        session = {
            'session_id': session_id,
            'config': config,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'preferences': [],  # List of ((i, j), pref) tuples
            'iteration': 0,
            'total_comparisons': 0,
            'model': None,
            'likelihood': None,
            'scaler': None,
            'features': None,
            'ranking': None,
            'scores': None,
            'converged': False,
            'history': [],  # Track iterations and rankings
        }

        # Save session
        self.save_session(session_id, session)

        logger.info(f"Created new session: {session_id}")
        return session_id

    def save_session(self, session_id: str, session: Dict[str, Any]) -> None:
        """
        Save session to pickle file.

        Args:
            session_id: Session identifier
            session: Session dictionary

        Example:
            >>> manager = SessionManager()
            >>> manager.save_session('session_20250129_130000', session)
        """
        session_path = self.sessions_dir / f"{session_id}.pkl"

        # Update timestamp
        session['updated_at'] = datetime.now().isoformat()

        with open(session_path, 'wb') as f:
            pickle.dump(session, f)

        logger.debug(f"Saved session: {session_id}")

    def load_session(self, session_id: str) -> Dict[str, Any]:
        """
        Load session from pickle file.

        Args:
            session_id: Session identifier

        Returns:
            Session dictionary

        Raises:
            FileNotFoundError: If session not found

        Example:
            >>> manager = SessionManager()
            >>> session = manager.load_session('session_20250129_130000')
        """
        session_path = self.sessions_dir / f"{session_id}.pkl"

        if not session_path.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")

        with open(session_path, 'rb') as f:
            session = pickle.load(f)

        logger.debug(f"Loaded session: {session_id}")
        return session

    def list_sessions(self) -> List[str]:
        """
        List all available sessions.

        Returns:
            List of session IDs

        Example:
            >>> manager = SessionManager()
            >>> sessions = manager.list_sessions()
            >>> print(f"Found {len(sessions)} sessions")
        """
        session_files = list(self.sessions_dir.glob("*.pkl"))
        session_ids = [f.stem for f in session_files]
        return sorted(session_ids)

    def delete_session(self, session_id: str) -> None:
        """
        Delete a session.

        Args:
            session_id: Session identifier

        Raises:
            FileNotFoundError: If session not found

        Example:
            >>> manager = SessionManager()
            >>> manager.delete_session('session_20250129_130000')
        """
        session_path = self.sessions_dir / f"{session_id}.pkl"

        if not session_path.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")

        session_path.unlink()
        logger.info(f"Deleted session: {session_id}")

    def auto_backup(self, session: Dict[str, Any], n: int = 5) -> bool:
        """
        Auto-backup session every N comparisons.

        Args:
            session: Session dictionary
            n: Backup frequency (every N comparisons)

        Returns:
            True if backup was created, False otherwise

        Example:
            >>> manager = SessionManager()
            >>> session = manager.load_session('session_20250129_130000')
            >>> if manager.auto_backup(session, n=5):
            ...     print("Backup created")
        """
        total_comparisons = session.get('total_comparisons', 0)

        # Check if we should backup
        if total_comparisons > 0 and total_comparisons % n == 0:
            session_id = session['session_id']

            # Create backup
            backup_id = f"{session_id}_backup_{total_comparisons}"
            backup_path = self.sessions_dir / f"{backup_id}.pkl"

            with open(backup_path, 'wb') as f:
                pickle.dump(session, f)

            logger.info(f"Auto-backup created: {backup_id}")
            return True

        return False

    def cleanup_old_backups(self, session_id: str, keep: int = 5) -> None:
        """
        Clean up old backups for a session.

        Args:
            session_id: Base session ID
            keep: Number of most recent backups to keep

        Example:
            >>> manager = SessionManager()
            >>> manager.cleanup_old_backups('session_20250129_130000', keep=3)
        """
        # Find all backup files for this session
        backup_pattern = f"{session_id}_backup_*"
        backup_files = list(self.sessions_dir.glob(backup_pattern))

        if len(backup_files) <= keep:
            return

        # Sort by modification time (oldest first)
        backup_files.sort(key=lambda f: f.stat().st_mtime)

        # Delete oldest backups
        for backup_file in backup_files[:-keep]:
            backup_file.unlink()
            logger.info(f"Deleted old backup: {backup_file.stem}")

    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get summary information about a session without loading full session.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with session metadata

        Example:
            >>> manager = SessionManager()
            >>> info = manager.get_session_info('session_20250129_130000')
            >>> print(f"Session has {info['total_comparisons']} comparisons")
        """
        session_path = self.sessions_dir / f"{session_id}.pkl"

        if not session_path.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")

        # Load session
        with open(session_path, 'rb') as f:
            session = pickle.load(f)

        # Extract metadata
        info = {
            'session_id': session['session_id'],
            'created_at': session['created_at'],
            'updated_at': session['updated_at'],
            'total_comparisons': session.get('total_comparisons', 0),
            'iteration': session.get('iteration', 0),
            'converged': session.get('converged', False),
            'config': session.get('config', {}),
            'file_size_mb': session_path.stat().st_size / (1024 * 1024),
        }

        return info

    def list_sessions_info(self) -> List[Dict[str, Any]]:
        """
        List summary information for all sessions.

        Returns:
            List of session info dictionaries

        Example:
            >>> manager = SessionManager()
            >>> sessions = manager.list_sessions_info()
            >>> for s in sessions:
            ...     print(f"{s['session_id']}: {s['total_comparisons']} comparisons")
        """
        session_ids = self.list_sessions()
        infos = []

        for session_id in session_ids:
            try:
                info = self.get_session_info(session_id)
                infos.append(info)
            except Exception as e:
                logger.warning(f"Failed to get info for session {session_id}: {e}")

        # Sort by updated_at (most recent first)
        infos.sort(key=lambda x: x['updated_at'], reverse=True)
        return infos
