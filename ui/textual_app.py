from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from services.settings import get_setting
from ui.main_menu import MainMenu
from application import Application


class Parkbanking(App):

    def __init__(self):
        super().__init__()
        self.state = 

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        self.title = get_setting("business_name")
        self.sub_title = "Accounts And Payment Manager"
        self.app.push_screen(MainMenu())
