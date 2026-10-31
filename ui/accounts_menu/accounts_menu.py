from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, ContentSwitcher, DataTable, Footer, Header, Static

from application import Application
from ui.accounts_menu.view_account_menu import ViewAccountMenu


class AccountsMenu(Screen):

    CSS_PATH = "accounts_menu.tcss"

    BINDINGS = (
        Binding("q", "back_screen", "Back"),
        Binding("ctrl+w", "save_to_db", "Save"),
    )

    def __init__(self, app: Application) -> None:
        super().__init__()
        self.app_state = app

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        # title = pyfiglet.figlet_format("ACCOUNTS MENU")

        # yield Static(title, classes="header")

        with Horizontal(id="tabs"):
            yield Button("Overview", id="tab_overview")
            yield Button("Accounts", id="tab_accounts")
            yield Button("Balances", id="tab_balances")
            yield Button("Site Holders", id="tab_site_holders")

        with ContentSwitcher(initial="overview"):
            yield Static("Overview", id="overview")
            yield DataTable(id="accounts", cursor_type="row", zebra_stripes=True)
            yield DataTable(id="balances", cursor_type="row", zebra_stripes=True)
            yield DataTable(id="site_holders", cursor_type="row", zebra_stripes=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id in {
            "tab_overview",
            "tab_accounts",
            "tab_balances",
            "tab_site_holders",
        }:
            screen_id = event.button.id.removeprefix("tab_")
            self.query_one(ContentSwitcher).current = screen_id

    def action_back_screen(self) -> None:
        self.dismiss()

    def on_mount(self) -> None:

        accounts_table = self.query_one("#accounts", DataTable)
        accounts_table.add_columns(
            "ID", "Site Holder", "Site Number", "Aliases", "Balance"
        )
        self.populate_accounts_table()

        balances_table = self.query_one("#balances", DataTable)
        balances_table.add_columns(
            "ID",
            "Site Holder",
            "Remaining From This FY",
            "Outstaning From Previous FYs",
            "Credit",
            "Total Balance",
        )
        self.populate_balances_table()

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

    def populate_overview(self):
        pass
        # Overview should have
        # - Total amount of arrears and a list of accounts in arrears
        # - Total nmumber of sites
        # - Total number of loaded accounts
        # - Total amount of visitor fees for the previous month

    def populate_accounts_table(self):

        accounts = self.app_state.state.accounts
        accounts_table = self.query_one("#accounts", DataTable)

        accounts_table.clear(columns=False)

        for account in accounts:
            if account.balance is not None:
                style = "green" if account.balance.check_on_track() else "red"
                accounts_table.add_row(
                    Text(f"{account.account_id}", style="cyan"),
                    Text(f"{account.name}", style="cyan"),
                    account.site_number,
                    account.aliases,
                    Text(f"${account.balance.balance:,.2f}", style=style),
                    key=str(account.account_id),
                )
            else:
                accounts_table.add_row(
                    Text(f"{account.account_id}", style="cyan"),
                    Text(f"{account.name}", style="cyan"),
                    account.site_number,
                    account.aliases,
                    "None",
                    key=str(account.account_id),
                )

    def populate_balances_table(self) -> None:

        accounts = self.app_state.state.accounts
        balances_table = self.query_one("#balances", DataTable)

        balances_table.clear(columns=False)

        for account in accounts:
            balance = account.balance
            if balance is not None:
                style = "green" if balance.check_on_track() else "red"
                balances_table.add_row(
                    Text(f"{account.account_id}", style="cyan"),
                    Text(f"{account.name}", style="cyan"),
                    Text(f"${balance.remaining:,.2f}", style=style),
                    Text(f"${balance.outstanding:,.2f}", style=style),
                    Text(f"${balance.credit:,.2f}", style=style),
                    Text(f"${balance.balance:,.2f}", style=style),
                    key=str(account.account_id),
                )

    def populate_holders_table(self) -> None:

        accounts = self.app_state.state.accounts
        holders_table = self.query_one("#site_holders", DataTable)

        holders_table.clear(columns=False)

        # Populate with data when site class is implimented

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:

        if event.data_table.id == "overview":
            return

        account_id = event.row_key.value
        assert (
            account_id is not None
        )  # Will have to select some otherway for new accounts

        self.app.push_screen(
            ViewAccountMenu(app=self.app_state, account_id=int(account_id)),
            callback=self.on_screen_close,
        )
        return

    def on_screen_close(self, result=None) -> None:
        self.populate_accounts_table()
        self.populate_balances_table()
        self.populate_holders_table()
