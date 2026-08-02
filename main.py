from match import Matcher
from files import importAccounts, importPayments, importWordsToIgnore
from files import exportAccounts, exportPayments, exportWordsToIgnore

# Import Data [x]
# Clearn Data [x]
# Import Accounts [x]
# Match payments to accounts Autonmatically
# Match paymets to accounts manually
# Review
# Update Account info and balances
# Add any new alias's to accounts
# Export csv of matched payments

if __name__ == '__main__':

    accounts = importAccounts('Accounts.csv')
    transactions = importPayments('Transactions.csv')
    ignore = importWordsToIgnore('WordsToIgnore.csv')

    matcher = Matcher(accounts, ignore)
    print('Matcher Initialised')

    for transaction in transactions:
        print('Transaction Accessed')
        possibilities = matcher.keywordMatch(transaction)
        matcher.match(transaction, possibilities)

    matcher.unknownWords()

    payments = []
    exportAccounts(accounts)
    exportPayments(payments)
    exportWordsToIgnore(ignore)
