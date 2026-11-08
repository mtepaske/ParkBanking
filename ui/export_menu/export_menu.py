from textual import on
from textual.app import ComposeResult
from textual.containers import (
    Horizontal,
    Vertical,
    VerticalGroup,
    VerticalScroll,
)
from textual.widgets import Button, Collapsible, DataTable, DirectoryTree, Input, Static

from services.settings import APP_DIRECTORY, get_setting
from ui.custom_widgets import FolderTree, Menu, StatusBox


class ExportMenu(Menu):
    """
    A menu to export current state as files

    Attributes:
        CSS_PATH: (str) The name of the file containing styling information for the app
        export_folder: (Path) The path of the folder to export too
    """

    CSS_PATH = "export_menu.tcss"

    def __init__(self, **kwargs):
        """Initialise the menu"""
        super().__init__(**kwargs)
        self.export_folder = APP_DIRECTORY / get_setting("exports_folder")
        self.loaded_file = None
        self.loaded_file_type = None

    def compose(self) -> ComposeResult:
        """Construct the widgets on the screen"""

        yield from super().compose()

        # File selection section
        with VerticalScroll(classes="section"):
            yield Static("Export Files", classes="section-title")

            with VerticalGroup(id="file-select"):

                with Collapsible(
                    title="Export Matched Transactions",
                    collapsed=True,
                    classes="tree-row",
                    id="statement",
                ):
                    yield FolderTree(
                        str(self.export_folder), classes="tree", id="statement-tree"
                    )

                with Collapsible(
                    title="Export Accounts",
                    collapsed=True,
                    classes="tree-row",
                    id="accounts",
                ):
                    yield FolderTree(
                        str(self.export_folder), classes="tree", id="accounts-tree"
                    )

                with Collapsible(
                    title="Export Balances",
                    collapsed=True,
                    classes="tree-row",
                    id="balances",
                ):
                    yield FolderTree(
                        str(self.export_folder), classes="tree", id="balances-tree"
                    )

                with Collapsible(
                    title="Export Site Information",
                    collapsed=True,
                    classes="tree-row",
                    id="site",
                ):
                    yield FolderTree(
                        str(self.export_folder), classes="tree", id="site-tree"
                    )

                with Collapsible(
                    title="Export Words To Ignore",
                    collapsed=True,
                    classes="tree-row",
                    id="ignore",
                ):
                    yield FolderTree(
                        str(self.export_folder), classes="tree", id="ignore-tree"
                    )

            with Vertical(id="confirm-stack"):

                with Horizontal(id="name-row"):
                    yield Input(placeholder="File Name", disabled=True, id="file-name")

                with Horizontal(id="confirm-row"):
                    yield Button.success(
                        "Export Selected File", disabled=True, id="confirm"
                    )

            yield StatusBox(app_state=self.app_state)

        # File preview
        with Vertical(classes="section"):

            yield Static("File Preview", classes="section-title")
            yield DataTable(zebra_stripes=True, id="file-preview")

    @on(Input.Changed)
    def on_input_changed(self):

        self.query_one("#confirm", Button).disabled = False

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed):

        if event.button.id == "confirm":

            match self.loaded_file_type:

                case "statement":
                    pass

                case "accounts":
                    pass

                case "balances":
                    pass

                case "site":
                    pass

                case "ignore":
                    pass

    @on(DirectoryTree.DirectorySelected)
    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ):

        match event.control.id:

            case "statement-tree":
                pass

            case "accounts-tree":
                pass

            case "balances-tree":
                pass

            case "site-tree":
                pass

            case "ignore-tree":
                pass

    def preview_statement(self):
        pass

    def preview_accounts(self):
        pass

    def preview_balances(self):
        pass

    def preview_sites(self):
        pass

    def preview_ignore(self):
        pass

    def export_statement(self, filename: str):
        pass

    def export_accounts(self, filename: str):
        pass

    def export_balances(self, filename: str):
        pass

    def export_sites(self, filename: str):
        pass

    def export_ignore(self, filename: str):
        pass
