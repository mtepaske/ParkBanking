from textual.containers import Horizontal, HorizontalGroup, VerticalGroup
from textual.screen import Screen
from textual.widgets import Button, Collapsible, DirectoryTree, Footer, Header, Static

from application import Application
from services.settings import APP_DIRECTORY, get_setting


class ImportMenu(Screen):

    CSS_PATH = "import_menu.tcss"

    def __init__(self, app: Application):
        super().__init__()
        self.app_state = app
        self.import_folder = APP_DIRECTORY / get_setting("imports_folder")

    def compose(self):
        yield Header()
        yield Footer()

        with Horizontal():

            with VerticalGroup(classes="section"):

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

                state = self.app_state.state

                with VerticalGroup(id="app-status"):

                    with HorizontalGroup(classes="status-box"):
                        yield Static(
                            f"Loaded Unmatched Payments: {len(state.transactions)}",
                            classes="status",
                            id="transactions",
                        )
                    with HorizontalGroup(classes="status-box"):
                        yield Static(
                            f"Loaded Matched Payments: {len(state.payments)}",
                            classes="status",
                            id="status-payments",
                        )
                    with HorizontalGroup(classes="status-box"):
                        yield Static(
                            f"Loaded Charges: {len(state.charges)}",
                            id="status-charges",
                            classes="status",
                        )
                    with HorizontalGroup(classes="status-box"):
                        yield Static(
                            f"Loaded Sites: {len(state.sites)}",
                            id="status-sites",
                            classes="status",
                        )
                    with HorizontalGroup(classes="status-box"):
                        yield Static(
                            f"Loaded Accounts: {len(state.accounts)}",
                            id="status-accounts",
                            classes="status",
                        )
                    with HorizontalGroup(classes="status-box"):
                        yield Static(
                            f"Loaded Words To Ignore: {len(state.words_to_ignore)}",
                            id="status-ignore",
                            classes="status",
                        )

            with VerticalGroup(classes="section"):

                yield Static("File Preview", classes="section-title")
