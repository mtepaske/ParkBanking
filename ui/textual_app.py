from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from application import Application, AppRepositories
from services.database import AccountRepository, IgnoreRepository, connect
from services.settings import get_setting
from ui.main_menu import MainMenu


class Parkbanking(App):

    def __init__(self):
        super().__init__()
        self.connection = connect()
        app = Application(
            AppRepositories(
                AccountRepository(self.connection), IgnoreRepository(self.connection)
            )
        )
        self.app_state = app
        self.app_state.load_from_db()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        self.title = get_setting("business_name")
        self.sub_title = "Accounts And Payment Manager"
        self.app.push_screen(MainMenu(self.app_state))
