from decimal import Decimal

from rich.text import Text
from textual import on, work
from textual.binding import Binding
from textual.containers import (
    Horizontal,
    HorizontalGroup,
    VerticalGroup,
    VerticalScroll,
)
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    MaskedInput,
    Select,
    Static,
    Switch,
)

from application import Application
from models.account import Account
from models.transactions import Transaction
from ui.custom_widgets import ConfirmScreen, EnterAmountScreen


class ViewAccountMenu(Screen):

    CSS_PATH = "view_account_menu.tcss"

    BINDINGS = (
        Binding("q", "back_screen", "Back"),
        Binding("ctrl+w", "save_account", "Save"),
    )

    def __init__(self, app: Application, account: Account):
        super().__init__()
        self.app_state = app
        self.account = account
        self.history = []

    def compose(self):

        balance = self.account.balance
        assert balance is not None

        site_numbers = []
        for number in range(1, 101):
            if len(str(number)) == 1:
                number = f"0{number}"
            site_numbers.append(number)
            # Change to actual site numbers picked from list of available sites. Check for duplicates before application

        site_number_options = [(str(number), str(number)) for number in site_numbers]

        yield Header()
        yield Footer()

        with Horizontal():

            with VerticalGroup():
                yield Static(
                    f"STATEMENT FOR SITE {self.account.site_number}, {self.account.name}",
                    classes="section-title",
                )
                with VerticalScroll():
                    yield DataTable(id="history", cursor_type="row", zebra_stripes=True)

            with VerticalGroup():  # Have to link buttons with payment screen
                yield Static("ACCOUNT ACTIONS", classes="section-title")

                with VerticalGroup(id="actions"):
                    yield Button.success("Add Payment", id="payment")
                    yield Button.error("Add Charge", id="charge")
                    yield Button.warning("Make Inactive", id="status")
                    yield Button.error(
                        "Recalculate Balance From Payment History", id="recalculate"
                    )

            with VerticalScroll():
                yield Static("EDIT ACCOUNT", classes="section-title")
                with VerticalGroup():

                    yield Static("CONTACT DETAILS", classes="settings-title")

                    with HorizontalGroup(classes="input-row"):
                        yield Static("Name: ", classes="label")
                        yield Input(value=self.account.name, id="name")

                    with HorizontalGroup(classes="input-row"):
                        yield Static("Phone Number: ", classes="label")
                        yield MaskedInput(
                            template="9999 999 999;0", value="0484 250 494", id="phone"
                        )

                    with HorizontalGroup(classes="input-row"):
                        yield Static("Email Address: ", classes="label")
                        yield Input("placeholder", id="email")

                    with HorizontalGroup(classes="input-row"):
                        yield Static("Postal Address: ", classes="label")
                        yield Input("placeholder", id="address")

                    yield Static("SITE DETAILS", classes="settings-title")

                    with HorizontalGroup(classes="select-row"):
                        yield Static("Site Number: ", classes="select-label")
                        yield Select(
                            site_number_options,
                            value=self.account.site_number,
                            allow_blank=False,
                            id="number",
                        )

                    with HorizontalGroup(classes="input-row"):
                        yield Static("Extra Guests: ", classes="label")
                        yield MaskedInput("9;0", value="0", id="guests")

                    with HorizontalGroup(classes="switch-row"):
                        yield Static("Air Conditioner", classes="switch-label")
                        yield Switch(value=True, animate=True, id="ac")

                    with HorizontalGroup(classes="switch-row"):
                        yield Static("Sewer", classes="switch-label")
                        yield Switch(value=False, animate=True, id="sewer")

                    with HorizontalGroup(classes="switch-row"):
                        yield Static("Cabin", classes="switch-label")
                        yield Switch(value=False, animate=True, id="type")

                    yield Static("BALANCE DETAILS", classes="settings-title")

                    with HorizontalGroup(classes="input-row"):
                        yield Static("Annual Fees: ", classes="label")
                        yield MaskedInput(
                            "$9999;0", value=f"${balance.annual}", id="annual"
                        )

                    with HorizontalGroup(classes="select-row"):
                        yield Static("Pay Period: ", classes="select-label")
                        yield Select(
                            [("Monthly", "m"), ("Quarterly", "q"), ("Annually", "a")],
                            value=f"{balance.pay_frequency}",
                            allow_blank=False,
                            id="frequency",
                        )

    def on_mount(self) -> None:
        history_table = self.query_one("#history", DataTable)
        history_table.add_columns("Date", "Description", "Debit", "Credit", "Balance")
        self.populate_history_table()

    def action_back_screen(self):
        self.dismiss()

    def action_save_account(self) -> None:
        balance = self.account.balance
        assert balance is not None

        self.app_state.repos.account_repo.save_accounts([self.account])
        self.app_state.repos.account_repo.save_payments(self.history)
        self.app_state.state.clear_payments()
        self.app_state.state.clear_charges()

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

    def populate_history_table(self) -> None:

        assert self.account.balance is not None

        # Get any existing payments from the database
        if self.account.account_id is not None:
            history: list[Transaction] = self.app_state.repos.account_repo.get_payments(
                self.account.account_id
            )
        else:
            history: list[Transaction] = []

        # Get any payments not in database
        for payment in self.app_state.state.payments:
            if payment.account == self.account:
                history.append(payment)

        for charge in self.app_state.state.charges:
            if charge.account == self.account:
                history.append(charge)

        # Sort history by date so newest payment first
        history.sort(key=lambda t: t.date, reverse=True)

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
                    )
                )
                running_balance -= amount

        # Reverse the rows so oldest payment is first
        rows.reverse()

        # Populate the table
        history_table = self.query_one("#history", DataTable)
        for index, (date, description, debit, credit, balance) in enumerate(rows):
            history_table.add_row(
                Text(date, style="cyan"),
                description,
                Text(debit, style="red"),
                Text(credit, style="green"),
                balance,
                key=str(index),
            )
        history.reverse()
        self.history = history

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed):
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

    @work
    async def recalculate_balance(self):
        assert self.account.balance is not None

        confirm = await self.app.push_screen_wait(
            ConfirmScreen("This Action Is Irreverable. Are You Sure?")
        )

        if confirm is None or False:
            self.notify("Recalculation Cancelled", timeout=5)
            return

        self.account.balance.recalculate_from_history(self.history)
        self.notify("Balance Recalculated", timeout=5)
        self.query_one("#history", DataTable).clear()
        self.populate_history_table()

    @work
    async def add_payment(self) -> None:
        assert self.account.balance is not None
        amount = await self.app.push_screen_wait(EnterAmountScreen("Enter Amount"))
        if amount is None:
            return
        self.account.balance.add_payment(Decimal(amount))

    @work
    async def add_charge(self) -> None:
        assert self.account.balance is not None
        amount = await self.app.push_screen_wait(EnterAmountScreen("Enter Amount"))
        if amount is None:
            return
        self.account.balance.add_charge(Decimal(amount))
