from application import Application
from models.balance import money
from services.settings import get_setting, update_setting


def settings_menu(app: Application):
    print("\nSETTINGS MENU")
    settings_actions = {
        "Business Settings": buisness_settings,
        "Data Settings": data_settings,
        "Fee Settings": fee_settings,
    }
    while True:
        available = [(name, _) for name, _ in settings_actions.items()]
        for i, (name, _) in enumerate(available, start=1):
            print(f"[{i}] -> {name}")
        print("[b] -> Back")
        choice = input("Choose an Action: ")
        if choice == "b":
            print("BACK")
            return
        try:
            name, _ = available[int(choice) - 1]
            settings_actions[name]()
        except (ValueError, IndexError):
            print("Invalid Choice. Please Choose From List")


def buisness_settings() -> None:
    business_settings = {
        "Business Name": {
            "value": "business_name",
            "function": change_name,
        }
    }
    settings = [(name, action) for name, action in business_settings.items()]
    while True:
        try:
            for i, (name, action) in enumerate(settings, start=1):
                print(f"[{i}] -> {name}: {get_setting(action['value'])}")
            print("[b] -> Back")
            choice = input("What would you like to change?: ")
            if choice == "b":
                print("BACK")
                return
            name, action = settings[int(choice) - 1]
            action["function"](action["value"])
        except (ValueError, IndexError):
            print("Invalid Choice. Please Choose From List")


def data_settings() -> None:
    data_settings = {
        "Imports Folder": {
            "value": "imports_folder",
            "function": change_folder,
        },
        "Exports Folder": {
            "value": "exports_folder",
            "function": change_folder,
        },
        "Database Location": {"value": "db_path", "function": change_folder},
        "Autoload From Database": {
            "value": "auto_load_from_db",
            "function": change_auto_db,
        },
        "Autosave To Database": {
            "value": "auto_save_to_db",
            "function": change_auto_db,
        },
        "Add To Loaded Accounts On Import": {
            "value": "append_accounts_on_import",
            "function": change_append,
        },
        "Add To Loaded Transactions On Import": {
            "value": "append_transactions_on_import",
            "function": change_append,
        },
    }
    settings = [(name, action) for name, action in data_settings.items()]
    while True:
        try:
            for i, (name, action) in enumerate(settings, start=1):
                print(f"[{i}] -> {name}: {get_setting(action['value'])}")
            print("[b] -> Back")
            choice = input("What would you like to change?: ")
            if choice == "b":
                print("BACK")
                return
            name, action = settings[int(choice) - 1]
            action["function"](action["value"])
        except (ValueError, IndexError):
            print("Invalid Choice. Please Choose From List")


def fee_settings() -> None:
    fee_settings = {
        "Base Rate": {
            "value": "annual_fees_base_rate",
            "function": change_fees,
        },
        "AC Charge": {
            "value": "annual_fees_ac_rate",
            "function": change_fees,
        },
        "Sewer Charge": {
            "value": "annual_fees_sewer_rate",
            "function": change_fees,
        },
        "Extra Nominated Visitors Charge": {
            "value": "annual_fees_extra_guests_rate",
            "function": change_fees,
        },
        "Annual Period": {
            "value": "annual_period",
            "function": change_period,
        },
    }
    settings = [(name, action) for name, action in fee_settings.items()]
    while True:
        try:
            for i, (name, action) in enumerate(settings, start=1):
                print(f"[{i}] -> {name}: {get_setting(action['value'])}")
            print("[b] -> Back")
            choice = input("What would you like to change?: ")
            if choice == "b":
                print("BACK")
                return
            name, action = settings[int(choice) - 1]
            action["function"](action["value"])
        except (ValueError, IndexError):
            print("Invalid Choice. Please Choose From List")


def change_name(key: str) -> None:
    new_name = input("Enter New Name: ")
    update_setting(key, new_name)


def change_folder(key: str) -> None:
    new_folder = input("Enter New Folder: ")
    update_setting(key, new_folder)


def change_append(key: str) -> None:
    while True:
        print("[1] -> Always")
        print("[2] -> Ask")
        print("[3] -> Never")
        choice = input("Enter Index For Option: ")
        if choice == "1":
            update_setting(key, "Always")
            return
        elif choice == "2":
            update_setting(key, "Ask")
            return
        elif choice == "3":
            update_setting(key, "Never")
            return
        else:
            print("Invalid Choice. Please Choose From List")


def change_fees(key: str) -> None:
    while True:
        new_amount = input("Enter New Amount: $")
        try:
            money(new_amount)
            update_setting(key, new_amount)
            return
        except ValueError:
            print("Must Enter Monetary Amount")


def change_period(key: str) -> None:
    while True:
        print("[1] -> Fincial Year: 1st July - 30th June")
        print("[2] -> Calender Year: 1st January - 31st December")
        choice = input("Enter Index For Option: ")
        if choice == "1":
            update_setting(key, "FY")
            return
        elif choice == "2":
            update_setting(key, "Calender")
            return
        else:
            print("Invalid Choice. Please Choose From List")


def change_auto_db(key: str) -> None:
    while True:
        print("[1] -> True")
        print("[2] -> False")
        choice = input("Enter Index For Option: ")
        if choice == "1":
            update_setting(key, "True")
            return
        elif choice == "2":
            update_setting(key, "False")
            return
        else:
            print("Invalid Choice. Please Choose From List")
