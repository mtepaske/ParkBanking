from application import Application, AppRepositories
from cli.menu import show_menu, start_program
from services.database import (
    AccountRepository,
    IgnoreRepository,
    connect,
    disconnect,
    initialise_database,
)

if __name__ == "__main__":
    # Connect to the database and initialise it
    connection = connect()
    initialise_database(connection)
    print("\nDATABASE CONNECTION ESTABLISHED")

    # Initialise the application and state
    app = Application(
        AppRepositories(AccountRepository(connection), IgnoreRepository(connection))
    )

    # Start the program
    start_program(app)

    try:
        # Shows the main menu
        while True:
            show_menu(app)

    finally:
        # Disconnect from the database
        disconnect(connection)
        print("\nDISCONNECTED FROM DATABASE")
