from rich.text import Text
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, DataTable, Static

from models.account import Account
from services.match import Matcher, match_transactions
from ui.custom_widgets import (
    AccountPicker,
    Menu,
    ProccessUnknownScreen,
    ReviewBalanceScreen,
    ReviewUnknownScreen,
    StatusBox,
)


class PaymentMenu(Menu):
    """
    A menu for displaying and managing payments

    Attributes:
        CSS_PATH: (str) The name of the file containing styling information for the app
    """

    CSS_PATH = "payment_menu.tcss"

    def compose(self) -> ComposeResult:
        """Construct the widgets on the screen"""

        yield from super().compose()

        # Unmatched payments section
        with VerticalScroll(classes="section"):
            yield Static("Unmacthed Tranactions", classes="section-title")
            yield DataTable(zebra_stripes=True, cursor_type="row", id="unmatched")

        # Unapplied payments and charges section
        with VerticalScroll(classes="section"):
            yield Static("Unapplied Payments/Charges", classes="section-title")
            yield DataTable(zebra_stripes=True, cursor_type="row", id="matched")

        # Actions section
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
            yield StatusBox(app_state=self.app_state)

    def on_mount(self) -> None:
        """Initialise tables"""

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
        """Find available actions and enable/disable buttons"""

        transactions = self.app_state.state.transactions
        accounts = self.app_state.state.accounts
        unapplied = self.app_state.state.unapplied
        unknown_words = self.app_state.state.unknown_words

        if len(transactions) > 0 and len(accounts) > 0:
            self.query_one("#match", Button).disabled = False

        if len(unapplied) > 0 and len(accounts) > 0:
            self.query_one("#payments", Button).disabled = False

        if len(unknown_words) > 0 and len(accounts) > 0:
            self.query_one("#unknown", Button).disabled = False

    def populate_matched(self) -> None:
        """Populate unapplied payments/charges table"""

        unapplied = self.app_state.state.unapplied
        payment_table = self.query_one("#matched", DataTable)
        payment_table.clear()

        for payment in unapplied:

            assert payment.account is not None

            payment_table.add_row(
                Text(payment.date, style="cyan"),
                Text(payment.account.site_number, style="cyan"),
                Text(payment.account.name, style="cyan"),
                Text(f"${payment.amount:,.2f}", style="green"),
                payment.type,
                payment.details,
            )

    def populate_unmatched(self) -> None:
        """Populate unmatched transactions table"""

        transactions = self.app_state.state.transactions
        transaction_table = self.query_one("#unmatched", DataTable)
        transaction_table.clear()

        for transaction in transactions:

            assert transaction.account is None

            transaction_table.add_row(
                Text(transaction.date, style="cyan"),
                Text(f"${transaction.amount:,.2f}", style="red"),
                transaction.details,
            )

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Runs when a button is pressed

        Args:
            event: The button presss
        """

        match event.button.id:

            case "match":
                self.match_transactions()

            case "payments":
                self.proccess_payments()

            case "unknown":
                self.proccess_unknown()

    @work
    async def match_transactions(self):
        """Match unmatched transactions to accounts"""

        # Initialise matcher
        matcher = Matcher(
            self.app_state.state.accounts, self.app_state.state.words_to_ignore
        )

        # Run matching on transactions
        for transaction in self.app_state.state.transactions.copy():
            possibilities = match_transactions(matcher, transaction)

            # No match found
            if len(possibilities) == 0:
                match = await self.app.push_screen_wait(
                    AccountPicker(
                        "No Matches Found. Please Pick An Account",
                        f"Date: {transaction.date} - Amount: {transaction.amount} - Details: {transaction.details}",
                        self.app_state.state.accounts,
                    )
                )

                if match == "None":
                    continue

                elif match is None:
                    self.notify("Matching Cancelled", severity="warning", timeout=5)
                    break

                else:
                    assert isinstance(match, Account)
                    transaction.account = match
                    transaction.type = "Unknown"
                    self.app_state.state.remove_transaction(transaction)
                    self.app_state.state.add_unapplied(transaction)

            # Only one match found
            elif len(possibilities) == 1:
                transaction.account = possibilities[0]
                transaction.type = "Direct Debit"
                self.app_state.state.remove_transaction(transaction)
                self.app_state.state.add_unapplied(transaction)

            # Multiple matches found
            else:
                match = await self.app.push_screen_wait(
                    AccountPicker(
                        "Multiple Matches Found. Please Pick An Account",
                        f"Date: {transaction.date} - Amount: {transaction.amount} - Details: {transaction.details}",
                        possibilities,
                    )
                )

                if match == "None":
                    continue

                elif match is None:
                    self.notify("Matching Cancelled", severity="warning", timeout=5)
                    break

                else:
                    assert isinstance(match, Account)
                    transaction.account = match
                    transaction.type = "Direct Debit"
                    self.app_state.state.remove_transaction(transaction)
                    self.app_state.state.add_unapplied(transaction)

            # Update tables
            self.populate_matched()
            self.populate_unmatched()

        unknown_words = matcher.unknown

        # Update unknown words
        for unknown in unknown_words:
            self.app_state.state.add_unknown(unknown)

        self.find_available()

    @work
    async def proccess_payments(self):
        """Proccess unapplied payments and charges"""

        unapplied = self.app_state.state.unapplied.copy()
        accounts = self.app_state.state.accounts
        choice = await self.app.push_screen_wait(
            ReviewBalanceScreen("Reviewing Updated Balances", accounts, unapplied)
        )

        if choice:
            for transaction in unapplied:

                account = transaction.account
                assert account is not None
                balance = account.balance
                assert balance is not None

                balance.apply_new_amounts(balance.add_payment(transaction.amount))
                self.app_state.state.apply_unapplied(transaction)

            self.notify(f"{len(unapplied)} Payments Applied", timeout=5)

        else:
            self.notify("Payment Proccessing Cancelled", severity="warning", timeout=5)

        self.find_available()

    @work
    async def proccess_unknown(self):
        """Proccess unknown words"""

        ignore_to_add: set[str] = set()
        alias_to_add: dict[str, Account] = {}

        for unknown in self.app_state.state.unknown_words:

            choice = await self.app.push_screen_wait(
                ProccessUnknownScreen(unknown, self.app_state.state.accounts)
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
                    self.find_available()
                    return

                case "skip-all":
                    break

                case None:
                    continue

        # Confirm changes
        confirm = await self.app.push_screen_wait(
            ReviewUnknownScreen(
                "Confirm The Following Changes", ignore_to_add, alias_to_add
            )
        )

        if confirm:

            for ignore in ignore_to_add:
                self.app_state.state.add_ignore(ignore)
                self.app_state.state.remove_unknown(ignore)

            for alias, account in alias_to_add.items():
                account.aliases.add(alias)
                self.app_state.state.remove_unknown(alias)

            self.notify("Unknown Words Proccessed", timeout=5)

        self.find_available()
