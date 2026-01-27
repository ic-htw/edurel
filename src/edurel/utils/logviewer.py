"""LogViewer for navigating and displaying hierarchical log files."""

import json
from pathlib import Path
from IPython.display import Markdown, display
from typing import Callable, List, Dict, Any, Optional
from datetime import datetime

from edurel.utils.misc import gslice


class LogViewer:
    """View and filter logs from a 4-level directory hierarchy.

    The directory structure should be:
    log_dir/l1/l2/l3/l4/yyyy_mm_dd___HH_MM_SS.json

    Each JSON file contains a list of objects with "type" and "content" attributes.
    """

    def __init__(self, log_dir: str):
        """Initialize LogViewer.

        Args:
            log_dir: Path to root of 4-level file hierarchy for log files
        """
        self.log_dir = Path(log_dir)
        self.l1_filter: List[str] = ["*"]
        self.l2_filter: List[str] = ["*"]
        self.l3_filter: List[str] = ["*"]
        self.l4_filter: List[str] = ["*"]
        self.entry_filter: Callable[[List[Any]], List[Any]] = gslice(":")
        self.logs: Dict[str, List[Dict[str, Any]]] = {}

    def set_l1_filter(self, filter_list: List[str]) -> None:
        """Set level 1 directory filter.

        Args:
            filter_list: List of directory names or ["*"] for all
        """
        self.l1_filter = filter_list

    def set_l2_filter(self, filter_list: List[str]) -> None:
        """Set level 2 directory filter.

        Args:
            filter_list: List of directory names or ["*"] for all
        """
        self.l2_filter = filter_list

    def set_l3_filter(self, filter_list: List[str]) -> None:
        """Set level 3 directory filter.

        Args:
            filter_list: List of directory names or ["*"] for all
        """
        self.l3_filter = filter_list

    def set_l4_filter(self, filter_list: List[str]) -> None:
        """Set level 4 directory filter.

        Args:
            filter_list: List of directory names or ["*"] for all
        """
        self.l4_filter = filter_list

    def _matches_filter(self, name: str, filter_list: List[str]) -> bool:
        """Check if a directory name matches the filter.

        Args:
            name: Directory name to check
            filter_list: Filter list (["*"] means all)

        Returns:
            True if name matches filter
        """
        return "*" in filter_list or name in filter_list

    def _get_newest_timestamp(self, dir_path: Path) -> Optional[str]:
        """Get the newest timestamp from JSON files in a directory.

        Args:
            dir_path: Path to directory containing JSON files

        Returns:
            Timestamp string or None if no files found
        """
        json_files = list(dir_path.glob("*.json"))
        if not json_files:
            return None

        # Extract timestamps and find newest
        timestamps = []
        for f in json_files:
            stem = f.stem
            # Parse yyyy_mm_dd___HH_MM_SS format
            try:
                dt = datetime.strptime(stem, "%Y_%m_%d___%H_%M_%S")
                timestamps.append((dt, stem))
            except ValueError:
                continue

        if not timestamps:
            return None

        timestamps.sort(reverse=True)
        return timestamps[0][1]

    def set_entry_filter(self, gslice_spec: str) -> None:
        self.entry_filter = gslice(gslice_spec)

    def reset_entry_filter(self) -> None:
        self.entry_filter = gslice(":")

    def read_log(self, timestamps: Optional[List[str]] = None) -> None:
        """Read log files using directory filters.

        Args:
            timestamps: Optional list of timestamps (yyyy_mm_dd___HH_MM_SS).
                       If None, reads only the newest file from each filtered path.
        """
        self.logs = {}

        if not self.log_dir.exists():
            return

        # Navigate 4-level hierarchy
        for l1_dir in self.log_dir.iterdir():
            if not l1_dir.is_dir() or not self._matches_filter(l1_dir.name, self.l1_filter):
                continue

            for l2_dir in l1_dir.iterdir():
                if not l2_dir.is_dir() or not self._matches_filter(l2_dir.name, self.l2_filter):
                    continue

                for l3_dir in l2_dir.iterdir():
                    if not l3_dir.is_dir() or not self._matches_filter(l3_dir.name, self.l3_filter):
                        continue

                    for l4_dir in l3_dir.iterdir():
                        if not l4_dir.is_dir() or not self._matches_filter(l4_dir.name, self.l4_filter):
                            continue

                        # Build path key
                        path_key = f"{l1_dir.name}/{l2_dir.name}/{l3_dir.name}/{l4_dir.name}"

                        # Determine which files to read
                        if timestamps is None:
                            # Read newest file only
                            newest = self._get_newest_timestamp(l4_dir)
                            if newest:
                                files_to_read = [f"{newest}.json"]
                            else:
                                files_to_read = []
                        else:
                            # Read specified timestamps
                            files_to_read = [f"{ts}.json" for ts in timestamps]

                        # Read JSON files
                        log_entries = []
                        for filename in files_to_read:
                            file_path = l4_dir / filename
                            if file_path.exists():
                                try:
                                    with open(file_path, 'r') as f:
                                        data = json.load(f)
                                        if isinstance(data, list):
                                            log_entries.append({
                                                'timestamp': filename[:-5],  # Remove .json
                                                'entries': data
                                            })
                                except (json.JSONDecodeError, IOError):
                                    continue

                        if log_entries:
                            self.logs[path_key] = log_entries

    def md(self) -> str:
        """Turn stored logs into a markdown-formatted string.

        Returns:
            Markdown string containing formatted log entries
        """
        if not self.logs:
            return "No logs to display.\n"

        output = []

        for path_key in sorted(self.logs.keys()):
            log_entries = self.logs[path_key]

            # Header with path
            output.append(f"# {path_key}\n")

            # Display entries from each log file
            for log_file in log_entries:
                timestamp = log_file['timestamp']
                entries = self.entry_filter(log_file['entries'])

                output.append(f"## {timestamp}.json\n")

                # Enumerate objects within log file
                for idx, entry in enumerate(entries, 0):
                    entry_type = entry.get('type', 'unknown')
                    content = entry.get('content', '')

                    output.append(f"### {idx}: {entry_type}")
                    output.append(f"{content}\n")

                output.append("")  # Blank line between files

            output.append("")  # Blank line between paths

        return "\n".join(output)

    def display(self) -> None:
        display(Markdown(self.md()))