from collections.abc import Iterable
from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import HorizontalGroup, Vertical, VerticalGroup, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, DirectoryTree, Label, Static

from application import Application
from models.transactions import Transaction


class FolderTree(DirectoryTree):

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [
            path
            for path in paths
            if path.is_dir()
            and not path.name.startswith(".")
            and not path.name.startswith("_")
        ]


class DatabaseTree(DirectoryTree):

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [
            path for path in paths if path.is_dir() and not path.name.startswith("_")
        ]


class StatusBox(VerticalGroup):

    def __init__(self, app: Application, **kwargs):
        super().__init__(**kwargs)
        self.border_title = "Loaded Data"
        self.app_state = app

    def compose(self) -> ComposeResult:

        state = self.app_state.state

        with HorizontalGroup(classes="status-row"):
            yield Static("Unmatched Payments: ", classes="status")
            yield Static(
                str(len(state.transactions)),
                classes="number",
                id="status-transactions",
            )
        with HorizontalGroup(classes="status-row"):
            yield Static("Matched Payments: ", classes="status")
            yield Static(
                str(len(state.payments)), classes="number", id="status-payments"
            )
        with HorizontalGroup(classes="status-row"):
            yield Static("Un Committed Charges: ", classes="status")
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

    def on_mount(self):
        self.app_state.state.subscribe(self.refresh_status)
        self.refresh_status()

    def on_unmount(self):
        self.app_state.state.unsubscribe(self.refresh_status)

    def refresh_status(self):
        state = self.app_state.state

        self.query_one("#status-transactions", Static).update(
            str(len(state.transactions))
        )
        self.query_one("#status-payments", Static).update(str(len(state.payments)))
        self.query_one("#status-charges", Static).update(str(len(state.charges)))
        self.query_one("#status-sites", Static).update(str(len(state.sites)))
        self.query_one("#status-accounts", Static).update(str(len(state.accounts)))
        self.query_one("#status-ignore", Static).update(str(len(state.words_to_ignore)))


class ConfirmScreen(ModalScreen[bool]):

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog"):
            yield Label(self.message)
            yield Button.success("Yes", id="yes")
            yield Button.error("No", id="no")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)


class ConfirmAppendScreen(ModalScreen[str | None]):

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog"):
            yield Label(self.message)
            yield Button.success("Add To", id="append")
            yield Button.warning("Replace", id="replace")
            yield Button.error("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss(event.button.id)


class ImportBalancesScreen(ModalScreen[Path | None]):

    def __init__(self, import_folder: Path):
        super().__init__()
        self.import_folder = import_folder
        self.filepath = None

    def compose(self) -> ComposeResult:
        with Vertical(classes="dialog"):
            yield Label(
                "Please Selected File Containing Balance Information For Imported Accounts"
            )
            yield DirectoryTree(
                str(self.import_folder), classes="tree", id="balance-tree"
            )
            yield Button.success("Confirm", disabled=True, id="confirm")
            yield Button.error("Cancel", id="cancel")

    @on(DirectoryTree.FileSelected)
    def on_directiory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        self.filepath = event.path
        self.query_one("#confirm", Button).disabled = False

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "confirm":
            self.dismiss(self.filepath)
        else:
            self.dismiss()


class ConfirmGeneratedCharges(ModalScreen[bool | None]):

    def __init__(self, charges: list[Transaction]) -> None:
        super().__init__()
        self.charges = charges

    def compose(self) -> ComposeResult:
        with VerticalScroll(classes="dialog"):
            yield Label("Please Confirm Autonmatically Generated Charges Are Correct")
            yield DataTable(zebra_stripes=True, id="charge-preview")
            yield Button.success("Confirm", id="confirm")
            yield Button.error("Cancel", id="cancel")

    def on_mount(self) -> None:
        charge_preview = self.query_one("#charge-preview", DataTable)

        charge_preview.add_columns("Account", "Date", "Description", "Amount")

        for charge in self.charges:
            charge_preview.add_row(
                charge.account, charge.date, charge.original_details, charge.amount
            )

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "confirm":
            self.dismiss(True)
        else:
            self.dismiss(False)
