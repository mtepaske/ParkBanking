# ParkBanking

A python app designed to automatically clean and match payments made to a site
holders account and track the balance. This app is designed for use in a caravan
park where site holders are paying each month (or week, or quarter) and payment
deatils are not standardised. Although it is designed for use in a caravan park,
can probably be modified for use in any business where payments need to be
tracked.

## To Do

- [ ] Add ability to add accounts from app
- [ ] Add ability to select transaction file import
- [ ] Add date object rather then string for date sorting
- [ ] Add GUI
- [ ] Add handling of Cash deposits
- [ ] Add ability to export credit on balances as negative value on remianing
      fees
- [ ] Add support for new financial year
    - [ ] Adding new fees
    - [ ] Tranfer remaining fees to outstanding fees
- [x] Refactor main.py to prompt user for steps
    - [ ] Add ability to preview files
    - [x] Add ability to review matches before balance updates
- [ ] Add Database storage through SQlite3
    - [ ] Add ability to read from database and import from csv
    - [ ] Add ability to export active accounts and balances to csv

## Usage

### Uploading Files

There must be three csv files on your system

- Accounts.csv
- Transactions.csv
- WordsToIgnore.csv
- Balances.csv

#### Accounts

This must contain the site number, the site holder name, and at least one alias,
it doesn't matter if there is only one the first time you import the file it
will autonmatically add some basic ones.

#### Transactions

Currently this project only supports importing transaction files from NAB.

#### WordsToIgnore

Just a single collumn with words that the program shouldn't try to match to an
account, this could be words like the name of your business, common words like
"Site" or "Fees", or connecting words like "I" or "The".

#### Balances

This must contain the site number (they must match the accounts site numbers),
the total annual fees for the financial year, the remianing fees for the
financial year, the outstanding fees from previous fincail years, and the
proposed pay period. If the remaining balance or outstanding fees are empty it
will autonmatically make them equal 0.

### Cleaning Data

It will clean the transaction data autonmatically. By first sorting through
irrelavent collumns (account number, category, ect) and then removing any
withdraws from the data, as we are only worried about payments into the account.
It will then go through each transactions details and remove words that are in
the WordsToIgnore.csv file, ensuring that only relavent information is present.

### Matching Data

This works by a keyword match. It will attempt to match each word to an alias in
an account, occationally it might find multiple options. If it doesn't find a
match it will save the word to ask you what to do with it later. If it finds no
matches for a transaction, it will prompt the user to manually match the
transaction

### Updating Balance Information

This iterates through the matched transactions and adds the payment information
to the matched account balances. First removing the ammount from any outstanding
fees, then current fees, and finally adds to credit

### Unknown Word Handling

At the end of the program, it will show you a list of words that it didnt find a
match for and ask for an input. You can either add it to the list of ignored
words, or add it as an alias for an account

### Exporting Files

When everything is complete, it will export and update the Accounts.csv,
Balance.csv and the WordsToIgnore.csv, and then it will export a new file that
is the cleaned and matched payment information for the account. This file will
be called "{this_month} {this_year}.csv"
