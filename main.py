import datetime as dt
import shutil
from zoneinfo import ZoneInfo

from dateutil.relativedelta import relativedelta

from files import (
    exportAccounts,
    exportPayments,
    exportWordsToIgnore,
    importAccounts,
    importPayments,
    importWordsToIgnore,
)
from match import Matcher

if __name__ == "__main__":

    accounts = importAccounts("Accounts.csv")
    transactions = importPayments("Transactions.csv")
    ignore = importWordsToIgnore("WordsToIgnore.csv")

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
