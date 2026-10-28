import pyfiglet
from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, ContentSwitcher, DataTable, Footer, Header, Static


class AccountsMenu(Screen):

    BINDINGS = (
        Binding("q", "back_screen", "Back"),
        Binding("ctrl+w", "save_to_db", "Save"),
    )

    def compose(self):
        yield Header()
        yield Footer()

        title = pyfiglet.figlet_format("ACCOUNTS MENU")

        # yield Static(title, classes="header")

        with Horizontal(id="tabs"):
            yield Button("Overview", id="overview")
            yield Button("Accounts", id="accounts")
            yield Button("Balances", id="balances")
            yield Button("Site Holders", id="site_holders")

        with ContentSwitcher(initial="overview"):
            yield Static("Overview", id="overview")
            yield DataTable(id="accounts")
            yield DataTable(id="balances")
            yield DataTable(id="site_holders")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.query_one(ContentSwitcher).current = event.button.id

    def action_back_screen(self):
        self.app.pop_screen()

    def on_mount(self):
        self.populate_accounts_table()
        self.pupulate_balances_table()
        self.populate_holders_table()

    def populate_accounts_table(self):
        pass

    def pupulate_balances_table(self):
        pass

    def populate_holders_table(self):
        pass
