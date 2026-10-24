import json

from application import APP_DIRECTORY

SETTINGS_PATH = APP_DIRECTORY / ".parkbanking" / "settings.json"

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
    "annual_period": "FY",
    "auto_load_from_db": "False",
    "auto_save_to_db": "False",
    "db_path": ".parkbanking",
}


def load_settings() -> dict:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not SETTINGS_PATH.exists():
        return DEFAULTS.copy()
    with SETTINGS_PATH.open("r", encoding="utf-8-sig") as settings:
        return json.load(settings)


def save_settings(settings: dict) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SETTINGS_PATH.open("w", encoding="utf-8-sig") as settings_file:
        json.dump(settings, settings_file, indent=4)


def get_setting(key: str) -> str:
    return load_settings()[key]


def update_setting(key: str, value: str) -> None:
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
