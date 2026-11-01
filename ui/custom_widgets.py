from collections.abc import Iterable
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import DirectoryTree, Static

from application import Application


class FolderTree(DirectoryTree):

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [
            path
            for path in paths
            if path.is_dir()
            and not path.name.startswith(".")
            and not path.name.startswith("_")
        ]


class DatabaseTree(DirectoryTree):

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [
            path for path in paths if path.is_dir() and not path.name.startswith("_")
        ]


class StatusBox(VerticalGroup):

    def __init__(self, app: Application, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "Loaded Data"
        self.app_state = app

    def compose(self) -> ComposeResult:

        state = self.app_state.state

        with HorizontalGroup(classes="status-row"):
            yield Static("Unmatched Payments: ", classes="status")
            yield Static(
                str(len(state.transactions)),
                classes="number",
                id="status-transactions",
            )
        with HorizontalGroup(classes="status-row"):
            yield Static("Matched Payments: ", classes="status")
            yield Static(
                str(len(state.payments)), classes="number", id="status-payments"
            )
        with HorizontalGroup(classes="status-row"):
            yield Static("Charges: ", classes="status")
            yield Static(str(len(state.charges)), classes="number", id="status-charges")
        with HorizontalGroup(classes="status-row"):
            yield Static("Sites: ", classes="status")
            yield Static(str(len(state.sites)), classes="number", id="status-sites")
        with HorizontalGroup(classes="status-row"):
            yield Static("Accounts: ", classes="status")
            yield Static(
                str(len(state.accounts)), classes="number", id="status-accounts"
            )
        with HorizontalGroup(classes="status-row"):
            yield Static("Words: ", classes="status")
            yield Static(
                str(len(state.words_to_ignore)),
                classes="number",
                id="status-ignore",
            )
