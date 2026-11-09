from collections.abc import Generator, Iterable
from copy import deepcopy
from pathlib import Path

from rich.text import Text
from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import (
    HorizontalGroup,
    Vertical,
    VerticalGroup,
    VerticalScroll,
)
from textual.screen import ModalScreen, Screen
from textual.widget import Widget
from textual.widgets import (
    Button,
    DataTable,
    DirectoryTree,
    Footer,
    Header,
    Input,
    Label,
    MaskedInput,
    Select,
    Static,
)

from application import Application
from models.account import Account
from models.transactions import Transaction
from services.date import end_of_fy, get_str_from_date, start_of_fy
from services.settings import get_setting


class Menu(Screen):
    """
    A menu screen

    Attributes:
        BINDINGS: (tuple[Binding]) The key bindings for the menu
        app_state: (Application) The application state
    """

    BINDINGS = (
        Binding("Q", "quit", "Quit Application"),
        Binding("q", "back", "Back"),
        Binding("ctrl+w", "save", "Save"),
        Binding("ctrl+l", "load", "Load"),
    )

    def __init__(self, app_state: Application, **kwargs):
        """
        Initialise the class

        Args:
            app_state: The application state
            **kwargs: Other keyword arguments for the base class
        """

        super().__init__(**kwargs)
        self.app_state = app_state

    def compose(self) -> ComposeResult:
        """Construct the widgets on the screen"""

        yield Header()
        yield Footer()

    @work
    async def action_quit(self) -> None:
        """Quit the program"""

        # Saves depending on settings
        if get_setting("auto_save_to_db") == "True":
            self.action_save()
            self.app.exit()
        else:
            confirm = await self.app.push_screen_wait(
                ConfirmScreen("Unsaved Progress Will Be Lost. Do You Want To Continue?")
            )
            if confirm:
                self.app.exit()
            else:
                return

    def action_back(self) -> None:
        """Go back a screen"""

        self.dismiss()

    def action_save(self) -> None:
        """Save the current state to the database"""

        self.app_state.repos.account_repo.save_accounts(self.app_state.state.accounts)
        self.app_state.repos.account_repo.save_history(self.app_state.state.payments)
        self.app_state.repos.account_repo.save_history(self.app_state.state.charges)
        self.app_state.repos.ignore_repo.save_all_ignore(
            self.app_state.state.words_to_ignore
        )

        self.app_state.state.clear_payments()
        self.app_state.state.clear_charges()

        self.notify("Saved To Database", timeout=5)

    def action_load(self) -> None:
        """Load from the database"""

        self.app_state.load_from_db()

        self.notify("Loaded From Database", timeout=5)


class StatusBox(VerticalGroup):
    """
    Display the application state

    Attributes:
        border_title: (str) The title of the widget
        app_state: (Application) The application state
    """

    def __init__(self, app_state: Application, **kwargs) -> None:
        """
        Initialise the widget

        Args:
            app_state: The application state
            **kwargs: Other key word arguments
        """

        super().__init__(**kwargs, classes="status-box")
        self.border_title = "Loaded Data"
        self.app_state = app_state

    def compose(self) -> ComposeResult:
        """Construct the widgets on the screen"""

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
        """On starting of the widget"""

        self.app_state.state.subscribe(self.refresh_status)
        self.refresh_status()

    def on_unmount(self) -> None:
        """On closing on the widget"""

        self.app_state.state.unsubscribe(self.refresh_status)

    def refresh_status(self) -> None:
        """Refresh display"""

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


class ConfirmScreen(ModalScreen[bool]):
    """
    A popup screen to for confirmation

    Attributes:
        message: (str) The message to display
    """

    def __init__(self, message: str) -> None:
        """
        Initialise the screen

        Args:
            message: The message to display
        """
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        """Construct the widgets on the screen"""

        with VerticalScroll(classes="dialog"):

            with HorizontalGroup():
                yield Label(self.message)

            yield from self.compose_content()

            yield Button.success("Confirm", id="confirm")
            yield Button.error("Cancel", id="cancel")

    def compose_content(self) -> Generator[Widget, None, None]:
        """Construct widgets of subclasses"""

        yield from ()

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Runs when a button is pressed

        Args:
            event: The button presss
        """

        if event.button.id == "confirm":
            self.dismiss(True)

        else:
            self.dismiss(False)


class AppendScreen(ModalScreen[str]):
    """
    A popup screen for getting user choice on adding to or replacing state

    Attributes:
        message: (str) The message to display
    """

    def __init__(self, message: str) -> None:
        """
        Initialise the screen

        Args:
            message: The message to display
        """

        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        """Construct the widgets on the screen"""

        with Vertical(classes="dialog"):

            with HorizontalGroup():
                yield Label(self.message)

            yield Button.success("Add To", id="append")
            yield Button.warning("Replace", id="replace")
            yield Button.error("Cancel", id="cancel")

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Runs when a button is pressed

        Args:
            event: The button presss
        """

        self.dismiss(event.button.id)


class ImportBalancesScreen(ModalScreen[Path | None]):
    """
    A popup screen to import matching balances for account import

    Attributes:
        import_folder: (Path) The path of the folder to import from
        filepath: (Path) The file to import
    """

    def __init__(self, import_folder: Path) -> None:
        """
        Initialise the screen

        Args:
            import_folder: The folder to import from
            filepath: The path of the file to import. None until selected from directory tree
        """

        super().__init__()
        self.import_folder = import_folder
        self.filepath = None

    def compose(self) -> ComposeResult:
        """Construct the widgets on the screen"""

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
        """
        Runs when a file is selected

        Args:
            event: The event of the file selection
        """

        self.filepath = event.path
        self.query_one("#confirm", Button).disabled = False

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Runs when a button is pressed

        Args:
            event: The button presss
        """

        if event.button.id == "confirm":
            self.dismiss(self.filepath)
        else:
            self.dismiss()


class SelectDateRange(ModalScreen[tuple[str, str] | None]):

    def __init__(self, message: str):

        super().__init__()
        self.message = message
        self.start_date = get_str_from_date(start_of_fy())
        self.end_date = get_str_from_date(end_of_fy())

    def compose(self) -> ComposeResult:

        with VerticalGroup(classes="dialog"):

            yield Label(self.message)

            with HorizontalGroup():

                with VerticalGroup():

                    yield Static("Start Date")
                    yield MaskedInput(
                        "9999-99-99", value=str(self.start_date), id="start-date"
                    )

                with VerticalGroup():

                    yield Static("End Date")
                    yield MaskedInput(
                        "9999-99-99", value=str(self.end_date), id="end-date"
                    )

            yield Button.success("Confirm", id="confirm")
            yield Button.error("Cancel", id="cancel")

    @on(MaskedInput.Submitted)
    def on_maskedinput_submitted(self, event: MaskedInput.Submitted):

        match event.control.id:

            case "start-date":

                self.start_date = self.query_one("#start-date", MaskedInput).value

            case "end-date":

                self.end_date = self.query_one("#end-date", MaskedInput).value

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed):

        if event.button.id == "confirm":

            self.dismiss((self.start_date, self.end_date))

        else:

            self.dismiss()


class ConfirmChargesScreen(ConfirmScreen):
    """
    A popup screen to confirm generated charges

    Attributes:
        charges: (list[Transaction]) A list of charges to confirm
    """

    def __init__(self, message: str, charges: list[Transaction]) -> None:
        """
        Initialise the screen

        Args:
            message: The message to display
            charges: A list of charges to confirm
        """

        super().__init__(message)
        self.charges = charges

    def compose_content(self) -> Generator[Widget, None, None]:
        """Construct the widgets on the screen"""

        charge_preview = DataTable(zebra_stripes=True, cursor_type="row")
        charge_preview.add_columns("Account", "Date", "Description", "Amount")

        for charge in self.charges:
            charge_preview.add_row(
                Text(f"{charge.account}", style="cyan"),
                charge.date,
                charge.details,
                charge.amount,
            )

        yield charge_preview


class AccountPicker(ModalScreen[Account | str | None]):
    """
    A popup screen for selecting an account

    Attributes:
        accounts: (list[Account]) The accounts to select from
        message: (str) The message to display
    """

    def __init__(self, message: str, accounts: list[Account]) -> None:
        """
        Initialise the screen

        Args:
            message: The message to display
            accounts: The accounts to choose from
        """

        super().__init__()
        self.accounts = accounts
        self.message = message

    def compose(self) -> ComposeResult:
        """Construct the widgets on the screen"""

        with VerticalScroll(classes="dialog"):

            with HorizontalGroup():
                yield Label(self.message)

            yield Button.warning("No Account", id="none")
            yield Button.error("Cancel", id="cancel")

            yield DataTable(zebra_stripes=True, cursor_type="row", id="accounts")

    def on_mount(self) -> None:
        """On starting of the widget"""

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
        """
        Runs when a row is selected

        Args:
            event: The row selection
        """

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
        """
        Runs when a button is pressed

        Args:
            event: The button presss
        """

        if event.button.id == "none":
            self.dismiss("None")
        else:
            self.dismiss()


class EnterAmountScreen(ModalScreen[str | None]):
    """
    A popup screen to enter an amount

    Attributes:
        message: (str) The message to display
    """

    def __init__(self, message: str) -> None:
        """
        Initialise the screen

        Args:
            message: The message to display
        """

        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        """Construct the widgets on the screen"""

        with Vertical(classes="dialog"):

            with HorizontalGroup():
                yield Label(self.message)

            yield Input(placeholder="$0", id="amount")

            yield Button.success("Confirm", id="confirm")
            yield Button.error("Cancel", id="cancel")

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Runs when a button is pressed

        Args:
            event: The button presss
        """

        if event.button.id == "confirm":
            self.dismiss(self.query_one("#amount", Input).value)
        else:
            self.dismiss()


class ReviewBalanceScreen(ModalScreen[list[Account] | None]):
    """
    A popup screen to review payments

    Attributes:
        message: (str) The message to display
        payments: (list[Transaction]) The payments to review
        accounts: (list[Account]) The accounts to review
    """

    def __init__(
        self, message: str, accounts: list[Account], payments: list[Transaction]
    ) -> None:
        """
        Initialise the screen

        Args:
            message: The message to display
            payments: The payments to review
            accounts: The accounts to review
        """

        super().__init__()
        self.message = message
        self.payments = payments
        self.accounts = deepcopy(accounts)

    def compose(self) -> ComposeResult:
        """Construct the widgets on the screen"""

        with VerticalScroll(classes="dialog"):

            yield DataTable(zebra_stripes=True, cursor_type="row", id="history")

            with HorizontalGroup():
                yield Label(self.message)

            yield Button.success("Confirm", id="confirm")
            yield Button.error("Cancel", id="cancel")

    def on_mount(self) -> None:
        """On starting of the widget"""

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
                Text(f"{sign}${abs(payment.amount):,.2f}", style="cyan"),
                Text(" -> ", style="cyan"),
                Text(f"${new_balance[0]:,.2f}", style="green"),
                (
                    Text(f"${new_balance[1]:,.2f}", style="green")
                    if new_balance[1] != 0
                    else ""
                ),
                (
                    Text(f"${new_balance[2]:,.2f}", style="green")
                    if new_balance[2] != 0
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
        """
        Runs when a button is pressed

        Args:
            event: The button presss
        """

        if event.button.id == "confirm":
            self.dismiss(self.accounts)

        else:
            self.dismiss()


class ProccessUnknownScreen(ModalScreen[str | Account | None]):
    """
    A popup screen to get user choice for handlig an unknown word

    Attributes:
        unknown: (str) The word to handle
        accounts: (list[Account]) A list of accounts that the word could be added as an alias for
    """

    def __init__(self, unknown: str, accounts_state: list[Account]):
        """
        Initialise the screen

        Args:
            unknown: The unknown word
            accounts: The accounts that the word could be added as an alias for
        """

        super().__init__()
        self.unknown = unknown
        self.accounts = [
            (f"{account.site_number}: {account.name}", account)
            for account in accounts_state
        ]

    def compose(self) -> ComposeResult:
        """Construct the widgets on the screen"""

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
        """
        Runs when a button is pressed

        Args:
            event: The button presss
        """

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
        """Runs when a select widget is changed"""

        self.query_one("#confirm", Button).disabled = False


class ReviewUnknownScreen(ConfirmScreen):
    """
    A popup sreen to review unknown words

    Attributes:
        ignore_to_add: (set[str]) The words to add to the ignored words
        alias_to_add: (dict[str, Account]) The words to add as aliases and the respective account
    """

    def __init__(
        self, message: str, ignore_to_add: set, alias_to_add: dict[str, Account]
    ) -> None:
        """
        Initialise the screen

        Args:
            ignore_to_add: The words to add to ignored words
            alias_to_add: The words to add as aliases and the respective account
        """

        super().__init__(message)
        self.ignore_to_add = ignore_to_add
        self.alias_to_add = alias_to_add

    def compose_content(self) -> Generator[DataTable, None, None]:
        """Construct the widgets on the screen"""

        unknown_table = DataTable(zebra_stripes=True, id="unknown")
        unknown_table.add_columns("Word", "Outcome")

        for ignore in self.ignore_to_add:
            unknown_table.add_row(ignore, "Add To Words To Ignore")

        for alias, account in self.alias_to_add.items():
            unknown_table.add_row(
                alias, f"Add As Alias For {account.site_number}: {account.name}"
            )

        yield unknown_table
