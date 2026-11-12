from collections.abc import Iterable
from pathlib import Path

from textual.widgets import (
    DirectoryTree,
)


class FolderTree(DirectoryTree):
    """A directory tree to display folders"""

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        """
        Filter the display to display only folders

        Args:
            paths: The paths in the current working directory

        Returns:
            The paths of only folders
        """

        return [
            path
            for path in paths
            if path.is_dir()
            and not path.name.startswith(".")
            and not path.name.startswith("_")
        ]


class DatabaseTree(DirectoryTree):
    """A directory tree to display only folders but also hidden folders"""

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        """
        Filter display to show folders and hidden folders

        Args:
            paths: The paths in the current working directory

        Returns:
            The paths of folders and hidden folders
        """

        return [
            path for path in paths if path.is_dir() and not path.name.startswith("_")
        ]
