class Account:
    """ Account class models the hedged account concept, containing loan and
        hedge classes, and facilities to save and restore state to and from
        a database."""

    # Ignore warning, Swagger validator has a bug. BitMEX API uses Swagger.
    warnings.simplefilter("ignore", SwaggerValidationWarning)

    """
        Native currency denomination. Note that our hedged account maintains a
        USD value. A future implementation will integrate with a traditional
        currency broker to maintain local currency value vs USD (if desired).
        Maintaining USD value instead of local may be more benefitial for uses
        who live in countries with weaker currencies or economic issues.
    """
    LOCAL_CURRENCY = "AUD"

    # Lending platform
    LOAN_PROVIDER = "Poloniex"

    # Asset we are lending
    LOAN_ASSET = "USDC"

    # Smallest permissible loan size (set by provider)
    MIN_LOAN = 50

    # Minimum duration of loan in days
    MIN_TERM = 2

    # As described below, this demo uses USDC, an asset not requiring hedging,
    # however hedging is implemented, working and will be demonstrated.
    HEDGE_REQUIRED = False

    # Lending platform API client
    LENDER_API = poloniex.Poloniex(
        key='HHDRON6N-H7C3LA42-AXV8EMJI-LPLUQD2Y',
        secret="c05289ca176fc5981118756accc84172a513609df14b8fa887"
            "cf6cf980292f724efbacd5fcd925f810cfaf71c0edfff31a4d0cfc"
            "1e41ea23a1a3cad1706d5c44")

    HEDGE_REQUIRED = False

    # Hedging platform
    HEDGE_PROVIDER = "BitMEX"

    # Hedging platform API client
    HEDGE_API = bitmex.bitmex(
        test=False,
        api_key='TsClPuXtKz8Yxtf5EPkNL0hV',
        api_secret='fFDYVqQl59Uku_1u8HFOnHHIXz1Tq5IM0H4wQIumgh-vvfun')

    def __init__(self, logger, account_id, duration=365, initial_deposit=100):
        self.logger = logger

        # Unique account identifier
        self.account_id = account_id

        # Duration of the account in days, default 365
        self.duration = duration

        # Account starting balance in USD, default $100
        self.initial_deposit = initial_deposit

        # Current value of the account in USD
        self.current_balance = initial_deposit

        # Current interest rate for the loaned asset
        self.current_interest_rate = None

        # Average interest rate for the loaned asset
        self.avg_interest_rate = None

        # Total USD value of all interest payouts
        self.interest_paid_to_date = 0

        # Stores daily interest rates datetime: rate
        self.interest_rate_history = {}

        # Stores balance: datetime for each time the balance changes
        self.balance_history = {}

        # Use this account as default payout account
        self.payout_account = self.account_id

        #  If yes, interest gets re-invested each time its paid out.
        self.compounding = True

        # Loan class for the loan we place on Polo/BlockFi
        self.loan = None

        # Hedge class for the hedge against our loaned asset.
        self.hedge = None