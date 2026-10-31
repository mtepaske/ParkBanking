import pyfiglet
from textual.binding import Binding
from textual.containers import VerticalGroup
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from application import Application
from ui.accounts_menu.accounts_menu import AccountsMenu


class MainMenu(Screen):

    CSS_PATH = "main_menu.tcss"

    BINDINGS = (
        Binding("q", "quit_app", "Quit"),
        Binding("ctrl+w", "save_to_db", "Save"),
    )

    def __init__(self, app: Application):
        super().__init__()
        self.app_state = app

    def compose(self):
        yield Header()
        yield Footer()

        title = pyfiglet.figlet_format("MAIN MENU")

        yield VerticalGroup(
            Static(title, classes="header"),
            VerticalGroup(
                Button("Manage Accounts", id="accounts"),
                Button("Matching Menu"),
                Button("Import Files"),
                Button("Export Files"),
                Button("Settings"),
                id="buttons",
            ),
            id="menu",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "accounts":
            self.app.push_screen(AccountsMenu(self.app_state))
