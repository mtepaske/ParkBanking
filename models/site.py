from decimal import Decimal


class Site:

    def __init__(self, site_number: int, ac: bool, sewer: bool, cabin: bool) -> None:
        self.site_number = site_number
        self.ac = ac
        self.sewer = sewer
        self.cabin = cabin

    def change_site_number(self, new_number: int) -> None:
        self.site_number = new_number

    def change_ac(self) -> None:
        self.ac = not self.ac

    def change_sewer(self) -> None:
        self.sewer = not self.sewer

    def change_cabin(self) -> None:
        self.cabin = not self.cabin

    def calc_annual_fees(
        self,
        extra_guests: int,
        base_rate: Decimal,
        ac_rate: Decimal,
        sewer_rate: Decimal,
        extra_guests_rate: Decimal,
    ) -> Decimal:
        return (
            base_rate
            + (ac_rate * int(self.ac))
            + (sewer_rate * int(self.sewer))
            + (extra_guests * extra_guests_rate)
        )
