from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import (
    Footer,
    Header,
)

from application import Application
from services.settings import get_setting
from ui.widgets.dialog import Dialog


class Menu(Screen):
    """
    A menu screen

    Attributes:
        BINDINGS: (tuple[Binding]) The key bindings for the menu
        app_state: (Application) The application state
    """

    BINDINGS = (
        Binding("Q", "quit", "Quit Application"),
        Binding("q", "back", "Back"),
        Binding("ctrl+w", "save", "Save"),
        Binding("ctrl+l", "load", "Load"),
    )

    def __init__(self, app_state: Application, **kwargs):
        """
        Initialise the class

        Args:
            app_state: The application state
            **kwargs: Other keyword arguments for the base class
        """

        super().__init__(**kwargs)
        self.app_state = app_state

    def compose(self) -> ComposeResult:
        """Construct the widgets on the screen"""

        yield Header()
        yield Footer()

    @work
    async def action_quit(self) -> None:
        """Quit the program"""

        # Saves depending on settings
        if get_setting("auto_save_to_db") == "True":
            self.action_save()
            self.app.exit()
        else:
            confirm = await self.app.push_screen_wait(
                Dialog("Unsaved Progress Will Be Lost. Do You Want To Continue?")
            )
            if confirm:
                self.app.exit()
            else:
                return

    def action_back(self) -> None:
        """Go back a screen"""

        self.dismiss()

    def action_save(self) -> None:
        """Save the current state to the database"""

        self.app_state.repos.account_repo.save_accounts(self.app_state.state.accounts)
        self.app_state.repos.account_repo.save_history(self.app_state.state.payments)
        self.app_state.repos.account_repo.save_history(self.app_state.state.charges)
        self.app_state.repos.ignore_repo.save_all_ignore(
            self.app_state.state.words_to_ignore
        )

        self.app_state.state.clear_payments()
        self.app_state.state.clear_charges()

        self.notify("Saved To Database", timeout=5)

    def action_load(self) -> None:
        """Load from the database"""

        self.app_state.load_from_db()

        self.notify("Loaded From Database", timeout=5)
