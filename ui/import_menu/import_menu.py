from pathlib import Path

from textual import on, work
from textual.binding import Binding
from textual.containers import (
    HorizontalGroup,
    Vertical,
    VerticalGroup,
    VerticalScroll,
)
from textual.screen import Screen
from textual.widgets import (
    Button,
    Collapsible,
    DataTable,
    DirectoryTree,
    Footer,
    Header,
    Static,
)

from application import Application, enable_logger
from models.transactions import Transaction
from services.imports import (
    import_matched,
    import_statement,
    import_words_to_ignore,
)
from services.settings import APP_DIRECTORY, get_setting
from ui.custom_widgets import ConfirmAppendScreen, StatusBox

log = enable_logger()


class ImportMenu(Screen):

    CSS_PATH = "import_menu.tcss"

    BINDINGS = (Binding("q", "back_screen", "Back"),)

    def __init__(self, app: Application, **kwargs):
        super().__init__(id="import-menu", **kwargs)
        self.app_state = app
        self.import_folder = APP_DIRECTORY / get_setting("imports_folder")
        self.loaded_file = None
        self.loaded_file_type = None

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
            yield DataTable(zebra_stripes=True, id="file-preview")

    def action_back_screen(self):
        self.dismiss()

    @on(Button.Pressed)
    async def on_button_pressed(self, event: Button.Pressed):
        match self.loaded_file_type:

            case "statement":
                self.import_statement()

            case "matched":
                pass
                # If a transaction has no account, add too transactions, else payments

            case "accounts":
                pass

            case "history":
                pass

            case "sites":
                pass

            case "ignore":
                self.import_ignore()

    @on(DirectoryTree.FileSelected)
    def on_directiory_tree_file_selected(self, event: DirectoryTree.FileSelected):

        match event.control.id:

            case "statement-tree":
                self.preview_statement(event.path)

            case "matched-tree":
                self.preview_matched(event.path)

            case "accounts-tree":
                self.preview_accounts(event.path)

            case "history-tree":
                self.preview_history(event.path)

            case "site-tree":
                self.preview_site(event.path)

            case "ignore-tree":
                self.preview_ignore(event.path)

    def preview_statement(self, filepath: Path):

        try:
            self.loaded_file = import_statement(str(filepath).removesuffix(".csv"))
        except FileNotFoundError:
            self.notify("File No Longer Exists", severity="error", timeout=5)
            return
        except KeyError:
            self.notify(
                "This File Does Not Contain Statment Information",
                severity="error",
                timeout=5,
            )
            return

        statement_table = self.query_one("#file-preview", DataTable)
        statement_table.clear(columns=True)
        statement_table.add_columns("Date", "Amount", "Transaction Details")

        for row in self.loaded_file:
            statement_table.add_row(row.date, row.amount, row.original_details)

        self.loaded_file_type = "statement"
        self.query_one("#confirm", Button).disabled = False

    def preview_matched(self, filepath: Path):

        if len(self.app_state.state.accounts) == 0:
            self.notify(
                "No Accounts To Match Against. Transactions Will Be Unmatched",
                severity="warning",
                timeout=5,
            )

        try:
            self.loaded_file = import_matched(
                str(filepath).removesuffix(".csv"), self.app_state.state.accounts
            )
        except FileNotFoundError:
            self.notify("File No Longer Exists", severity="error", timeout=5)
            return
        except KeyError:
            self.notify(
                "This File Does Not Contain Statment Information",
                severity="error",
                timeout=5,
            )
            return

        matched_table = self.query_one("#file-preview", DataTable)
        matched_table.clear(columns=True)
        matched_table.add_columns("Date", "Site Number", "Name", "Amount")

        for row in self.loaded_file:
            matched_table.add_row(
                row.date,
                row.account.site_number if row.account is not None else "??",
                row.account.name if row.account is not None else "??",
                row.amount,
            )

        self.loaded_file_type = "matched"
        self.query_one("#confirm", Button).disabled = False

    def preview_accounts(self, filepath: Path):
        account_table = self.query_one("#file-preview", DataTable)
        account_table.clear(columns=True)
        account_table.add_columns("Active", "Name", "Site Number", "Aliases")
        # Mustnt update app_state till balances are imported

    def preview_balances(self, filepath: Path):
        balance_table = self.query_one("#file-preview", DataTable)
        balance_table.clear(columns=True)
        balance_table.add_columns(
            "Site", "Annual Fee", "Remaining", "Outstanding", "Pay Frequency"
        )
        # Mustnt update app_state till accounts are imported

    def preview_history(self, filepath: Path):
        history_table = self.query_one("#file-preview", DataTable)
        history_table.clear(columns=True)
        history_table.add_columns()
        # Complete when importing histoyr is implimented

    def preview_site(self, filepath: Path):
        site_table = self.query_one("#file-preview", DataTable)
        site_table.clear(columns=True)
        site_table.add_columns()
        # Conplete when sites are implimented

    def preview_ignore(self, filepath: Path):

        try:
            self.loaded_file = import_words_to_ignore(
                str(filepath).removesuffix(".csv")
            )
        except FileNotFoundError:
            self.notify("File No Longer Exists", severity="error", timeout=5)
            return
        except KeyError:
            self.notify(
                "This File Does Not Contain Words To Ignore",
                severity="error",
                timeout=5,
            )
            return

        ignore_table = self.query_one("#file-preview", DataTable)
        ignore_table.clear(columns=True)
        ignore_table.add_columns("Word")

        for row in self.loaded_file:
            ignore_table.add_row(row)

        self.loaded_file_type = "ignore"
        self.query_one("#confirm", Button).disabled = False

    @work
    async def import_statement(self):
        assert self.loaded_file is not None
        if len(self.app_state.state.transactions) != 0:

            if get_setting("append_transactions_on_import") == "Never":
                self.app_state.state.clear_transactions()

            elif get_setting("append_transactions_on_import") == "Ask":
                choice = await self.app.push_screen_wait(
                    ConfirmAppendScreen(
                        message="Add To Or Replace Previously Loaded Transactions?"
                    )
                )

                if choice == "replace":
                    self.app_state.state.clear_transactions()
                elif choice is None or choice == "cancel":
                    return

        for transaction in self.loaded_file:
            assert isinstance(transaction, Transaction)
            self.app_state.state.add_transaction(transaction)
            self.query_one("#file-preview", DataTable).clear(columns=True)
            self.query_one("#confirm", Button).disabled = True

    def import_ignore(self):
        assert self.loaded_file is not None
        for word in self.loaded_file:
            assert isinstance(word, str)
            self.app_state.state.add_ignore(word)
            self.query_one("#file-preview", DataTable).clear(columns=True)
            self.query_one("#confirm", Button).disabled = True
