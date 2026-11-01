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


class ImportMenu(Screen):

    CSS_PATH = "import_menu.tcss"

    BINDINGS = Binding("q", "back_screen", "Back")

    def __init__(self, app: Application):
        super().__init__()
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

            with VerticalGroup(id="app-status") as box:
                box.border_title = "Loaded Data"
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
                    yield Static(
                        str(len(state.charges)), classes="number", id="status-charges"
                    )
                with HorizontalGroup(classes="status-row"):
                    yield Static("Sites: ", classes="status")
                    yield Static(
                        str(len(state.sites)), classes="number", id="status-sites"
                    )
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

        with Vertical(classes="section"):

            yield Static("File Preview", classes="section-title")

    def action_back_screen(self):
        self.dismiss()
