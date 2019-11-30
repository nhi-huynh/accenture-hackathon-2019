from datetime import datetime, timedelta

class Loan:
    """Loan class models the lending product utilised."""

    def __init__(self, logger, api, asset, deposit, duration, agent):
        self.api = api
        self.logger = logger

        # Asset we are lending (string)
        self.asset = asset

        # intended size of the loan, in native denomination
        self.total = deposit

        # Current price of the asset in USD (one unit)
        self.current_price = 0

        # Current daily interest rate of the loan
        self.current_interest_rate = 0

        # Date of termination of the loan
        self.close_date = self.get_close_date(duration)

        # Loan agent runs in background in a new thread
        self.loan_agent = agent

        # Loan status - when loan terminated, this will be false.
        self.active = True

    def get_price(self, asset):
        """Return the current USD price of one unit of the asset. Becasuse
        we use USDC for loans, the price will awlays be 1 (USD). Future
        implementations with non-pegged assets will poll the lending provider
        for the current price."""

        if self.asset == "USDC":
            return 1

        return 0

    def update_loan_size(self, new_loan_size):
        """Adjusts total size of loan (use when adjusting accrued interest).
        Changes may take 48hr to propagate, depending on current loan.
        This is intended to be used only for incrementing loans with
        interest payouts."""

        self.loan_agent.update_loan(new_loan_size)
        print('Loan size updated. Allow 48hrs for changes to propagate.')

    def get_interest_history(self):
        """Return dict containing interest payout history."""

    def terminate_loan(self):
        """Stop the loan agent from renewing loans and offers, may take max 48
        hrs to garuantee all loans are closed."""

        self.loan_agent.active = False
        self.active = False
        print('Loan terminated. Allow 48hrs for all lending to cease.')

    def get_close_date(self, duration):
        """Return the date [duration] days from now."""

        close = datetime.utcnow() + timedelta(days=10)
        close = close.replace(microsecond=0, second=0, minute=0, hour=0)
        return close