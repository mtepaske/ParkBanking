from collections.abc import Iterable
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import (
    Horizontal,
    HorizontalGroup,
    VerticalGroup,
)
from textual.screen import Screen
from textual.widgets import (
    Collapsible,
    DirectoryTree,
    Footer,
    Header,
    Input,
    MaskedInput,
    Select,
    Static,
    Switch,
)

from application import Application
from services.settings import APP_DIRECTORY, load_settings, save_settings


class SettingsMenu(Screen):

    CSS_PATH = "settings_menu.tcss"

    BINDINGS = (
        Binding("q", "back_screen", "Back"),
        Binding("ctrl+w", "save", "Save Settings"),
    )

    def __init__(self, app: Application) -> None:
        super().__init__()
        self.app_state = app
        self.settings = load_settings()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        with Horizontal():

            with VerticalGroup():
                yield Static("BUSINESS SETTINGS", classes="section-title")

                with HorizontalGroup(classes="input-row"):
                    yield Static("Business Name: ", classes="input-label")
                    yield Input(
                        value=self.settings["business_name"], id="business-name"
                    )

            with VerticalGroup():
                yield Static("DATA SETTINGS", classes="section-title")

                with Collapsible(
                    title=f'Imports Folder: {self.settings["imports_folder"]}',
                    collapsed=True,
                    classes="tree-row",
                    id="import-folder",
                ):
                    yield FolderTree(
                        str(APP_DIRECTORY), classes="tree", id="import-tree"
                    )

                with Collapsible(
                    title=f"Export Folder: {self.settings['exports_folder']}",
                    collapsed=True,
                    classes="tree-row",
                    id="export-folder",
                ):
                    yield FolderTree(
                        str(APP_DIRECTORY), classes="tree", id="export-tree"
                    )

                with Collapsible(
                    title=f"Database Location: {self.settings['db_path']}",
                    collapsed=True,
                    classes="tree-row",
                    id="database-folder",
                ):
                    yield DatabaseTree(
                        str(APP_DIRECTORY), classes="tree", id="database-tree"
                    )

                with HorizontalGroup(classes="switch-row"):
                    yield Static(
                        "Auto Load From Database On Start: ", classes="switch-label"
                    )
                    yield Switch(
                        value=self.settings["auto_load_from_db"] == "True",
                        animate=True,
                        id="load",
                    )

                with HorizontalGroup(classes="switch-row"):
                    yield Static(
                        "Auto Save To Database On Close: ", classes="switch-label"
                    )
                    yield Switch(
                        value=self.settings["auto_save_to_db"] == "True",
                        animate=True,
                        id="save",
                    )

                with HorizontalGroup(classes="switch-row"):
                    yield Static(
                        "Add To Loaded Accounts On Import: ", classes="switch-label"
                    )
                    yield Switch(
                        value=self.settings["append_accounts_on_import"] == "True",
                        animate=True,
                        id="append-accounts",
                    )

                with HorizontalGroup(classes="switch-row"):
                    yield Static(
                        "Add To Loaded Transactions On Import: ", classes="switch-label"
                    )
                    yield Switch(
                        value=self.settings["append_transactions_on_import"] == "True",
                        animate=True,
                        id="append-transactions",
                    )

            with VerticalGroup():
                yield Static("FEE SETTINGS", classes="section-title")

                with HorizontalGroup(classes="input-row"):
                    yield Static("Base Rate: ", classes="input-label")
                    yield MaskedInput(
                        "$9999;0",
                        value=f'${self.settings["annual_fees_base_rate"]}',
                        id="base",
                    )

                with HorizontalGroup(classes="input-row"):
                    yield Static("AC Charge: ", classes="input-label")
                    yield MaskedInput(
                        "$999;0",
                        value=f'${self.settings["annual_fees_ac_rate"]}',
                        id="ac",
                    )

                with HorizontalGroup(classes="input-row"):
                    yield Static("Sewer Charge: ", classes="input-label")
                    yield MaskedInput(
                        "$999;0",
                        value=f'${self.settings["annual_fees_sewer_rate"]}',
                        id="sewer",
                    )

                with HorizontalGroup(classes="input-row"):
                    yield Static(
                        "Extra Nominated Visitors Charge: ", classes="input-label"
                    )
                    yield MaskedInput(
                        "$99;0",
                        value=f'${self.settings["annual_fees_extra_guests_rate"]}',
                        id="extra-guests",
                    )

                with HorizontalGroup(classes="input-row"):
                    yield Static("On-Time Payment Discount: ", classes="input-label")
                    yield MaskedInput(
                        "$999;0",
                        value=f'${self.settings["annual_fees_discount"]}',
                        id="discount",
                    )

                with HorizontalGroup(classes="select-row"):
                    yield Static("Annual Period", classes="select-label")
                    yield Select(
                        [("Financial Year", "FY"), ("Calendar Year", "CY")],
                        value=self.settings["annual_period"],
                        allow_blank=False,
                        id="period",
                    )

    def action_back_screen(self):
        self.dismiss()

    def action_save(self) -> None:

        self.settings["business_name"] = str(
            self.query_one("#business-name", Input).value
        )

        self.settings["auto_load_from_db"] = str(self.query_one("#load", Switch).value)
        self.settings["auto_save_to_db"] = str(self.query_one("#save", Switch).value)
        self.settings["append_accounts_on_import"] = str(
            self.query_one("#append-accounts", Switch).value
        )
        self.settings["append_transactions_on_import"] = str(
            self.query_one("#append-transactions", Switch).value
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
