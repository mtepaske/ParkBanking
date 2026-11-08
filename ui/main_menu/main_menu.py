import pyfiglet
from textual import on
from textual.containers import VerticalGroup
from textual.widgets import Button, Static

from ui.accounts_menu.accounts_menu import AccountsMenu
from ui.custom_widgets import Menu
from ui.export_menu.export_menu import ExportMenu
from ui.import_menu.import_menu import ImportMenu
from ui.payments_menu.payments_menu import PaymentMenu
from ui.settings_menu.settings_menu import SettingsMenu


class MainMenu(Menu):
    """
    The main menu of the application

    Attributes:
        CSS_PATH: (str) The name of the file containing styling information for the app
    """

    CSS_PATH = "main_menu.tcss"

    def compose(self):
        """Construct the widgets on the screen"""

        yield from super().compose()
        title = pyfiglet.figlet_format("MAIN MENU")

        yield Static(title, classes="section-title")

        # The buttons
        with VerticalGroup(id="buttons"):
            yield Button("Manage Accounts", id="accounts")
            yield Button("Matching Menu", id="payments")
            yield Button("Import Files", id="import")
            yield Button("Export Files", id="export")
            yield Button("Settings", id="settings")

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Runs when a button is pressed

        Args:
            event: The button presss
        """

        match event.button.id:

            case "accounts":
                self.app.push_screen(
                    AccountsMenu(app_state=self.app_state, id="accounts-menu")
                )

            case "payments":
                self.app.push_screen(
                    PaymentMenu(app_state=self.app_state, id="payments-menu")
                )

            case "import":
                self.app.push_screen(
                    ImportMenu(app_state=self.app_state, id="import-menu")
                )

            case "export":
                self.app.push_screen(
                    ExportMenu(app_state=self.app_state, id="export-menu")
                )

            case "settings":
                self.app.push_screen(
                    SettingsMenu(app_state=self.app_state, id="settings-menu")
                )
