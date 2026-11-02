from textual.binding import Binding
from textual.containers import (
    HorizontalGroup,
    Vertical,
    VerticalGroup,
    VerticalScroll,
)
from textual.screen import Screen
from textual.widgets import Button, Collapsible, DirectoryTree, Footer, Header, Static

from application import Application
from services.settings import APP_DIRECTORY, get_setting
from ui.custom_widgets import StatusBox


class ImportMenu(Screen):

    CSS_PATH = "import_menu.tcss"

    BINDINGS = (Binding("q", "back_screen", "Back"),)

    def __init__(self, app: Application, **kwargs):
        super().__init__(id="import-menu", **kwargs)
        self.app_state = app
        self.import_folder = APP_DIRECTORY / get_setting("imports_folder")

    def compose(self):
        yield Header()
        yield Footer()

        with VerticalScroll(classes="section"):

            yield Static("Import Files", classes="section-title")

            with VerticalGroup(id="file-select"):

                with Collapsible(
                    title="Import Bank Statement",
                    collapsed=True,
                    classes="tree-row",
                    id="statement",
                ):
                    yield DirectoryTree(
                        str(self.import_folder), classes="tree", id="statement-tree"
                    )

                with Collapsible(
                    title="Import Previously Matched Transactions",
                    collapsed=True,
                    classes="tree-row",
                    id="matched",
                ):
                    yield DirectoryTree(
                        str(self.import_folder), classes="tree", id="matched-tree"
                    )

                with Collapsible(
                    title="Import Accounts & Balances",
                    collapsed=True,
                    classes="tree-row",
                    id="accounts",
                ):
                    yield DirectoryTree(
                        str(self.import_folder), classes="tree", id="accounts-tree"
                    )

                with Collapsible(
                    title="Import Account History",
                    collapsed=True,
                    classes="tree-row",
                    id="history",
                ):
                    yield DirectoryTree(
                        str(self.import_folder), classes="tree", id="history-tree"
                    )

                with Collapsible(
                    title="Import Site Information",
                    collapsed=True,
                    classes="tree-row",
                    id="site",
                ):
                    yield DirectoryTree(
                        str(self.import_folder), classes="tree", id="site-tree"
                    )

                with Collapsible(
                    title="Import Words To Ignore",
                    collapsed=True,
                    classes="tree-row",
                    id="ignore",
                ):
                    yield DirectoryTree(
                        str(self.import_folder), classes="tree", id="ignore-tree"
                    )

            with HorizontalGroup(id="confirm-row"):
                yield Button.success(
                    "Import Selected File", disabled=True, id="confirm"
                )

            yield StatusBox(self.app_state, id="app-status")

        with Vertical(classes="section"):

            yield Static("File Preview", classes="section-title")

    def action_back_screen(self):
        self.dismiss()
