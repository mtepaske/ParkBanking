from textual.app import ComposeResult
from textual.containers import (
    Horizontal,
    Vertical,
    VerticalGroup,
    VerticalScroll,
)
from textual.widgets import Button, Collapsible, Input, Static

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
                    title="Export Accounts & Balances",
                    collapsed=True,
                    classes="tree-row",
                    id="accounts",
                ):
                    yield FolderTree(
                        str(self.export_folder), classes="tree", id="accounts-tree"
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
