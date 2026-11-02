import pyfiglet
from textual.binding import Binding
from textual.containers import VerticalGroup
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from application import Application
from ui.accounts_menu.accounts_menu import AccountsMenu
from ui.export_menu.export_menu import ExportMenu
from ui.import_menu.import_menu import ImportMenu
from ui.settings_menu.settings_menu import SettingsMenu


class MainMenu(Screen):

    CSS_PATH = "main_menu.tcss"

    BINDINGS = (
        Binding("q", "quit_app", "Quit"),
        Binding("ctrl+w", "save_to_database", "Save Accounts To Database"),
        Binding("ctrl+l", "load_from_database", "Load Accounts From Database"),
    )

    def __init__(self, app: Application, **kwargs):
        super().__init__(id="main-menu", **kwargs)
        self.app_state = app

    def compose(self):
        # yield StatusBox(app=self.app_state, id="app-status")
        yield Header()
        yield Footer()

        title = pyfiglet.figlet_format("MAIN MENU")

        yield Static(title, classes="section-title")

        with VerticalGroup(id="buttons"):
            yield Button("Manage Accounts", id="accounts")
            yield Button("Matching Menu", id="payments")
            yield Button("Import Files", id="import")
            yield Button("Export Files", id="export")
            yield Button("Settings", id="settings")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:

            case "accounts":
                self.app.push_screen(AccountsMenu(self.app_state))

            case "payments":
                # self.app.push_screen(PaymentMenu(self.app_state))
                pass

            case "import":
                self.app.push_screen(ImportMenu(self.app_state))

            case "export":
                self.app.push_screen(ExportMenu(self.app_state))

            case "settings":
                self.app.push_screen(SettingsMenu(self.app_state))

    def action_save_to_database(self) -> None:
        self.app_state.repos.account_repo.save_accounts(self.app_state.state.accounts)
        self.app_state.repos.ignore_repo.replace_all_ignore(
            self.app_state.state.words_to_ignore
        )

    def action_load_from_database(self) -> None:
        self.app_state.load_from_db()
