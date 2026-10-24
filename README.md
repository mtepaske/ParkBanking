# ParkBanking

I recently took over management of a caravan park in southern Victoria. When I
took over all the banking was hand sorted and hand written to index cards. While
this only had to be done once a month, it was time consuming and I figured I
could easily autonmate it and track it using a program. I've developed this app
to do just that.

Payments come in to the account with different descriptions, so the program
works by macthing keywords in the description.

I've designed this for my own personal use, and as my first useful application.
But I imagine it can easily be adapted for any other small businmess or service
where regular payments are made into an account that you might have to match to
an account and track over time.

This is written by my self in python, and is still a work in progress. I intend
to move most of my computer workflow and tracking to this program, inlcuding
tracking payment history and the autonmatic creation of account statements,
autonmattically calculating and applying new fees in the new year, and adding a
settings menu to make it more customisable.

## To Do

- [ ] Add requirements.txt
- [ ] Should check for test_* files to import if none are found
    - Check with user before importing
- [ ] Add ability to load from database and load from CSV
    - Should be able to load from database then load from csv or vice versa
    - Should be given option to replace or add to list
- [ ] Finish database functionality
    - Add deleting from database
    - Add getting all accounts from database
        - Add viewing just inactive accounts from database
- [ ] Add payment history
    - Add history table to database
    - Converts proccessed payments to a new class payments
        - Date (datetime)
        - Amount (Decimal)
        - Type (Card/Cash/Deposit)
    - Adds Payments to database when proccessed
    - Load Payments from database and display as spreadsheet
    - Export Payment history as pdf and statement of account
    - Use ReportLab module
- [ ] Add settings menu
    - Use QSettings module
    - Set business name
    - Set default export/import folder
    - Set annual fees and site fees
    - Auto load from database vs manual load
    - Reset/Backup database
    - Autosave/Manual save
    - Does importing add to or replace the list
    - Whats the yearly basis (FY or calender year)
- [ ] Set up Site class
    - Stores information for constructing annual fees
- [ ] Set up new financial year support
    - Works will Site class to construct new fees and add them to payment
      history

- [ ] Add GUI using pyside6

## Usage

Currently this is a CLI tool. You can launch the app by typing python3 main.py
into your command line.

Once launched, you will see a main menu screen. You can begin by loading from
the database, or by loading from CSV files

### Loading From CSV's

If you choose to load from CSV files, then you need 2 files. One for the Account
names, sites and aliases. And one for the balance information (examples are
included under test_files/). You can also choose to load a CSV containing words
the matcher should ignore. If there is previously matched payments you would
like to import for payment processing, you can do that by selecting the import
previously matched option and typing in the file path

### Loading Bank Information

Currently this app only supports bank information downloaded from NAB, but could
be modified to load other CSVs downloaded from otehr banks. Once you have the
CSV in yout project root (By default called "Transactions.csv", but could be
modified in the code) and you have eitehr loaded some account information from
the database or from CSV files, you can select import payment information.

### Matching Keywords

The matcher works by using the account information given to generate a list of
aliases, or words that might be associated with an account. It filters through
each transaction, first removing withdrawls and CASH deposits, and then
filtering descriptions for any words in the ignore list.

It then generates a list of possible matches by matching the account aliases to
the transaction details. If only one match is found it will prompt the user to
pick one, or if none are found it shows a list of all accounts to choose from.
With the option to leave the account unmatched.

### Unknown Words

Once everything is matched, users have the option to handle any unknown words
that were included in the descriptions, and add them either as an alias for an
account, or to the list of words to ignore. Meaning the more you run the
program, the better at matching it becomes.

### Payment Processing

When processing payments is selected, any matched transactions will be applied
as payments to the matched accounts. First by removing any outstanding fees and
then the remianing fees for the year.

### Accounts Screen

The accounts menu shows a list of all accounts and allows you to edit them, add
more, or apply a manual payment. The accounts are coloured depending on if they
are judged to be 'on-track', which uses the indicated payment frequency
(monthly, quarterly, or annually) and the due dates (15th of each month, first
15th of each quarter, or the 1st of January respectivly) to calculate how much
should have been paid, and compare that to how much has been paid. Accounts with
outstanding amounts are autonmattically coloured red for 'behind'. You are also
able to activate or deactivate accounts to keep records on old accounts

### Exports Screen

You are able to export any information in the app to a CSV file, including a
list of matched payments and they're respective amounts. You can do this by
entering the exports menu and selecting what you would like to export

### Saving Updates

You must manaully save at the end of proccessing or matching. You can do this by
selecting the save to database option.

## Issue and Bug Reporting

If you have any issues or encounter any bugs, please open an issue on GitHub.
Alternativly you can find me at u/Mooball123 on reddit.

If anyone has any questions about the finctionality of the app, feedback for
imporvements, or want help modifying the app for their own personal or business
use, please feel free to get in touch!
