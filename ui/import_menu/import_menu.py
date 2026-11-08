from pathlib import Path

from rich.text import Text
from textual import on, work
from textual.app import ComposeResult
from textual.containers import (
    HorizontalGroup,
    Vertical,
    VerticalGroup,
    VerticalScroll,
)
from textual.widgets import (
    Button,
    Collapsible,
    DataTable,
    DirectoryTree,
    Static,
)

from application import (
    DuplicateAccount,
    DuplicateTransaction,
    MissingBalance,
)
from models.account import Account
from models.transactions import Transaction
from services.imports import (
    import_account_info_from_csv,
    import_accounts,
    import_history,
    import_matched,
    import_statement,
    import_words_to_ignore,
)
from services.settings import APP_DIRECTORY, get_setting
from ui.custom_widgets import (
    AccountPicker,
    AppendScreen,
    ConfirmChargesScreen,
    ImportBalancesScreen,
    Menu,
    StatusBox,
)


class ImportMenu(Menu):
    """
    A menu to import CSV files

    Attributes:
        CSS_PATH: (str) The name of the file containing styling information for the app
        import_folder: (Path) The path of the folder to import from
        loaded_file: (Iterable) The information of the current loaded file
        loaded_file_type: (str) The type of loaded file
    """

    CSS_PATH = "import_menu.tcss"

    def __init__(self, **kwargs) -> None:
        """Initialise the menu"""

        super().__init__(**kwargs)
        self.import_folder = APP_DIRECTORY / get_setting("imports_folder")
        self.loaded_file = None
        self.loaded_file_type = None
        self._generated_charges = None
        self._account_for_history = None

    def compose(self) -> ComposeResult:
        """Construct the widgets on the screen"""

        yield from super().compose()

        # File selection section
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
                    title="Import Accounts",
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

            yield StatusBox(self.app_state)

        # File preview section
        with Vertical(classes="section"):

            yield Static("File Preview", classes="section-title")
            yield DataTable(zebra_stripes=True, id="file-preview")

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed):
        """
        Runs when a button is pressed

        Args:
            event: The button presss
        """

        if event.button.id == "confirm":
            match self.loaded_file_type:

                case "statement":
                    self.import_statement()

                case "matched":
                    self.import_matched()

                case "account":
                    self.import_accounts()

                case "history":
                    self.import_history()

                case "site":
                    pass

                case "ignore":
                    self.import_ignore()

    @on(DirectoryTree.FileSelected)
    def on_directiory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        """
        Runs when a file is selected

        Args:
            event: The event of the file selection
        """

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
        """
        Preview an bank statement before importing

        Args:
            filepath: The path of the file
        """

        # Try to load the selected file
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

        # Preview selected file
        statement_table = self.query_one("#file-preview", DataTable)
        statement_table.clear(columns=True)
        statement_table.add_columns("Date", "Amount", "Transaction Details")

        for row in self.loaded_file:
            statement_table.add_row(row.date, row.amount, row.details)

        self.loaded_file_type = "statement"
        self.query_one("#confirm", Button).disabled = False

    def preview_matched(self, filepath: Path):
        """
        Preview matched transactions before importing

        Args:
            filepath: The path of the file
        """

        # Checks there is loaded accounts
        if len(self.app_state.state.accounts) == 0:
            self.notify(
                "No Accounts To Match Against. Transactions Will Be Unmatched",
                severity="warning",
                timeout=5,
            )

        # Try to load the selected file
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

        # Preview the selected file
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

    @work
    async def preview_accounts(self, filepath: Path):
        """
        Preview accounts before imporing

        Args:
            filepath: The path of the file
        """

        # Try to load the selected file
        try:
            self.loaded_file = import_accounts(str(filepath).removesuffix(".csv"))
        except FileNotFoundError:
            self.notify("File No Longer Exists", severity="error", timeout=5)
            return
        except KeyError:
            self.notify(
                "This File Does Not Contain Accounts Information",
                severity="error",
                timeout=5,
            )
            return

        # Ask for and import balance information. Match to accounts
        balance_filepath = await self.app.push_screen_wait(
            ImportBalancesScreen(self.import_folder)
        )
        if balance_filepath is None:
            self.notify("Account Import Cancelled", severity="warning", timeout=5)
            return

        # Try to load the selected file
        try:
            self.loaded_file, self._generated_charges = import_account_info_from_csv(
                str(filepath).removesuffix(".csv"),
                str(balance_filepath).removesuffix(".csv"),
            )
        except FileNotFoundError:
            self.notify("File No Longer Exists", severity="error", timeout=5)
            return
        except KeyError:
            self.notify(
                "This File Does Not Contain Balance Imformation",
                severity="error",
                timeout=5,
            )
            return
        except MissingBalance:
            self.notify("Account Information Does Not Match Balance Information")
            return

        # Preview the file
        account_table = self.query_one("#file-preview", DataTable)
        account_table.clear(columns=True)
        account_table.add_columns(
            "Site Number",
            "Name",
            "Aliases",
            "Active",
            "Account ID",
            "Annual Fees",
            "Remaining",
            "Outstanding",
            "Pay Frequency",
            "Balance ID",
        )

        for row in self.loaded_file:
            assert row.balance is not None
            account_table.add_row(
                row.site_number,
                row.name,
                row.aliases,
                row.active,
                row.account_id,
                row.balance.annual,
                row.balance.remaining,
                row.balance.outstanding,
                row.balance.pay_frequency,
                row.balance.balance_id,
            )

        self.loaded_file_type = "account"
        self.query_one("#confirm", Button).disabled = False

    @work
    async def preview_history(self, filepath: Path):
        """
        Preview account history before importing

        Args:
            filepath: The path of the file
        """

        # Select the account to import the history of
        self._account_for_history = await self.app.push_screen_wait(
            AccountPicker("For Which Account?", self.app_state.state.accounts)
        )
        if self._account_for_history is None or self._account_for_history == "None":
            self.notify(
                "Account History Import Cancelled", severity="warning", timeout=5
            )
            return

        assert isinstance(self._account_for_history, Account)

        # Try to load the selected file
        try:
            self.loaded_file = import_history(
                str(filepath).removesuffix(".csv"), account=self._account_for_history
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

        # Preview the selected file
        history_table = self.query_one("#file-preview", DataTable)
        history_table.clear(columns=True)
        history_table.add_columns("Date", "Description", "Debit", "Credit", "Balance")

        self.loaded_file.sort(key=lambda t: t.date, reverse=True)

        assert self._account_for_history.balance is not None
        running_balance = self._account_for_history.balance.balance
        rows = []
        for payment in self.loaded_file:
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

        rows.reverse()

        for date, description, debit, credit, balance in rows:
            history_table.add_row(
                Text(date, style="cyan"),
                description,
                Text(debit, style="red"),
                Text(credit, style="green"),
                balance,
            )

        self.loaded_file_type = "history"
        self.query_one("#confirm", Button).disabled = False

    def preview_site(self, filepath: Path):
        """
        Preview site information before importing

        Args:
            filepath: The path of the file
        """

        site_table = self.query_one("#file-preview", DataTable)
        site_table.clear(columns=True)
        site_table.add_columns()
        # Conplete when sites are implimented

    def preview_ignore(self, filepath: Path):
        """
        Preview words to ignore before importing

        Args:
            filepath: The path of the file
        """

        # Try to load the selected file
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

        # Preview the selected file
        ignore_table = self.query_one("#file-preview", DataTable)
        ignore_table.clear(columns=True)
        ignore_table.add_columns("Word")

        for row in self.loaded_file:
            ignore_table.add_row(row)

        self.loaded_file_type = "ignore"
        self.query_one("#confirm", Button).disabled = False

    @work
    async def import_statement(self):
        """Import selected file as unmatched transactions"""

        assert self.loaded_file is not None

        # Sets the original application state
        original_state = self.app_state.state.transactions.copy()

        # If there is currently loaded unmatched transactions, append or replace
        if len(self.app_state.state.transactions) != 0:

            if get_setting("append_transactions_on_import") == "Never":
                self.app_state.state.clear_transactions()
                self.notify("Transactions Cleared", severity="warning", timeout=5)

            elif get_setting("append_transactions_on_import") == "Ask":
                choice = await self.app.push_screen_wait(
                    AppendScreen(
                        message="Add To Or Replace Previously Loaded Transactions?"
                    )
                )

                if choice == "replace":
                    self.app_state.state.clear_transactions()
                    self.notify("Transactions Cleared", severity="warning", timeout=5)
                elif choice is None or choice == "cancel":
                    self.notify(
                        "Statement Import Cancelled", severity="warning", timeout=5
                    )
                    return

        for transaction in self.loaded_file:
            assert isinstance(transaction, Transaction)

            while True:
                try:
                    self.app_state.state.add_transaction(transaction)
                    break

                # If there is a duplicate transaction
                except DuplicateTransaction:
                    confirm = await self.app.push_screen_wait(
                        AppendScreen(
                            f"{transaction} Matches A Transaction Thats Already Loaded"
                        )
                    )

                    if confirm == "replace":
                        self.notify("Transaction Replaced", timeout=5)
                        break
                    elif confirm is None or confirm == "cancel":
                        self.app_state.state.transactions = original_state
                        self.notify(
                            "Statement Import Cancelled", severity="warning", timeout=5
                        )
                        return

                    else:
                        transaction.details = f"{transaction.details} (Duplicate)"
                        self.notify(
                            f"Transaction Details Have Been Changed To {transaction.details}",
                            timeout=5,
                        )

        self.query_one("#confirm", Button).disabled = True
        self.query_one("#file-preview", DataTable).clear(columns=True)

    @work
    async def import_matched(self):
        """Import selected file as matched transactions"""

        assert self.loaded_file is not None

        unmatched_to_add = []
        matched_to_add = []
        choice = None

        for transaction in self.loaded_file:
            assert isinstance(transaction, Transaction)

            # If the transaction has no matched account
            if transaction.account is None:
                # If there is currently loaded unmatched transactions, append or replace
                if len(self.app_state.state.transactions) != 0:

                    if (
                        choice is None
                        and get_setting("append_transactions_on_import") == "Ask"
                    ):
                        choice = await self.app.push_screen_wait(
                            AppendScreen(
                                "Add To Or Replace Previously Loaded Transactions?"
                            )
                        )
                        if choice == "replace":
                            self.app_state.state.clear_transactions()
                            self.notify(
                                "Transactions Cleared", severity="warning", timeout=5
                            )
                        elif choice is None or choice == "cancel":
                            self.notify(
                                "Matched Statement Import Cancelled",
                                severity="warning",
                                timeout=5,
                            )
                            return

                    elif get_setting("append_transactions_on_import") == "Never":
                        self.app_state.state.clear_transactions()
                        self.notify(
                            "Transactions Cleared", severity="warning", timeout=5
                        )

                unmatched_to_add.append(transaction)

            else:
                matched_to_add.append(transaction)

        # Sets the original application state
        original_transactions = self.app_state.state.transactions.copy()
        for unmatched in unmatched_to_add:

            while True:
                try:
                    self.app_state.state.add_transaction(unmatched)
                    break

                # If there is a duplicate transaction
                except DuplicateTransaction:
                    confirm = await self.app.push_screen_wait(
                        AppendScreen(
                            f"{unmatched} Matches A Transaction Thats Already Loaded"
                        )
                    )

                    if confirm == "replace":
                        break

                    elif confirm is None or confirm == "cancel":
                        self.app_state.state.transactions = original_transactions
                        self.app_state.state.notify_changed()
                        self.notify(
                            "Matched Statement Import Cancelled",
                            severity="warning",
                            timeout=5,
                        )
                        return

                    else:
                        unmatched.details = f"{unmatched.details} (Duplicate)"
                        self.notify(
                            f"Unmatched Transaction Details Have Been Chnaged To {unmatched.details}",
                            timeout=5,
                        )

        # Sets the original application state
        original_payments = self.app_state.state.unapplied.copy()

        for matched in matched_to_add:

            while True:
                try:
                    self.app_state.state.add_unapplied(matched)
                    break

                # If there is a duplicate transaction
                except DuplicateTransaction:
                    confirm = await self.app.push_screen_wait(
                        AppendScreen(
                            f"{matched} Matches A Payment Thats Already Loaded"
                        )
                    )

                    if confirm == "replace":
                        break

                    elif confirm is None or confirm == "cancel":
                        self.app_state.state.unapplied = original_payments
                        self.app_state.state.transactions = original_transactions
                        self.app_state.state.notify_changed()
                        self.notify("Matched Statement Import Cancelled")
                        return

                    else:
                        matched.details = f"{matched.details} (Duplicate)"
                        self.notify(
                            f"Matched Transaction Details Have Been Chnaged To {matched.details}",
                            timeout=5,
                        )

        self.query_one("#confirm", Button).disabled = True
        self.query_one("#file-preview", DataTable).clear(columns=True)

    @work
    async def import_accounts(self):
        """Import selected file as accounts"""

        assert self.loaded_file is not None
        assert self._generated_charges is not None

        # If there is currently loaded unmatched accounts, append or replace
        if len(self.app_state.state.accounts) != 0:

            if get_setting("append_accounts_on_import") == "Never":
                self.app_state.state.clear_accounts()
                self.notify("Accounts Cleared", timeout=5)

            elif get_setting("append_accounts_on_import") == "Ask":
                choice = await self.app.push_screen_wait(
                    AppendScreen(
                        message="Add To Or Replace Previously Loaded Accounts?"
                    )
                )

                if choice == "replace":
                    self.app_state.state.clear_accounts()
                elif choice is None or choice == "cancel":
                    return

        # Confirm autonmatically generated charges
        charge_confirm = await self.app.push_screen_wait(
            ConfirmChargesScreen(
                message="Please Confirm Autonmatically Generated Charges Are Correct",
                charges=self._generated_charges,
            )
        )

        if not charge_confirm:
            self.notify("Account Import Cancelled", severity="warning", timeout=5)
            return

        # Sets the original application state
        original_accounts = self.app_state.state.accounts.copy()
        for account in self.loaded_file:
            assert isinstance(account, Account)

            while True:
                try:
                    self.app_state.state.add_account(account)
                    break

                # If there is a duplicate account
                except DuplicateAccount:
                    confirm = AppendScreen(
                        f"There is Already An Active Account For {account.site_number}"
                    )
                    if confirm == "replace":
                        self.app_state.state.deactivate_by_site_number(
                            account.site_number
                        )
                        self.notify(
                            f"Existing Account For {account.site_number} Now Inactive",
                            timeout=5,
                        )
                    elif confirm is None or confirm == "cancel":
                        self.app_state.state.accounts = original_accounts
                        self.app_state.state.notify_changed()
                        self.notify("Accounts Import Cancelled", timeout=5)
                        return
                    else:
                        account.switch_active()
                        self.notify(f"{account} Swicthed To Inactive")

        # Sets the original application state
        original_charges = self.app_state.state.charges.copy()
        for charge in self._generated_charges:
            assert isinstance(charge, Transaction)

            while True:
                try:
                    self.app_state.state.add_charge(charge)
                    break

                # If there is a duplicate transaction
                except DuplicateTransaction:
                    confirm = await self.app.push_screen_wait(
                        AppendScreen(
                            f"The Generated Charge {charge} Matches A Charge Thats Already Loaded"
                        )
                    )

                    if confirm == "replace":
                        break

                    elif confirm is None or confirm == "cancel":
                        self.app_state.state.charges = original_charges
                        self.app_state.state.accounts = original_accounts
                        self.app_state.state.notify_changed()
                        self.notify("Accounts Import Cancelled", timeout=5)
                        return

                    else:
                        charge.details = f"{charge.details} (Duplicate)"
                        self.notify(
                            f"Charge Details Have Been Changed To {charge.details}",
                            timeout=5,
                        )

        self.query_one("#confirm", Button).disabled = True
        self.query_one("#file-preview", DataTable).clear(columns=True)

    @work
    async def import_history(self):
        """Import selected file as account history"""

        assert self.loaded_file is not None
        assert isinstance(self._account_for_history, Account)
        transactions_to_add = []

        for payment in self.loaded_file:

            assert isinstance(payment, Transaction)
            transactions_to_add.append(payment)

        # Checks for history in the database
        if self._account_for_history.account_id is not None:

            database_charges = self.app_state.repos.account_repo.get_history(
                self._account_for_history.account_id
            )

            if len(database_charges) != 0:
                delete_previous = await self.app.push_screen_wait(
                    ConfirmChargesScreen(
                        message="The Following Charges And Payments Were Found In The Database, Would You Like To Delete Them?",
                        charges=database_charges,
                    )
                )
                if delete_previous is None:
                    self.notify(
                        "Account History Import Cancelled",
                        severity="warning",
                        timeout=5,
                    )
                    return
                elif delete_previous is True:
                    self.app_state.repos.account_repo.delete_history_by_account(
                        self._account_for_history
                    )
                    self.notify(
                        f"Account History For Acccount {self._account_for_history.account_id} Deleted From Database",
                        timeout=5,
                    )

        # Checks for unsaved history
        charges_to_delete = []
        for charge in self.app_state.state.charges:
            if charge.account == self._account_for_history:
                charges_to_delete.append(charge)

        if len(charges_to_delete) != 0:
            delete_previous = await self.app.push_screen_wait(
                ConfirmChargesScreen(
                    message="The Following Charges And Payments Were Found In The History, Would You Like To Delete Them?",
                    charges=charges_to_delete,
                )
            )
            if delete_previous is None:
                self.notify(
                    "Account History Import Cancelled", severity="warning", timeout=5
                )
                return
            elif delete_previous is True:
                for charge in charges_to_delete:
                    self.app_state.state.remove_charge(charge)
                self.notify(
                    f"Account History For Acccount {self._account_for_history.account_id} Deleted",
                    timeout=5,
                )

        for transaction in transactions_to_add:
            if transaction.amount > 0:
                self.app_state.state.add_payment(transaction)
            else:
                self.app_state.state.add_charge(transaction)

        self.query_one("#confirm", Button).disabled = True
        self.query_one("#file-preview", DataTable).clear(columns=True)

    def import_ignore(self):
        """Import selected file as words to ignore"""

        assert self.loaded_file is not None

        for word in self.loaded_file:
            assert isinstance(word, str)
            self.app_state.state.add_ignore(word)

        self.query_one("#confirm", Button).disabled = True
        self.query_one("#file-preview", DataTable).clear(columns=True)
