"""
Shared Pattern Database
======================
Central database for Perl and EDA patterns used across all MCP servers.
Provides caching and fast lookup for pattern matching.
"""

import re
from typing import List, Dict, Optional, Any
from datetime import datetime


class PatternDatabase:
    """
    Centralized pattern database with caching for fast lookups.
    Used by all MCP servers to access Perl and EDA patterns.
    """

    def __init__(self):
        self._patterns = {}
        self._cache = {}
        self._last_updated = datetime.now()

    def register_pattern(self, pattern_id: str, pattern_data: Dict):
        """Register a new pattern in the database."""
        self._patterns[pattern_id] = {
            **pattern_data,
            'registered_at': datetime.now().isoformat()
        }

    def get_pattern(self, pattern_id: str) -> Optional[Dict]:
        """Get a pattern by ID."""
        return self._patterns.get(pattern_id)

    def search_patterns(self, category: str = None, severity: str = None) -> List[Dict]:
        """Search patterns by category and/or severity."""
        results = []
        for pid, pdata in self._patterns.items():
            if category and pdata.get('category') != category:
                continue
            if severity and pdata.get('severity') != severity:
                continue
            results.append({'id': pid, **pdata})
        return results

    def match_patterns(self, content: str, pattern_ids: List[str] = None) -> List[Dict]:
        """Match content against registered patterns."""
        matches = []
        targets = pattern_ids if pattern_ids else self._patterns.keys()

        for pid in targets:
            pattern = self._patterns.get(pid)
            if not pattern:
                continue

            regex = pattern.get('pattern')
            if not regex:
                continue

            compiled = re.compile(regex, re.IGNORECASE)
            if compiled.search(content):
                matches.append({
                    'pattern_id': pid,
                    'description': pattern.get('description', ''),
                    'severity': pattern.get('severity', 'info'),
                    'category': pattern.get('category', 'general')
                })

        return matches

    def clear_cache(self):
        """Clear the pattern cache."""
        self._cache.clear()

    @property
    def pattern_count(self) -> int:
        return len(self._patterns)

    @property
    def last_updated(self) -> str:
        return self._last_updated.isoformat()


# Global instance for shared use
_global_db = None


def get_pattern_db() -> PatternDatabase:
    """Get or create the global pattern database instance."""
    global _global_db
    if _global_db is None:
        _global_db = PatternDatabase()
    return _global_db