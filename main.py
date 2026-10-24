from application import Application, AppRepositories
from cli.menu import show_menu
from services.database import (
    AccountRepository,
    IgnoreRepository,
    connect,
    disconnect,
    initialise_database,
)

if __name__ == "__main__":
    connection = connect()
    initialise_database(connection)
    print("\nDATABASE CONNECTION ESTABLISHED")
    app = Application(
        AppRepositories(AccountRepository(connection), IgnoreRepository(connection))
    )
    try:
        while True:
            show_menu(app)
    finally:
        disconnect(connection)
        print("\nDISCONNECTED FROM DATABASE")
