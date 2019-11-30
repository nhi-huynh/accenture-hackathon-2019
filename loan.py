class Loan:
    """ Loan class models the lending product utilised."""

    def __init__(self, api, logger, asset, deposit, duration, agent):
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
        self.close_date = self.close_date(duration)

        # Loan agent runs in background in a new thread
        self.loan_agent = agent

        # Loan status - when loan terminated, this will be false.
        self.active = True
