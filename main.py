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
    transactions = importPayments('transactions.csv')
    ignore = importWordsToIgnore('WordsToIgnore.csv')

    payments = []
    exportAccounts(accounts)
    exportPayments(payments)
    exportWordsToIgnore(ignore)
