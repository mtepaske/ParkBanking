from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, ContentSwitcher, DataTable, Footer, Header, Static

from application import Application
from ui.accounts_menu.view_account_menu import ViewAccountMenu


class AccountsMenu(Screen):
    """
    A screen to view all account information

    Attributes:
        CSS_PATH: The path of the .tcss file for this screen
        BINDINGS: The key bindings for this screen
        app_state: The application instance for tracking state
    """

    CSS_PATH = "accounts_menu.tcss"
    BINDINGS = (
        Binding("q", "back_screen", "Back"),
        Binding("ctrl+w", "save_to_database", "Save Accounts To Database"),
        Binding("ctrl+l", "load_from_database", "Load Accounts From Database"),
    )

    def __init__(self, app: Application, **kwargs) -> None:
        """
        Initialise the instance

        Args:
            app: The application instance for tracking state
        """

        super().__init__(id="accounts-menu", **kwargs)
        self.app_state = app

    def compose(self) -> ComposeResult:
        """Construct the widgets on the screen"""

        # Show program name and keybindings
        yield Header()
        yield Footer()

        # The content switcher tabs
        with Horizontal(classes="tabs"):
            yield Button("Overview", id="tab_overview")
            yield Button("Accounts", id="tab_accounts")
            yield Button("Balances", id="tab_balances")
            yield Button("Site Holders", id="tab_site_holders")

        # The content switcher to view different account information
        with ContentSwitcher(initial="overview", classes="tables"):
            yield Static("Overview", id="overview")
            yield DataTable(id="accounts", cursor_type="row", zebra_stripes=True)
            yield DataTable(id="balances", cursor_type="row", zebra_stripes=True)
            yield DataTable(id="site_holders", cursor_type="row", zebra_stripes=True)

    def action_back_screen(self) -> None:
        """Go back to the main menu"""

        self.dismiss()

    def action_save_to_database(self) -> None:
        """Save updates to the database"""

        self.app_state.repos.account_repo.save_accounts(self.app_state.state.accounts)
        self.app_state.repos.ignore_repo.save_all_ignore(
            self.app_state.state.words_to_ignore
        )

    def action_load_from_database(self) -> None:
        """Load account information from the database"""

        self.app_state.load_from_db()

    def on_mount(self) -> None:
        """Initialise the datatables"""

        # Initialise the accounts table
        accounts_table = self.query_one("#accounts", DataTable)
        accounts_table.add_columns(
            "ID", "Site Holder", "Site Number", "Aliases", "Balance"
        )
        self.populate_accounts_table()

        # Initialise the balances table
        balances_table = self.query_one("#balances", DataTable)
        balances_table.add_columns(
            "ID",
            "Site Holder",
            "Annual Fees",
            "Remaining From This FY",
            "Outstaning From Previous FYs",
            "Credit",
            "Total Balance",
        )
        self.populate_balances_table()

        # Initialise the site holders table
        holders_table = self.query_one("#site_holders", DataTable)
        holders_table.add_columns(
            "ID",
            "Site Holder",
            "Phone Number",
            "Email Address",
            "Nominated Visitors",
            "Postal Address",
        )
        self.populate_holders_table()

    def populate_overview(self) -> None:
        """Populate the overview view"""
        # Overview should have
        # - Total amount of arrears and a list of accounts in arrears
        # - Total nmumber of sites
        # - Total number of loaded accounts
        # - Total amount of visitor fees for the previous month

    def populate_accounts_table(self) -> None:
        """Populate the accounts table"""

        accounts = self.app_state.state.accounts
        accounts_table = self.query_one("#accounts", DataTable)

        # Clear the current information
        accounts_table.clear(columns=False)

        # Add updated information
        for account in accounts:
            assert account.balance is not None
            style = "green" if account.balance.check_on_track() else "red"
            accounts_table.add_row(
                Text(f"{account.account_id}", style="cyan"),
                Text(f"{account.name}", style="cyan"),
                Text(f"{account.site_number}"),
                Text(f"{account.aliases}"),
                Text(f"${account.balance.balance:,.2f}", style=style),
                # Set the row key to the accounts database ID if its been previously inserted to the database
                key=(
                    str(account.account_id) if account.account_id is not None else None
                ),
            )

    def populate_balances_table(self) -> None:
        """Populate the balances table"""

        accounts = self.app_state.state.accounts
        balances_table = self.query_one("#balances", DataTable)

        # Clear the current information
        balances_table.clear(columns=False)

        # Add updated information
        for account in accounts:
            balance = account.balance
            assert balance is not None
            style = "green" if balance.check_on_track() else "red"
            balances_table.add_row(
                Text(f"{account.account_id}", style="cyan"),
                Text(f"{account.name}", style="cyan"),
                Text(f"{balance.annual}"),
                Text(f"${balance.remaining:,.2f}", style=style),
                Text(f"${balance.outstanding:,.2f}", style=style),
                Text(f"${balance.credit:,.2f}", style=style),
                Text(f"${balance.balance:,.2f}", style=style),
                # Set the row key to the accounts database ID if its been previously inserted to the database
                key=(
                    str(account.account_id) if account.account_id is not None else None
                ),
            )

    def populate_holders_table(self) -> None:
        """Populate the site holders table"""
        # accounts = self.app_state.state.accounts
        # holders_table = self.query_one("#site_holders", DataTable)
        #
        # holders_table.clear(columns=False)

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Runs when a button is pressed

        Args:
            event: The button press that triggered the method
        """

        if event.button.id in {
            "tab_overview",
            "tab_accounts",
            "tab_balances",
            "tab_site_holders",
        }:
            screen_id = event.button.id.removeprefix("tab_")
            self.query_one(ContentSwitcher).current = screen_id

    @on(DataTable.RowSelected)
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """
        Runs when a row is selected

        Args:
            event: The event that triggered the method
        """

        account_id = event.row_key.value

        # If the selected account has no database ID
        if account_id is None:
            selected: list[Text] = event.data_table.get_row(event.row_key)

            for account in self.app_state.state.accounts:

                if selected[1].plain == account.name:
                    self.app.push_screen(
                        ViewAccountMenu(app=self.app_state, account=account),
                        callback=self.on_screen_close,
                    )
                    return

        # If the selected account has a database ID
        else:

            for account in self.app_state.state.accounts:

                if account_id == str(account.account_id):
                    self.app.push_screen(
                        ViewAccountMenu(app=self.app_state, account=account),
                        callback=self.on_screen_close,
                    )
                    return

    def on_screen_close(self, result=None) -> None:
        """Updates tables with updated accounts information after the view accounts screen closes"""

        self.populate_accounts_table()
        self.populate_balances_table()
        self.populate_holders_table()
