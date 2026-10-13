import datetime as dt
from decimal import ROUND_HALF_UP, Decimal


class Balance:

    def __init__(
        self, site: int, annual: float, remaining: float, outstanding: float
    ) -> None:
        self.site = site
        self.annual = Decimal(str(annual))
        self.remianing = Decimal(str(remaining))
        self.outstanding = Decimal(str(outstanding))

    def info(self) -> None:
        print(f"Balance info for Site {self.site}")
        print(
            f"  Total Annual Fees: {self.annual} | Monthly Payment: {self.calcMonthlyPayments(self.annual, 12)}"
        )
        print(f"  Annual Fees Remaining: {self.remianing}")
        print(f"  Outstanding From Previous Years: {self.outstanding}")

    def getTotalBalance(self) -> Decimal:
        return self.outstanding + self.remianing

    def getSite(self) -> int:
        return self.site

    def getAnnual(self) -> Decimal:
        return self.annual

    def getRemaining(self) -> Decimal:
        return self.remianing

    def getOutstanding(self) -> Decimal:
        return self.outstanding

    def calcMonthlyPayments(self, amount: Decimal, monthsToPay: int) -> Decimal:
        return (amount / monthsToPay).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calcMonthsLeft(self, date: dt.date) -> int:
        month = date.month
        if month >= 7:
            return 12 - month + 6
        else:
            return 6 - month


if __name__ == "__main__":

    test = Balance(1, 7550, 7550, 0)
    test.info()
