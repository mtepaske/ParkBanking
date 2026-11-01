from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import (
    Horizontal,
    HorizontalGroup,
    Vertical,
    VerticalGroup,
    VerticalScroll,
)
from textual.screen import Screen
from textual.widgets import Button, Collapsible, Footer, Header, Input, Static

from application import Application
from services.settings import APP_DIRECTORY, get_setting
from ui.custom_widgets import FolderTree


class ExportMenu(Screen):

    BINDINGS = (Binding("q", "back_screen", "Back"),)
    CSS_PATH = "export_menu.tcss"

    def __init__(self, app: Application):
        super().__init__()
        self.app_state = app
        self.export_folder = APP_DIRECTORY / get_setting("exports_folder")

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        with VerticalScroll(classes="section"):
            yield Static("Export Files", classes="section-title")

            with VerticalGroup(id="file-select"):

                with Collapsible(
                    title="Export Matched Transactions",
                    collapsed=True,
                    classes="tree-row",
                    id="statement",
                ):
                    yield FolderTree(
                        str(self.export_folder), classes="tree", id="statement-tree"
                    )

                with Collapsible(
                    title="Export Accounts & Balances",
                    collapsed=True,
                    classes="tree-row",
                    id="accounts",
                ):
                    yield FolderTree(
                        str(self.export_folder), classes="tree", id="accounts-tree"
                    )

                with Collapsible(
                    title="Export Site Information",
                    collapsed=True,
                    classes="tree-row",
                    id="site",
                ):
                    yield FolderTree(
                        str(self.export_folder), classes="tree", id="site-tree"
                    )

                with Collapsible(
                    title="Export Words To Ignore",
                    collapsed=True,
                    classes="tree-row",
                    id="ignore",
                ):
                    yield FolderTree(
                        str(self.export_folder), classes="tree", id="ignore-tree"
                    )

            with Vertical(id="confirm-stack"):

                with Horizontal(id="name-row"):
                    yield Input(placeholder="File Name", disabled=True, id="file-name")

                with Horizontal(id="confirm-row"):
                    yield Button.success(
                        "Export Selected File", disabled=True, id="confirm"
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
