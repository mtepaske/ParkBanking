from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import (
    Horizontal,
    HorizontalGroup,
    VerticalGroup,
)
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Static

from application import Application
from services.settings import get_setting


class SettingsMenu(Screen):

    CSS_PATH = "settings_menu.tcss"

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

        with Horizontal():

            with VerticalGroup():
                yield Static("BUSINESS SETTINGS", classes="section-title")

                with HorizontalGroup(classes="input-row"):
                    yield Static("Business Name: ", classes="input-label")
                    yield Input(value=get_setting("business_name"), id="business-name")

            with VerticalGroup():
                yield Static("DATA SETTINGS", classes="section-title")

            with VerticalGroup():
                yield Static("FEE SETTINGS", classes="section-title")
