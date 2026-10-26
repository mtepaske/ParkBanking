from decimal import Decimal


class Site:
    """
    Tracks information for sites and their facilities. Used for calculating annual fees

    Attributes:
        site_number: (int) The site number
        ac: (bool) If the site has an air conditioner unit
        sewer: (bool) If the site has a sewer
        cabin: (bool) If the site is a cabin
    """

    def __init__(self, site_number: int, ac: bool, sewer: bool, cabin: bool) -> None:
        """
        Initialises the class

        Args:
            site_number: The site number
            ac: True if the site has an air conditioning unit
            sewer: True if the site has a sewer
            cabin: True if the site is a cabin. Defaults to False
        """

        self.site_number = site_number
        self.ac = ac
        self.sewer = sewer
        self.cabin = cabin

    def change_ac(self) -> None:
        """Change the ac status"""
        self.ac = not self.ac

    def change_sewer(self) -> None:
        """Change the sewer status"""
        self.sewer = not self.sewer

    def change_cabin(self) -> None:
        """Change the cabin status"""
        self.cabin = not self.cabin

    def calc_annual_fees(
        self,
        extra_guests: int,
        base_rate: Decimal,
        ac_rate: Decimal,
        sewer_rate: Decimal,
        extra_guests_rate: Decimal,
    ) -> Decimal:
        """
        Calculates the annual fees for the site

        Args:
            extra_guests: The amount of extra nominated visitors
            base_rate: The base annual fees
            ac_rate: The extra charge for ac
            sewer_rate: The extra charge for sewer
            extra_guests_rate: The extra charge for extra nominated visitors

        Returns:
            The calculated annual fee
        """

        return (
            base_rate
            + (ac_rate * int(self.ac))
            + (sewer_rate * int(self.sewer))
            + (extra_guests * extra_guests_rate)
        )
