from textual.app import ComposeResult
from textual.containers import (
    HorizontalGroup,
    VerticalGroup,
)
from textual.widgets import (
    Static,
)

from application import Application


class StatusBox(VerticalGroup):
    """
    Display the application state

    Attributes:
        border_title: (str) The title of the widget
        app_state: (Application) The application state
    """

    def __init__(self, app_state: Application, **kwargs) -> None:
        """
        Initialise the widget

        Args:
            app_state: The application state
            **kwargs: Other key word arguments
        """

        super().__init__(**kwargs, classes="status-box")
        self.border_title = "Loaded Data"
        self.app_state = app_state

    def compose(self) -> ComposeResult:
        """Construct the widgets on the screen"""

        state = self.app_state.state

        with HorizontalGroup(classes="status-row"):
            yield Static("Unmatched Payments: ", classes="status")
            yield Static(
                str(len(state.transactions)),
                classes="number",
                id="status-transactions",
            )

        with HorizontalGroup(classes="status-row"):
            yield Static("Unapplied Payments/Charges: ", classes="status")
            yield Static(
                str(len(state.unapplied)), classes="number", id="status-unapplied"
            )

        with HorizontalGroup(classes="status-row"):
            yield Static("Unsaved Payments: ", classes="status")
            yield Static(
                str(len(state.payments)), classes="number", id="status-payments"
            )

        with HorizontalGroup(classes="status-row"):
            yield Static("Unsaved Charges: ", classes="status")
            yield Static(str(len(state.charges)), classes="number", id="status-charges")

        with HorizontalGroup(classes="status-row"):
            yield Static("Sites: ", classes="status")
            yield Static(str(len(state.sites)), classes="number", id="status-sites")

        with HorizontalGroup(classes="status-row"):
            yield Static("Accounts: ", classes="status")
            yield Static(
                str(len(state.accounts)), classes="number", id="status-accounts"
            )

        with HorizontalGroup(classes="status-row"):
            yield Static("Words: ", classes="status")
            yield Static(
                str(len(state.words_to_ignore)),
                classes="number",
                id="status-ignore",
            )

    def on_mount(self) -> None:
        """On starting of the widget"""

        self.app_state.state.subscribe(self.refresh_status)
        self.refresh_status()

    def on_unmount(self) -> None:
        """On closing on the widget"""

        self.app_state.state.unsubscribe(self.refresh_status)

    def refresh_status(self) -> None:
        """Refresh display"""

        state = self.app_state.state

        self.query_one("#status-transactions", Static).update(
            str(len(state.transactions))
        )
        self.query_one("#status-unapplied", Static).update(str(len(state.unapplied)))
        self.query_one("#status-payments", Static).update(str(len(state.payments)))
        self.query_one("#status-charges", Static).update(str(len(state.charges)))
        self.query_one("#status-sites", Static).update(str(len(state.sites)))
        self.query_one("#status-accounts", Static).update(str(len(state.accounts)))
        self.query_one("#status-ignore", Static).update(str(len(state.words_to_ignore)))
