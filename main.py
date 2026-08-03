from files import (
    exportAccounts,
    exportPayments,
    exportWordsToIgnore,
    importAccounts,
    importPayments,
    importWordsToIgnore,
)
from match import Matcher

# Import Data [x]
# Clearn Data [x]
# Import Accounts [x]
# Match payments to accounts Autonmatically
# Match paymets to accounts manually
# Review
# Update Account info and balances
# Add any new alias's to accounts
# Export csv of matched payments

if __name__ == "__main__":

    accounts = importAccounts("Accounts.csv")
    transactions = importPayments("Transactions.csv")
    ignore = importWordsToIgnore("WordsToIgnore.csv")

    matcher = Matcher(accounts, ignore)

    for transaction in transactions:
        possibilities = matcher.keywordMatch(transaction)
        matcher.match(transaction, possibilities)

    matcher.unknownWords()

    exportAccounts(accounts)
    exportPayments(transactions, "Test.csv")
    exportWordsToIgnore(ignore)
