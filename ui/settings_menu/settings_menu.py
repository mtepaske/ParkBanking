from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import (
    Horizontal,
    Vertical,
)
from textual.widgets import (
    Collapsible,
    DirectoryTree,
    Input,
    Label,
    MaskedInput,
    Select,
    Static,
    Switch,
)

from services.settings import APP_DIRECTORY, load_settings, save_settings
from ui.custom_widgets import DatabaseTree, FolderTree, Menu


class SettingsMenu(Menu):
    """
    A settings menu

    Attributes:
        BINDINGS: (tuple[Binding]) The keybindings for the menu
        CSS_PATH: (str) The name of the file containing styling information for the app
        settings: (dict) The dictionary containing current settings
    """

    BINDINGS = (
        Binding("q", "back", "Back"),
        Binding("ctrl+s", "save_settings", "Save Settings"),
    )

    CSS_PATH = "settings_menu.tcss"

    def __init__(self, **kwargs) -> None:
        """Initialise the menu"""

        super().__init__(**kwargs)
        self.settings = load_settings()

    def compose(self) -> ComposeResult:
        """Construct the widgets on the screen"""

        yield from super().compose()

        # Business settings section
        with Vertical(classes="section"):
            yield Static("BUSINESS SETTINGS", classes="section-title")

            with Horizontal(classes="row"):
                yield Label("Business Name: ")
                yield Input(value=self.settings["business_name"], id="business-name")

        # Data settings section
        with Vertical(classes="section"):
            yield Static("DATA SETTINGS", classes="section-title")

            with Collapsible(
                title=f'Imports Folder: {self.settings["imports_folder"]}',
                collapsed=True,
                classes="tree-row",
                id="import-folder",
            ):

                yield FolderTree(str(APP_DIRECTORY), classes="tree", id="import-tree")

            with Collapsible(
                title=f"Export Folder: {self.settings['exports_folder']}",
                collapsed=True,
                classes="tree-row",
                id="export-folder",
            ):
                yield FolderTree(str(APP_DIRECTORY), classes="tree", id="export-tree")

            with Collapsible(
                title=f"Database Location: {self.settings['db_path']}",
                collapsed=True,
                classes="tree-row",
                id="database-folder",
            ):
                yield DatabaseTree(
                    str(APP_DIRECTORY), classes="tree", id="database-tree"
                )

            with Horizontal(classes="row"):
                yield Label(
                    "Add To Loaded Accounts On Import: ", classes="select-label"
                )
                yield Select(
                    [("Never", "Never"), ("Ask", "Ask"), ("Always", "Always")],
                    value=self.settings["append_accounts_on_import"],
                    allow_blank=False,
                    id="append-accounts",
                )

            with Horizontal(classes="row"):
                yield Label(
                    "Add To Loaded Transactions On Import: ", classes="select-label"
                )
                yield Select(
                    [("Never", "Never"), ("Ask", "Ask"), ("Always", "Always")],
                    value=self.settings["append_transactions_on_import"],
                    allow_blank=False,
                    id="append-transactions",
                )

            with Horizontal(classes="row"):
                yield Label("Auto Load From Database On Start: ")
                yield Switch(
                    value=self.settings["auto_load_from_db"] == "True",
                    animate=True,
                    id="load",
                )

            with Horizontal(classes="row"):
                yield Label("Auto Save To Database On Close: ")
                yield Switch(
                    value=self.settings["auto_save_to_db"] == "True",
                    animate=True,
                    id="save",
                )

            # Add buttons for backing up database, clearing loaded data, and clearing database

        # Fee settings section
        with Vertical(classes="section"):
            yield Static("FEE SETTINGS", classes="section-title")

            with Horizontal(classes="row"):
                yield Label("Base Rate: ")
                yield MaskedInput(
                    "$9999;0",
                    value=f'${self.settings["annual_fees_base_rate"]}',
                    id="base",
                )

            with Horizontal(classes="row"):
                yield Label("AC Charge: ")
                yield MaskedInput(
                    "$999;0",
                    value=f'${self.settings["annual_fees_ac_rate"]}',
                    id="ac",
                )

            with Horizontal(classes="row"):
                yield Label("Sewer Charge: ")
                yield MaskedInput(
                    "$999;0",
                    value=f'${self.settings["annual_fees_sewer_rate"]}',
                    id="sewer",
                )

            with Horizontal(classes="row"):
                yield Label("Extra Nominated Visitors Charge: ")
                yield MaskedInput(
                    "$99;0",
                    value=f'${self.settings["annual_fees_extra_guests_rate"]}',
                    id="extra-guests",
                )

            with Horizontal(classes="row"):
                yield Label("On-Time Payment Discount: ")
                yield MaskedInput(
                    "$999;0",
                    value=f'${self.settings["annual_fees_discount"]}',
                    id="discount",
                )

            with Horizontal(classes="row"):
                yield Label("Annual Period: ", classes="select-label")
                yield Select(
                    [("Financial Year", "FY"), ("Calendar Year", "CY")],
                    value=self.settings["annual_period"],
                    allow_blank=False,
                    id="period",
                )

    def action_save_settings(self) -> None:
        """Save current settings"""

        self.settings["business_name"] = str(
            self.query_one("#business-name", Input).value
        )

        self.settings["auto_load_from_db"] = str(self.query_one("#load", Switch).value)
        self.settings["auto_save_to_db"] = str(self.query_one("#save", Switch).value)
        self.settings["append_accounts_on_import"] = str(
            self.query_one("#append-accounts", Select).value
        )
        self.settings["append_transactions_on_import"] = str(
            self.query_one("#append-transactions", Select).value
        )

        self.settings["annual_fees_base_rate"] = str(
            self.query_one("#base", MaskedInput).value.removeprefix("$")
        )
        self.settings["annual_fees_ac_rate"] = str(
            self.query_one("#ac", MaskedInput).value.removeprefix("$")
        )
        self.settings["annual_fees_sewer_rate"] = str(
            self.query_one("#sewer", MaskedInput).value.removeprefix("$")
        )
        self.settings["annual_fees_extra_guests_rate"] = str(
            self.query_one("#extra-guests", MaskedInput).value.removeprefix("$")
        )
        self.settings["annual_fees_discount"] = str(
            self.query_one("#discount", MaskedInput).value.removeprefix("$")
        )
        self.settings["annual_period"] = str(self.query_one("#period", Select).value)

        save_settings(self.settings)

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        """
        Runs when a folder is selected

        Args:
            event: The event of the folder selection
        """

        match event.control.id:

            case "import-tree":

                self.settings["imports_folder"] = str(
                    event.path.relative_to(APP_DIRECTORY)
                )
                self.query_one("#import-folder", Collapsible).title = (
                    f'Imports Folder: {self.settings["imports_folder"]}'
                )
                self.query_one("#import-folder", Collapsible).collapsed = True

            case "export-tree":

                self.settings["exports_folder"] = str(
                    event.path.relative_to(APP_DIRECTORY)
                )
                self.query_one("#export-folder", Collapsible).title = (
                    f'Exports Folder: {self.settings["exports_folder"]}'
                )
                self.query_one("#export-folder", Collapsible).collapsed = True

            case "database-tree":

                self.settings["db_path"] = str(event.path.relative_to(APP_DIRECTORY))
                self.query_one("#database-folder", Collapsible).title = (
                    f'Database Folder: {self.settings["db_path"]}'
                )
                self.query_one("#database-folder", Collapsible).collapsed = True
