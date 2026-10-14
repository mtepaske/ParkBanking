import datetime as dt
import shutil
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta

import balance
from files import (
    export_balances,
    exportAccounts,
    exportPayments,
    exportWordsToIgnore,
    import_balances,
    importAccounts,
    importPayments,
    importWordsToIgnore,
)
from match import Matcher

if __name__ == "__main__":

    accounts = importAccounts("Accounts.csv")
    transactions = importPayments("Transactions.csv")
    ignore = importWordsToIgnore("WordsToIgnore.csv")
    balances = import_balances("Balances.csv")

    if len(balances) != len(accounts):
        raise ValueError("Accounts and Balances do not match")

    for index in range(len(accounts)):
        account = accounts[index]
        balance = balances[index]
        print(account)
        balance.info()
        if balance.site != account.site:
            raise ValueError("Account and Balance site numbers do not match")
        account.add_balance(balance)

    matcher = Matcher(accounts, ignore)

    for transaction in transactions:
        possibilities = matcher.keywordMatch(transaction)
        matcher.match(transaction, possibilities)

    matcher.unknownWords()

    last_month = (
        dt.datetime.now(ZoneInfo("Australia/Melbourne")) - relativedelta(months=1)
    ).strftime("%B")
    this_year = dt.datetime.now(ZoneInfo("Australia/Melbourne")).strftime("%Y")
    shutil.copy2("Transactions.csv", f"{last_month}{this_year}Raw.csv")

    exportAccounts(accounts)
    exportPayments(transactions, f"{last_month} {this_year}.csv")
    exportWordsToIgnore(ignore)
    export_balances(balances)
