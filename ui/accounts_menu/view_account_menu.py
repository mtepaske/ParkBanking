from copy import deepcopy
from decimal import Decimal

from rich.text import Text
from textual import on, work
from textual.app import ComposeResult
from textual.containers import (
    Horizontal,
    Vertical,
)
from textual.widgets import (
    Button,
    DataTable,
    Input,
    Label,
    MaskedInput,
    Select,
    Static,
    Switch,
)

from models.account import Account
from models.transactions import Transaction
from services.date import get_str_from_date, get_today
from ui.custom_widgets import (
    EditHistoryScreen,
    EnterAmountScreen,
    Menu,
    ReviewBalanceScreen,
)


class ViewAccountMenu(Menu):
    """
    A menu to view and edit a specific accounts information

    Attributes:
        CSS_PATH: (str) The name of the file containing styling information for the app
        account: (Account) The account to view
    """

    CSS_PATH = "view_account_menu.tcss"

    def __init__(self, account: Account, **kwargs) -> None:
        """
        Initialise the instance

        Args:
            account: The account to view
            **kwargs: Other key word arguments for base class
        """

        super().__init__(**kwargs)
        self.account = account
        self.history_keys = {}

    def compose(self) -> ComposeResult:
        """Construct the widgets on the screen"""

        balance = self.account.balance
        assert balance is not None

        # Generate possible site numbers
        site_numbers = []
        for number in range(1, 101):
            if len(str(number)) == 1:
                number = f"0{number}"
            site_numbers.append(number)
            # Change to actual site numbers picked from list of available sites. Check for duplicates before application

        site_number_options = [(str(number), str(number)) for number in site_numbers]

        yield from super().compose()

        # The account history section
        with Vertical(classes="section"):
            yield Static(
                f"STATEMENT FOR SITE {Text(f"{self.account.site_number}, {self.account.name}", style='green')}",
                classes="section-title",
            )
            yield DataTable(id="history", cursor_type="row", zebra_stripes=True)

        # The account actions section
        with Vertical(classes="section"):  # Have to link buttons with payment screen
            yield Static("ACCOUNT ACTIONS", classes="section-title")

            with Horizontal(classes="row"):
                yield Button.success("Add Payment", id="payment")

            with Horizontal(classes="row"):
                yield Button.error("Add Charge", id="charge")

            with Horizontal(classes="row"):
                yield Button.warning("Make Inactive", id="status")

            with Horizontal(classes="row"):
                yield Button.error(
                    "Recalculate Balance From Payment History", id="recalculate"
                )

        # The edit account section
        with Vertical(classes="section"):
            yield Static("EDIT ACCOUNT", classes="section-title")

            with Horizontal(classes="row"):
                yield Static("CONTACT DETAILS", classes="sub-title")

            with Horizontal(classes="row"):
                yield Label("Name: ")
                yield Input(value=self.account.name, id="name")

            with Horizontal(classes="row"):
                yield Label("Phone Number: ")
                yield MaskedInput(
                    template="9999 999 999;0", value="0484 250 494", id="phone"
                )

            with Horizontal(classes="row"):
                yield Label("Email Address: ")
                yield Input("placeholder", id="email")

            with Horizontal(classes="row"):
                yield Label("Postal Address: ")
                yield Input("placeholder", id="address")

            with Horizontal(classes="row"):
                yield Static("SITE DETAILS", classes="sub-title")

            with Horizontal(classes="row"):
                yield Label("Site Number: ", classes="label")
                yield Select(
                    site_number_options,
                    value=self.account.site_number,
                    allow_blank=False,
                    id="number",
                )

            with Horizontal(classes="row"):
                yield Label("Extra Guests: ")
                yield MaskedInput("9;0", value="0", id="guests")

            with Horizontal(classes="row"):
                yield Label("Air Conditioner: ")
                with Horizontal(classes="switch"):
                    yield Switch(value=True, animate=True, id="ac")

            with Horizontal(classes="row"):
                yield Label("Sewer: ")
                with Horizontal(classes="switch"):
                    yield Switch(value=False, animate=True, id="sewer")

            with Horizontal(classes="row"):
                yield Label("Cabin: ")
                with Horizontal(classes="switch"):
                    yield Switch(value=False, animate=True, id="type")

            with Horizontal(classes="row"):
                yield Static("BALANCE DETAILS", classes="sub-title")

            with Horizontal(classes="row"):
                yield Label("Annual Fees: ")
                yield MaskedInput("$9999;0", value=f"${balance.annual}", id="annual")

            with Horizontal(classes="row"):
                yield Label("Pay Period: ", classes="label")
                yield Select(
                    [("Monthly", "m"), ("Quarterly", "q"), ("Annually", "a")],
                    value=f"{balance.pay_frequency}",
                    allow_blank=False,
                    id="frequency",
                )

    def action_save(self) -> None:
        """Save updates to the database"""

        balance = self.account.balance
        assert balance is not None

        # Contact Details
        self.account.name = str(self.query_one("#name", Input).value)
        # self.account.phone_number = self.query_one('#phone', MaskedInput).value
        # self.account.email = self.query_one('#email', Input).value
        # self.account.address = self.query_one('#address', Input).value

        # Site Details
        self.account.site_number = str(self.query_one("#number", Select).value)
        # self.account.extra_guests = self.query_one("#guests", Input).value
        # self.account.site.ac = self.query_one("#ac", Switch).value
        # self.account.site.sewer = self.query_one("#sewer", Switch).value
        # self.account.site.cabin = self.query_one("#cabin", Switch).value

        # Balance Details
        balance.annual = Decimal(
            self.query_one("#annual", MaskedInput).value.removeprefix("$")
        )
        balance.pay_frequency = str(self.query_one("#frequency", Select).value)

        # Save updates to database
        history = self.get_account_history()
        self.app_state.repos.account_repo.save_accounts([self.account])
        self.app_state.repos.account_repo.save_history(history)

        # Clear payments and charges from the application state
        for transaction in history:

            try:
                self.app_state.state.remove_payment(transaction)
            except ValueError:
                pass

            try:
                self.app_state.state.remove_charge(transaction)
            except ValueError:
                pass

    def on_mount(self) -> None:
        """Initialise the account history table"""

        history_table = self.query_one("#history", DataTable)
        history_table.add_columns("Date", "Description", "Debit", "Credit", "Balance")
        self.populate_history_table()

    def get_account_history(self) -> list[Transaction]:
        """
        Gets the account history from the database and current app state

        Returns:
            A list of transactions representing the account history
        """

        assert self.account.balance is not None

        # Get the existsing history from the database
        if self.account.account_id is not None:
            history: list[Transaction] = self.app_state.repos.account_repo.get_history(
                self.account
            )
        else:
            history: list[Transaction] = []

        # Get any applied payments not in database
        for payment in self.app_state.state.payments:
            if payment.account == self.account:
                history.append(payment)

        # Get any applied charges not in the database
        for charge in self.app_state.state.charges:
            if charge.account == self.account:
                history.append(charge)

        # Sort history by date so newest payment first
        history.sort(key=lambda t: t.date, reverse=True)

        return history

    def populate_history_table(self) -> None:
        """Populate the account history table"""

        assert self.account.balance is not None

        history = self.get_account_history()

        # Add each payment to a list of rows calculating running balance
        running_balance = self.account.balance.balance
        rows = []

        for payment in history:

            if payment.amount > 0:
                rows.append(
                    (
                        payment.date,
                        payment.type,
                        "",
                        f"${payment.amount:,.2f}",
                        f"${running_balance:,.2f}",
                        payment,
                    )
                )
                running_balance += payment.amount

            else:
                amount = abs(payment.amount)
                rows.append(
                    (
                        payment.date,
                        payment.type,
                        f"${payment.amount:,.2f}",
                        "",
                        f"${running_balance:,.2f}",
                        payment,
                    )
                )
                running_balance -= amount

        # Reverse the rows so oldest payment is first
        rows.reverse()

        # Populate the table
        history_table = self.query_one("#history", DataTable)
        history_table.clear()
        for date, description, debit, credit, balance, payment in rows:
            key = history_table.add_row(
                Text(date, style="cyan"),
                description,
                Text(debit, style="red"),
                Text(credit, style="green"),
                balance,
            )

            self.history_keys[key] = payment

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed):
        """
        Runs when a button is pressed

        Args:
            event: The button presss
        """

        assert self.account.balance is not None

        match event.button.id:

            case "payment":
                self.add_payment()

            case "charge":
                self.add_charge()

            case "status":
                self.account.switch_active()
                self.notify(
                    f"Account Switched To Active: {self.account.active}", timeout=5
                )

            case "recalculate":
                self.recalculate_balance()

    @on(DataTable.RowSelected)
    def on_datatable_row_selected(self, event: DataTable.RowSelected):
        transaction = self.history_keys[event.row_key]
        self.edit_history(transaction)

    @work
    async def recalculate_balance(self):
        """Recalculates the account balance from the current account history"""

        balance = self.account.balance
        assert balance is not None

        # Get the current history with oldest payment first
        history = self.get_account_history()
        history.reverse()

        # Recaculate the new balance
        new_balance = balance.recalculate_from_history(history)

        old_balance = deepcopy(balance)
        balance.apply_new_amounts((Decimal(0), Decimal(0), Decimal(0)))

        # Confirm the new account balance
        confirm = await self.app.push_screen_wait(
            ReviewBalanceScreen(
                "Confirm New Balance", accounts=[self.account], payments=history
            )
        )

        # Apply new account balance
        if confirm:
            balance.apply_new_amounts(new_balance)
            self.notify("Balance Recalculated", timeout=5)
            self.query_one("#history", DataTable).clear()
            self.populate_history_table()

        # Cancel recalculation
        else:
            balance = old_balance
            self.notify("Recalculation Cancelled", severity="warning", timeout=5)

    @work
    async def add_payment(self) -> None:
        """Add a payment to the account"""

        assert self.account.balance is not None

        # Get the amount to add
        amount = await self.app.push_screen_wait(EnterAmountScreen("Enter Amount"))

        # Cancel adding the payment
        if amount is None:
            self.notify("Cancelled Adding Payment", severity="warning", timeout=5)
            return

        payment = Transaction(
            date=get_str_from_date(get_today()),
            amount=Decimal(amount),
            type_str="Custom Payment",
        )
        payment.add_account(self.account)
        assert payment.account is not None

        # Apply the paymet
        new_balance = self.account.balance.add_payment(payment.amount)
        self.account.balance.apply_new_amounts(new_balance)
        self.app_state.state.add_payment(payment)

        self.notify("New Payment Added", timeout=5)
        self.populate_history_table()

    @work
    async def add_charge(self) -> None:
        """Add a charge to the account"""

        assert self.account.balance is not None

        # Get the amount to add
        amount = await self.app.push_screen_wait(EnterAmountScreen("Enter Amount"))

        # Cancel adding the charge
        if amount is None:
            self.notify("Cancelled Adding Charge", severity="warning", timeout=5)
            return

        charge = Transaction(
            date=get_str_from_date(get_today()),
            amount=0 - Decimal(amount),
            type_str="Custom Charge",
        )
        charge.add_account(self.account)
        assert charge.account is not None

        # Apply the charge
        new_balance = self.account.balance.add_charge(charge.amount)
        self.account.balance.apply_new_amounts(new_balance)
        self.app_state.state.add_charge(charge)

        self.notify("New Charge Added", timeout=5)
        self.populate_history_table()

    @work
    async def edit_history(self, history_item: Transaction):
        await self.app.push_screen_wait(EditHistoryScreen(history_item))
        self.populate_history_table()
