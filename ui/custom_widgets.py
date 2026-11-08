from collections.abc import Generator, Iterable
from copy import deepcopy
from pathlib import Path

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import (
    HorizontalGroup,
    Vertical,
    VerticalGroup,
    VerticalScroll,
)
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import (
    Button,
    DataTable,
    DirectoryTree,
    Input,
    Label,
    Select,
    Static,
)

from application import Application
from models.account import Account
from models.transactions import Transaction


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

    def __init__(self, app: Application, **kwargs) -> None:

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
            yield Static("Unapplied Payments/Charges: ", classes="status")
            yield Static(
                str(len(state.unapplied)), classes="number", id="status-unapplied"
            )

        with HorizontalGroup(classes="status-row"):
            yield Static("Unsaved Payments: ", classes="status")
            yield Static(
                str(len(state.payments)), classes="number", id="status-payments"
            )

        with HorizontalGroup(classes="status-row"):
            yield Static("Unsaved Charges: ", classes="status")
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

    def on_mount(self) -> None:

        self.app_state.state.subscribe(self.refresh_status)
        self.refresh_status()

    def on_unmount(self) -> None:

        self.app_state.state.unsubscribe(self.refresh_status)

    def refresh_status(self) -> None:

        state = self.app_state.state

        self.query_one("#status-transactions", Static).update(
            str(len(state.transactions))
        )
        self.query_one("#status-unapplied", Static).update(str(len(state.unapplied)))
        self.query_one("#status-payments", Static).update(str(len(state.payments)))
        self.query_one("#status-charges", Static).update(str(len(state.charges)))
        self.query_one("#status-sites", Static).update(str(len(state.sites)))
        self.query_one("#status-accounts", Static).update(str(len(state.accounts)))
        self.query_one("#status-ignore", Static).update(str(len(state.words_to_ignore)))


class ConfirmScreen(ModalScreen[bool]):

    def __init__(self, message: str) -> None:

        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:

        with VerticalScroll(classes="dialog"):

            with HorizontalGroup():
                yield Label(self.message)

            yield from self.compose_content()

            yield Button.success("Confirm", id="confirm")
            yield Button.error("Cancel", id="cancel")

    def compose_content(self) -> Generator[Widget, None, None]:

        yield from ()

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:

        if event.button.id == "confirm":
            self.dismiss(True)

        else:
            self.dismiss(False)


class AppendScreen(ModalScreen[str]):

    def __init__(self, message: str) -> None:

        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:

        with Vertical(classes="dialog"):

            with HorizontalGroup():
                yield Label(self.message)

            yield Button.success("Add To", id="append")
            yield Button.warning("Replace", id="replace")
            yield Button.error("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:

        self.dismiss(event.button.id)


class ImportBalancesScreen(ModalScreen[Path | None]):

    def __init__(self, import_folder: Path) -> None:

        super().__init__()
        self.import_folder = import_folder
        self.filepath = None

    def compose(self) -> ComposeResult:

        with Vertical(classes="dialog"):

            with HorizontalGroup():
                yield Label(
                    "Please Selected File Containing Balance Information For Imported Accounts"
                )

            with HorizontalGroup():
                yield DirectoryTree(
                    str(self.import_folder), classes="tree", id="balance-tree"
                )

            yield Button.success("Confirm", disabled=True, id="confirm")
            yield Button.error("Cancel", id="cancel")

    @on(DirectoryTree.FileSelected)
    def on_directiory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:

        self.filepath = event.path
        self.query_one("#confirm", Button).disabled = False

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:

        if event.button.id == "confirm":
            self.dismiss(self.filepath)
        else:
            self.dismiss()


class ConfirmChargesScreen(ConfirmScreen):

    def __init__(self, message: str, charges: list[Transaction]) -> None:

        super().__init__(message)
        self.charges = charges

    def compose_content(self) -> Generator[Widget, None, None]:

        charge_preview = DataTable(zebra_stripes=True, cursor_type="row")
        charge_preview.add_columns("Account", "Date", "Description", "Amount")

        for charge in self.charges:
            charge_preview.add_row(
                charge.account, charge.date, charge.details, charge.amount
            )

        yield charge_preview


class AccountPicker(ModalScreen[Account | str | None]):

    def __init__(self, message: str, accounts: list[Account]) -> None:

        super().__init__()
        self.accounts = accounts
        self.message = message

    def compose(self) -> ComposeResult:
        with VerticalScroll(classes="dialog"):

            with HorizontalGroup():
                yield Label(self.message)

            yield Button.warning("No Account", id="none")
            yield Button.error("Cancel", id="cancel")

            yield DataTable(zebra_stripes=True, cursor_type="row", id="accounts")

    def on_mount(self) -> None:

        account_table = self.query_one("#accounts", DataTable)
        account_table.add_columns("Account ID", "Name", "Site Number", "Active")

        for account in self.accounts:
            account_table.add_row(
                Text(f"{account.account_id}", style="cyan"),
                account.name,
                account.site_number,
                account.active,
                key=str(account.account_id) if account.account_id is not None else None,
            )

    @on(DataTable.RowSelected)
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:

        account_id = event.row_key.value

        if account_id is None:
            selected: list = event.data_table.get_row(event.row_key)
            for account in self.accounts:
                if selected[1] == account.name:
                    self.dismiss(account)

        else:
            for account in self.accounts:
                if account_id == str(account.account_id):
                    self.dismiss(account)

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:

        if event.button.id == "none":
            self.dismiss("None")
        else:
            self.dismiss()


class EnterAmountScreen(ModalScreen[str | None]):

    def __init__(self, message: str) -> None:

        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:

        with Vertical(classes="dialog"):

            with HorizontalGroup():
                yield Label(self.message, id="amount")

            yield Input(placeholder="$0")

            yield Button.success("Confirm", id="confirm")
            yield Button.error("Cancel", id="cancel")

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:

        if event.button.id == "confirm":
            self.dismiss(self.query_one("#amount", Input).value)
        else:
            self.dismiss()


class ReviewBalanceScreen(ModalScreen[list[Account] | None]):

    def __init__(
        self, message: str, accounts: list[Account], payments: list[Transaction]
    ) -> None:

        super().__init__()
        self.message = message
        self.payments = payments
        self.accounts = deepcopy(accounts)

    def compose(self) -> ComposeResult:

        with VerticalScroll(classes="dialog"):

            yield DataTable(zebra_stripes=True, cursor_type="row", id="history")

            with HorizontalGroup():
                yield Label(self.message)

            yield Button.success("Confirm", id="confirm")
            yield Button.error("Cancel", id="cancel")

    def on_mount(self) -> None:

        review_table = self.query_one("#history", DataTable)
        review_table.add_columns(
            "Account",
            "Old Remaining",
            "Old Outstanding",
            "Old Credit",
            " -> ",
            "Amount",
            " -> ",
            "New Remaining",
            "New Outstanding",
            "New Credit",
            "New Total Balance",
        )

        for payment in self.payments:
            account = payment.account
            assert account is not None
            balance = account.balance
            assert balance is not None

            old_balance = (balance.remaining, balance.outstanding, balance.credit)

            if payment.amount > 0:
                new_balance = balance.add_payment(payment.amount)
                sign = "-"
            else:
                new_balance = balance.add_charge(payment.amount)
                sign = "+"

            review_table.add_row(
                Text(f"{account.site_number}: {account.name}", style="cyan"),
                Text(f"${old_balance[0]:,.2f}", style="red"),
                (
                    Text(f"${old_balance[1]:,.2f}", style="red")
                    if old_balance[1] != 0
                    else ""
                ),
                (
                    Text(f"${old_balance[2]:,.2f}", style="red")
                    if old_balance[2] != 0
                    else ""
                ),
                Text(" -> ", style="cyan"),
                Text(f"{sign}${payment.amount:,.2f}", style="cyan"),
                Text(" -> ", style="cyan"),
                Text(f"${new_balance[0]:,.2f}", style="green"),
                (
                    Text(f"${new_balance[1]:,.2f}", style="green")
                    if old_balance[1] != 0
                    else ""
                ),
                (
                    Text(f"${new_balance[2]:,.2f}", style="green")
                    if old_balance[2] != 0
                    else ""
                ),
                Text(
                    f"${new_balance[0] + new_balance[1] - new_balance[2]:,.2f}",
                    style="cyan",
                ),
            )

            balance.apply_new_amounts(new_balance)

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:

        if event.button.id == "confirm":
            self.dismiss(self.accounts)

        else:
            self.dismiss()


class ProccessUnknownScreen(ModalScreen[str | Account | None]):

    def __init__(self, unknown: str, accounts_state: list[Account]):

        super().__init__()
        self.unknown = unknown
        self.accounts = [
            (f"{account.site_number}: {account.name}", account)
            for account in accounts_state
        ]

    def compose(self) -> ComposeResult:

        with Vertical(classes="dialog"):
            with HorizontalGroup():
                yield Label("Proccessing Unknown Words")

            with HorizontalGroup():
                yield Label(f"{self.unknown}")

            with HorizontalGroup():
                yield Button.success("Ignore This Word", id="ignore")

            with HorizontalGroup():

                yield Select(
                    self.accounts,
                    prompt="Select Account",
                    type_to_search=True,
                    id="account",
                )

                yield Button.success(
                    f"Add {self.unknown} As An Alias For This Account",
                    disabled=True,
                    id="confirm",
                )

            yield Button.warning("Skip", id="skip")
            yield Button.error("Skip All", id="skip-all")
            yield Button.error("Cancel", id="cancel")

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:

        match event.button.id:

            case "confirm":
                account = self.query_one("#account", Select).value

                if isinstance(account, Account):
                    self.dismiss(account)

            case "cancel":
                self.dismiss("cancel")

            case "skip":
                self.dismiss()

            case "skip-all":
                self.dismiss("skip-all")

            case "ignore":
                self.dismiss("ignore")

    @on(Select.Changed)
    def on_select_changed(self) -> None:

        self.query_one("#confirm", Button).disabled = False


class ReviewUnknownScreen(ConfirmScreen):

    def __init__(
        self, message: str, ignore_to_add: set, alias_to_add: dict[str, Account]
    ) -> None:

        super().__init__(message)
        self.ignore_to_add = ignore_to_add
        self.alias_to_add = alias_to_add

    def compose_content(self) -> Generator[DataTable, None, None]:

        unknown_table = DataTable(zebra_stripes=True, id="unknown")
        unknown_table.add_columns("Word", "Outcome")

        for ignore in self.ignore_to_add:
            unknown_table.add_row(ignore, "Add To Words To Ignore")

        for alias, account in self.alias_to_add.items():
            unknown_table.add_row(
                alias, f"Add As Alias For {account.site_number}: {account.name}"
            )

        yield unknown_table
