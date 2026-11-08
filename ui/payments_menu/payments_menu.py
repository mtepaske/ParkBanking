from application import Application
from models.account import Account
from rich.text import Text
from services.match import Matcher, match_transactions
from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Static
from ui.custom_widgets import (
    AccountPicker,
    ConfirmUnknownScreen,
    ReviewBalanceScreen,
    ReviewUnknownScreen,
    StatusBox,
)


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
            yield DataTable(zebra_stripes=True, cursor_type="row", id="unmatched")

        with VerticalScroll(classes="section"):
            yield Static("Matched Tranactions", classes="section-title")
            yield DataTable(zebra_stripes=True, cursor_type="row", id="matched")

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

        self.find_available()

    def find_available(self):

        transactions = self.app_state.state.transactions
        accounts = self.app_state.state.accounts
        payments = self.app_state.state.payments
        unknown_words = self.app_state.state.unknown_words

        if len(transactions) > 0 and len(accounts) > 0:
            self.query_one("#match", Button).disabled = False

        if len(payments) > 0 and len(accounts) > 0:
            self.query_one("#payments", Button).disabled = False

        if len(unknown_words) > 0 and len(accounts) > 0:
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
                self.proccess_payments()

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

                if match == "None":
                    continue

                elif match is None:
                    self.notify("Matching Cancelled", severity="warning", timeout=5)
                    return

                else:
                    assert isinstance(match, Account)
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

                if match == "None":
                    continue

                elif match is None:
                    self.notify("Matching Cancelled", severity="warning", timeout=5)
                    return

                else:

                    assert isinstance(match, Account)
                    transaction.account = match
                    transaction.type = "Direct Debit"
                    self.app_state.state.remove_transaction(transaction)
                    self.app_state.state.add_payment(transaction)

            self.populate_matched()
            self.populate_unmatched()

        unknown_words = matcher.unknown

        for unknown in unknown_words:
            self.app_state.state.add_unknown(unknown)

        self.find_available()

    @work
    async def proccess_payments(self):

        payments = self.app_state.state.payments
        choice = await self.app.push_screen_wait(
            ReviewBalanceScreen("Reviewing Updated Balances", payments)
        )

        if choice:

            for payment in payments:

                account = payment.account
                assert account is not None
                balance = account.balance
                assert balance is not None

                balance.apply_transactions(balance.add_payment(payment.amount))

            self.notify(f"{len(payments)} Payments Applied", timeout=5)
            self.app_state.state.clear_payments()

        else:

            self.notify("Payment Proccessing Cancelled", severity="warning", timeout=5)

        self.find_available()

    @work
    async def proccess_unknown(self):

        ignore_to_add: set[str] = set()
        alias_to_add: dict[str, Account] = {}

        for unknown in self.app_state.state.unknown_words.copy():

            choice = await self.app.push_screen_wait(
                ReviewUnknownScreen(unknown, self.app_state.state.accounts)
            )

            match choice:

                case choice if isinstance(choice, Account):
                    alias_to_add[unknown] = choice

                case "ignore":
                    ignore_to_add.add(unknown)

                case "cancel":
                    self.notify(
                        "Unknown Words Proccessing Cancelled",
                        severity="warning",
                        timeout=5,
                    )
                    return

                case "skip-all":
                    break

                case None:
                    continue

        confirm = await self.app.push_screen_wait(
            ConfirmUnknownScreen(
                "Confirm The Following Changes", ignore_to_add, alias_to_add
            )
        )

        if confirm:

            for ignore in ignore_to_add:
                self.app_state.state.add_ignore(ignore)
                self.app_state.state.remove_unknown(ignore)

            for alias, account in alias_to_add.items():
                account.add_alias(alias)
                self.app_state.state.remove_unknown(alias)

            self.notify("Unknown Words Proccessed", timeout=5)
