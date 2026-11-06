from rich.text import Text
from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Static

from application import Application
from services.match import Matcher, match_transactions
from ui.custom_widgets import AccountPicker, StatusBox


class PaymentMenu(Screen):

    CSS_PATH = "payment_menu.tcss"

    BINDINGS = (Binding("q", "back_screen", "Back"),)

    def __init__(self, app_state: Application, **kwargs):
        super().__init__(id="payment-screen", **kwargs)
        self.app_state = app_state

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        with VerticalScroll(classes="section"):
            yield Static("Unmacthed Tranactions", classes="section-title")
            yield DataTable(cursor_type="row", id="unmatched")

        with VerticalScroll(classes="section"):
            yield Static("Matched Tranactions", classes="section-title")
            yield DataTable(cursor_type="row", id="matched")

        with Vertical(classes="section"):
            yield Static("Actions", classes="section-title")
            with Horizontal(classes="button-row"):
                yield Button.success(
                    "Match Tranactions To Accounts", id="match", disabled=True
                )
            with Horizontal(classes="button-row"):
                yield Button.warning("Proccess Payments", id="payments", disabled=True)
            with Horizontal(classes="button-row"):
                yield Button.warning(
                    "Proccess Unknown Words", id="unknown", disabled=True
                )
            yield StatusBox(app=self.app_state, id="app-status")

    def on_mount(self) -> None:
        self.query_one("#matched", DataTable).add_columns(
            "Date",
            "Site Number",
            "Account",
            "Amount",
            "Type",
            "Details",
        )
        self.query_one("#unmatched", DataTable).add_columns("Date", "Amount", "Details")
        self.populate_matched()
        self.populate_unmatched()

        if (
            len(self.app_state.state.transactions) > 0
            and len(self.app_state.state.accounts) > 0
        ):
            self.query_one("#match", Button).disabled = False

        if (
            len(self.app_state.state.payments) > 0
            and len(self.app_state.state.accounts) > 0
        ):
            self.query_one("#payments", Button).disabled = False

        if (
            len(self.app_state.state.unknown_words) > 0
            and len(self.app_state.state.accounts) > 0
        ):
            self.query_one("#unknown", Button).disabled = False

    def populate_matched(self) -> None:
        payments = self.app_state.state.payments
        payment_table = self.query_one("#matched", DataTable)
        payment_table.clear()
        for payment in payments:
            assert payment.account is not None
            payment_table.add_row(
                Text(payment.date, style="cyan"),
                Text(payment.account.site_number, style="cyan"),
                Text(payment.account.name, style="cyan"),
                Text(f"${payment.amount:,.2f}", style="green"),
                payment.type,
                payment.original_details,
            )

    def populate_unmatched(self) -> None:
        transactions = self.app_state.state.transactions
        transaction_table = self.query_one("#unmatched", DataTable)
        transaction_table.clear()
        for transaction in transactions:
            assert transaction.account is None
            transaction_table.add_row(
                Text(transaction.date, style="cyan"),
                Text(f"${transaction.amount:,.2f}", style="red"),
                transaction.original_details,
            )

    def action_back_screen(self):
        self.dismiss()

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:

            case "match":
                self.match_transactions()

            case "payments":
                self.proccess_paymets()

            case "unknown":
                self.proccess_unknown()

    @work
    async def match_transactions(self):
        matcher = Matcher(
            self.app_state.state.accounts, self.app_state.state.words_to_ignore
        )
        for transaction in self.app_state.state.transactions.copy():
            possibilities = match_transactions(matcher, transaction)

            if len(possibilities) == 0:
                match = await self.app.push_screen_wait(
                    AccountPicker(
                        f"No Matches For {transaction} Found, Please Pick An Account",
                        self.app_state.state.accounts,
                    )
                )
                if match is None:
                    continue
                else:
                    transaction.account = match
                    transaction.type = "Unknown"
                    self.app_state.state.remove_transaction(transaction)
                    self.app_state.state.add_payment(transaction)

            elif len(possibilities) == 1:
                transaction.account = possibilities[0]
                transaction.type = "Direct Debit"
                self.app_state.state.remove_transaction(transaction)
                self.app_state.state.add_payment(transaction)

            else:
                match = await self.app.push_screen_wait(
                    AccountPicker(
                        f"Multiple Matches for {transaction} Found, Please Pick An Account",
                        possibilities,
                    )
                )
                if match is None:
                    continue
                else:
                    transaction.account = match
                    transaction.type = "Direct Debit"
                    self.app_state.state.remove_transaction(transaction)
                    self.app_state.state.add_payment(transaction)
            self.populate_matched()
            self.populate_unmatched()

    def proccess_paymets(self):
        pass

    def proccess_unknown(self):
        pass
