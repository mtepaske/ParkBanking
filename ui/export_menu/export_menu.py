from typing import cast

from textual import on, work
from textual.app import ComposeResult
from textual.containers import (
    Horizontal,
    Vertical,
    VerticalScroll,
)
from textual.widgets import Button, Collapsible, DataTable, DirectoryTree, Input, Static

from models.account import Account
from models.balance import Balance
from models.transactions import Transaction, match_transaction_on_account_id
from services.date import get_today
from services.exports import (
    export_accounts_to_csv,
    export_balances_to_csv,
    export_ignore_to_csv,
    export_payments_to_csv,
)
from services.settings import APP_DIRECTORY, get_setting
from ui.custom_widgets import FolderTree, Menu, SelectDateRange, StatusBox


class ExportMenu(Menu):
    """
    A menu to export current state as files

    Attributes:
        CSS_PATH: (str) The name of the file containing styling information for the app
        export_folder: (Path) The path of the folder to export too
    """

    CSS_PATH = "export_menu.tcss"

    def __init__(self, **kwargs):
        """Initialise the menu"""
        super().__init__(**kwargs)
        self.export_folder = APP_DIRECTORY / get_setting("exports_folder")
        self.loaded_file = None
        self.loaded_file_type = None

    def compose(self) -> ComposeResult:
        """Construct the widgets on the screen"""

        yield from super().compose()

        # File selection section
        with VerticalScroll(classes="section"):
            yield Static("Export Files", classes="section-title")

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
                title="Export Accounts",
                collapsed=True,
                classes="tree-row",
                id="accounts",
            ):
                yield FolderTree(
                    str(self.export_folder), classes="tree", id="accounts-tree"
                )

            with Collapsible(
                title="Export Balances",
                collapsed=True,
                classes="tree-row",
                id="balances",
            ):
                yield FolderTree(
                    str(self.export_folder), classes="tree", id="balances-tree"
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

            with Horizontal(classes="row"):
                yield Input(placeholder="File Name", disabled=True, id="file-name")

            with Horizontal(classes="row"):
                yield Button.success(
                    "Export Selected File", disabled=True, id="confirm"
                )

            yield StatusBox(app_state=self.app_state)

        # File preview
        with Vertical(classes="section"):

            yield Static("File Preview", classes="section-title")
            yield DataTable(zebra_stripes=True, id="file-preview")

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed):

        if event.button.id == "confirm":

            filename = self.query_one("#file-name", Input).value
            if filename == "":
                self.notify("Please Enter A File Name", severity="warning", timeout=5)
                return

            match self.loaded_file_type:

                case "statement":
                    self.export_statement(filename)

                case "accounts":
                    self.export_accounts(filename)

                case "balances":
                    self.export_balances(filename)

                case "site":
                    self.export_sites(filename)

                case "ignore":
                    self.export_ignore(filename)

    @on(DirectoryTree.DirectorySelected)
    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ):

        match event.control.id:

            case "statement-tree":
                self.preview_statement()

            case "accounts-tree":
                self.preview_accounts()

            case "balances-tree":
                self.preview_balances()

            case "site-tree":
                self.preview_sites()

            case "ignore-tree":
                self.preview_ignore()

    def set_default_filename(self):

        today = get_today()

        match self.loaded_file_type:

            case "statement":
                self.query_one("#file-name", Input).value = (
                    f"{today.month} {today.year} - Statement"
                )

            case "accounts":
                self.query_one("#file-name", Input).value = (
                    f"{today.month} {today.year} - Accounts"
                )

            case "balances":
                self.query_one("#file-name", Input).value = (
                    f"{today.month} {today.year} - Balances"
                )

            case "site":
                self.query_one("#file-name", Input).value = (
                    f"{today.month} {today.year} - Sites"
                )

            case "ignore":
                self.query_one("#file-name", Input).value = "Words To Ignore"

    @work
    async def preview_statement(self):

        date_range = await self.app.push_screen_wait(
            SelectDateRange("Select The Date Range Of The Statement")
        )

        if date_range is None:
            self.notify("Statement Import Cancelled", severity="warning", timeout=5)
            return

        start_date, end_date = date_range

        self.loaded_file = self.app_state.repos.account_repo.get_payments_by_range(
            start=start_date, end=end_date
        )

        for payment in self.app_state.state.payments:
            if payment.date >= start_date and payment.date <= end_date:
                self.loaded_file.append(payment)

        self.loaded_file.sort(key=lambda t: t.date)

        for transaction in self.loaded_file:
            match_transaction_on_account_id(
                transaction=transaction, accounts=self.app_state.state.accounts
            )

        statement_table = self.query_one("#file-preview", DataTable)
        statement_table.clear(columns=True)
        statement_table.add_columns(
            "Date", "Site Number", "Name", "Amount", "Description", "Transaction ID"
        )

        for row in self.loaded_file:
            statement_table.add_row(
                row.date,
                row.account.site_number if row.account is not None else "??",
                row.account.name if row.account is not None else "??",
                row.amount,
                row.type,
                row.transaction_id if row.transaction_id is not None else "None",
            )

        self.loaded_file_type = "statement"
        self.query_one("#confirm", Button).disabled = False
        self.query_one("#file-name", Input).disabled = False
        self.set_default_filename()

    def preview_accounts(self):

        self.loaded_file = self.app_state.state.accounts

        account_table = self.query_one("#file-preview", DataTable)
        account_table.clear(columns=True)
        account_table.add_columns(
            "Site Number", "Name", "Aliases", "Active", "Account ID", "Balance ID"
        )

        for row in self.loaded_file:
            account_table.add_row(
                row.site_number,
                row.name,
                " ,".join(row.aliases),
                str(row.active),
                str(row.account_id),
                str(row.balance_id),
            )

        self.loaded_file_type = "accounts"
        self.query_one("#confirm", Button).disabled = False
        self.query_one("#file-name", Input).disabled = False
        self.set_default_filename()

    def preview_balances(self):

        self.loaded_file = []
        for account in self.app_state.state.accounts:
            assert account.balance is not None
            self.loaded_file.append(account.balance)

        balance_table = self.query_one("#file-preview", DataTable)
        balance_table.clear(columns=True)
        balance_table.add_columns(
            "Site Number",
            "Annual Fee",
            "Remaining from this FY",
            "Outstanding from previous FYs",
            "Pay Frequency",
            "Account ID",
            "Balance ID",
        )

        for balance in self.loaded_file:
            balance_table.add_row(
                balance.site_number if balance is not None else "??",
                str(balance.annual) if balance is not None else "??",
                str(balance.remaining) if balance is not None else "??",
                str(balance.outstanding) if balance is not None else "??",
                balance.pay_frequency if balance is not None else "??",
                str(balance.account_id) if balance is not None else "??",
                str(balance.balance_id) if balance is not None else "??",
            )

        self.loaded_file_type = "balances"
        self.query_one("#confirm", Button).disabled = False
        self.query_one("#file-name", Input).disabled = False
        self.set_default_filename()

    def preview_sites(self):
        pass

    def preview_ignore(self):

        self.loaded_file = self.app_state.state.words_to_ignore

        ignore_table = self.query_one("#file-preview", DataTable)
        ignore_table.clear(columns=True)
        ignore_table.add_columns("Word")

        for word in self.loaded_file:
            ignore_table.add_row(word)

        self.loaded_file_type = "ignore"
        self.query_one("#confirm", Button).disabled = False
        self.query_one("#file-name", Input).disabled = False
        self.set_default_filename()

    def export_statement(self, filename: str):

        filename = self.query_one("#file-name", Input).value
        self.loaded_file = cast(list[Transaction], self.loaded_file)
        export_payments_to_csv(payments=self.loaded_file, filename=filename)

        self.query_one("#confirm", Button).disabled = True
        self.query_one("#file-name", Input).disabled = True
        self.query_one("#file-name", Input).value = ""
        self.query_one("#file-preview", DataTable).clear(columns=True)
        self.loaded_file = None
        self.loaded_file_type = None

    def export_accounts(self, filename: str):

        filename = self.query_one("#file-name", Input).value
        self.loaded_file = cast(list[Account], self.loaded_file)
        export_accounts_to_csv(accounts=self.loaded_file, filename=filename)

        self.query_one("#confirm", Button).disabled = True
        self.query_one("#file-name", Input).disabled = True
        self.query_one("#file-name", Input).value = ""
        self.query_one("#file-preview", DataTable).clear(columns=True)
        self.loaded_file = None
        self.loaded_file_type = None

    def export_balances(self, filename: str):

        filename = self.query_one("#file-name", Input).value
        self.loaded_file = cast(list[Balance], self.loaded_file)
        export_balances_to_csv(balances=self.loaded_file, filename=filename)

        self.query_one("#confirm", Button).disabled = True
        self.query_one("#file-name", Input).disabled = True
        self.query_one("#file-name", Input).value = ""
        self.query_one("#file-preview", DataTable).clear(columns=True)
        self.loaded_file = None
        self.loaded_file_type = None

    def export_sites(self, filename: str):
        filename = self.query_one("#file-name", Input).value

    def export_ignore(self, filename: str):

        filename = self.query_one("#file-name", Input).value
        self.loaded_file = cast(set[str], self.loaded_file)
        export_ignore_to_csv(words=self.loaded_file, filename=filename)

        self.query_one("#confirm", Button).disabled = True
        self.query_one("#file-name", Input).disabled = True
        self.query_one("#file-name", Input).value = ""
        self.query_one("#file-preview", DataTable).clear(columns=True)
        self.loaded_file = None
        self.loaded_file_type = None
