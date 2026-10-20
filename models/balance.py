from __future__ import annotations

from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal
from zoneinfo import ZoneInfo


class Balance:

    CENT = Decimal("0.01")

    @staticmethod
    def get_today() -> date:
        return datetime.now(ZoneInfo("Australia/Melbourne")).date()

    @staticmethod
    def money(value: Decimal | float | str) -> Decimal:
        return Decimal(str(value)).quantize(Balance.CENT, rounding=ROUND_HALF_UP)

    def __init__(
        self,
        account_id: int | None,
        site_number: str | int,
        annual: str,
        remaining: str,
        outstanding: str,
        pay_frequency: str,
        id: int | None = None,
    ) -> None:
        self.id = id
        self.account_id = account_id
        # Site number is extended to 2 digits
        self.site_number = str(site_number)
        if len(self.site_number) == 1:
            self.site_number = f"0{self.site_number}"
        self.annual = self.money(annual)
        self.remaining = self.money(remaining)
        self.outstanding = self.money(outstanding)
        self.credit = Decimal("0.00")
        # Checks for valid pay_frequency
        if pay_frequency not in ["a", "q", "m"]:
            pay_frequency = "m"
        self.pay_frequency = pay_frequency

    @classmethod
    def from_csv(cls, row: dict[str, str]) -> Balance:
        site = row["Site"]
        annual = row["Annual Fee"]
        remaining = row["Remaining from this FY"]
        outstanding = row["Outstanding from previous FYs"]
        pay_frequency = row["Pay Frequency"]
        if row["ID"] == "None":
            id = None
        else:
            id = int(row["ID"])
        if row["Account ID"] == "None":
            account_id = None
        else:
            account_id = int(row["Account ID"])
        if remaining == "":
            remaining = annual
        if outstanding == "":
            outstanding = "0.00"
        return cls(
            account_id,
            site,
            annual,
            remaining,
            outstanding,
            pay_frequency,
            id,
        )

    @property
    def balance(self) -> Decimal:
        return self.outstanding + self.remaining

    @property
    def outstanding(self) -> Decimal:
        return self._outstanding

    @outstanding.setter
    def outstanding(self, amount: Decimal) -> None:
        amount = self.money(amount)
        if amount < 0:
            raise ValueError("Outstanding can not be negative")
        else:
            self._outstanding = amount

    @property
    def remaining(self) -> Decimal:
        return self._remaining

    @remaining.setter
    def remaining(self, amount: Decimal) -> None:
        amount = self.money(amount)
        if amount < 0:
            raise ValueError("Remaining can not be negative")
        else:
            self._remaining = amount

    @property
    def end_of_fy(self) -> date:
        today = self.get_today()
        if today.month >= 7:
            return date(today.year + 1, 6, 30)
        else:
            return date(today.year, 6, 30)

    @property
    def start_of_fy(self) -> date:
        today = self.get_today()
        if today.month >= 7:
            return date(today.year, 7, 1)
        else:
            return date(today.year - 1, 7, 1)

    def change_payfrequency(self, new_frequency: Literal["a", "q", "m"]):
        self.pay_frequency = new_frequency

    def calc_payments(self, amount: Decimal, num_of_payments: int = 0) -> Decimal:
        if num_of_payments < 0:
            raise ValueError("Number of payments must be greater then 0")
        elif num_of_payments == 0:
            match self.pay_frequency:
                case "a":
                    num_of_payments = 1
                case "q":
                    num_of_payments = 4
                case "m":
                    num_of_payments = 12
        return self.money(amount / num_of_payments)

    def add_payment(self, amount: Decimal) -> None:
        amount = self.money(amount)
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        if amount < self.outstanding:
            self.outstanding -= amount
        elif amount < self.balance:
            amount -= self.outstanding
            self.outstanding = Decimal("0.00")
            self.remaining -= amount
        else:
            amount -= self.outstanding
            self.outstanding = Decimal("0.00")
            amount -= self.remaining
            self.remaining = Decimal("0.00")
            self.credit = amount

    def expected_paid(self, as_of_date: date | None = None) -> Decimal:
        count = 0
        month_offset = 0
        if as_of_date is None:
            as_of_date = self.get_today()
        if self.pay_frequency == "a":
            if as_of_date >= date(self.end_of_fy.year, 1, 1):
                return self.annual
            else:
                return self.money("0")
        else:
            while True:
                year = self.start_of_fy.year + ((6 + month_offset) // 12)
                month = (6 + month_offset) % 12 + 1
                due_date = date(year, month, 15)
                if due_date >= as_of_date:
                    break
                count += 1
                if self.pay_frequency == "q":
                    month_offset += 3
                else:
                    month_offset += 1
        return self.calc_payments(self.annual) * count

    def check_on_track(self, as_of_date: date | None = None) -> bool:
        if self.outstanding != self.money(0):
            return False
        expected = self.expected_paid(as_of_date)
        actual_paid = self.annual - self.remaining
        return actual_paid >= expected

    def to_dict(self) -> dict[str, str]:
        # Credit should show as negative outstanding amount
        id = str(self.id)
        account_id = str(self.account_id)
        site_number = str(self.site_number)
        annual = str(self.annual)
        remaining = self.remaining
        outstanding = str(self.outstanding)
        pay_frequency = self.pay_frequency
        # Converts credit into a negative remaining amount
        if self.credit != self.money(0):
            remaining -= self.credit
        remaining = str(remaining)
        return {
            "ID": id,
            "Account ID": account_id,
            "Site": site_number,
            "Annual Fee": annual,
            "Remaining from this FY": remaining,
            "Outstanding from previous FYs": outstanding,
            "Pay Frequency": pay_frequency,
        }

    def __str__(self) -> str:
        return f"Balance for {self.site_number} with Account ID {self.account_id} -> Annual = {self.annual}, Remaining = {self.remaining}, Outstanding = {self.outstanding}, Pay Frequency = {self.pay_frequency}"
