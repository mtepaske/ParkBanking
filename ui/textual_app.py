from textual.app import App

from application import Application, AppRepositories
from services.database import (
    AccountRepository,
    IgnoreRepository,
    connect,
    initialise_database,
)
from services.settings import get_setting
from ui.main_menu.main_menu import MainMenu


class Parkbanking(App):
    """
    The textual app that displays the screen

    Attributes:
        CSS_PATH: (str) The name of the file containing styling information for the app
        connection: (sqlite3.Connection) The database connection
        app_state: (Application) The state of the application
        title: (str) The screen title
        sub_title: (str) The screen subtitle
    """

    # CSS_PATH = "app.tcss"
    CSS_PATH = "new_app.tcss"

    def __init__(self):
        """Initialise the application"""

        super().__init__()

        # Connect to the database and initialise repositories
        self.connection = connect()
        app = Application(
            AppRepositories(
                AccountRepository(self.connection), IgnoreRepository(self.connection)
            )
        )

        # Initialise the database
        initialise_database(self.connection)

        self.app_state = app

        # If auto load is set, load from the database
        if get_setting("auto_load_from_db") == "True":
            self.app_state.load_from_db()

    def on_mount(self) -> None:
        """On starting of the app"""

        self.title = get_setting("business_name")
        self.sub_title = "Accounts And Payment Manager"
        self.app.push_screen(MainMenu(app_state=self.app_state))
