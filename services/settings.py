import json
from pathlib import Path

# Finds the folder containing source code
APP_DIRECTORY = Path(__file__).resolve().parent.parent

# Sets the path for the settings.json
SETTINGS_PATH = APP_DIRECTORY / ".parkbanking" / "settings.json"

# Default settings
DEFAULTS = {
    "business_name": "Caravan Park",
    "imports_folder": "files",
    "exports_folder": "files",
    "append_accounts_on_import": "Ask",
    "append_transactions_on_import": "Ask",
    "annual_fees_base_rate": "7550",
    "annual_fees_ac_rate": "150",
    "annual_fees_sewer_rate": "300",
    "annual_fees_extra_guests_rate": "80",
    "annual_fees_discount": "150",
    "annual_period": "FY",
    "auto_load_from_db": "False",
    "auto_save_to_db": "False",
    "db_path": ".parkbanking",
}


def load_settings() -> dict:
    """
    Loads current settings from a json file. Creates a file with default settings if none found

    Returns:
        A dictionary containing the setting information
    """

    # Sets the path for the file
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Creates a settings file with default settings if none exist
    if not SETTINGS_PATH.exists():
        return DEFAULTS.copy()

    # Loads the file into a dictionary
    with SETTINGS_PATH.open("r", encoding="utf-8-sig") as settings:
        return json.load(settings)


def save_settings(settings: dict) -> None:
    """
    Saves updated settings into a json file

    Args:
        settings: A dictionary of settings to change
    """

    # Sets the path for the file
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Write to the file
    with SETTINGS_PATH.open("w", encoding="utf-8-sig") as settings_file:
        json.dump(settings, settings_file, indent=4)


def get_setting(key: str) -> str:
    """
    Gets a specific setting

    Args:
        key: The dictionary key for the specific setting

    Returns:
        A string containing the current setting
    """

    return load_settings()[key]


def update_setting(key: str, value: str) -> None:
    """
    Updates a setting

    Args:
        key: The key of the setting to update
        value: The value to change it too
    """

    settings = load_settings()
    settings[key] = value
    save_settings(settings)
