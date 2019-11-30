from swagger_spec_validator.common import SwaggerValidationWarning
from polo_loan_agent import LoanAgent
import warnings
import datetime
import requests
import poloniex
import bitmex
import json


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
        key='',
        secret=""
            ""
            "")

    HEDGE_REQUIRED = False

    # Hedging platform
    HEDGE_PROVIDER = "BitMEX"

    # Hedging platform API client
    HEDGE_API = bitmex.bitmex(
        test=False,
        api_key='',
        api_secret='')

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

    def open_account(): 
        """ Initiate the loan and hedge. This method must be invoked to start
            the account after the account objcet has been created.
        """

        self.convert_currency()
        # self.loan = init_loan()
        self.hedge = init_hedge()
        

    def init_loan(self):
        """ Open a loan with third party lending platform. We use Poloniex
            for this demo. Future versions can include integrations with
            multiple platforms, and the ability to automatically select the
            optimal (most stable and profitable) asset and lending provider.
            Loan class has a LoanAgent which cancels old loan offers, turns
            auto-renew off on active loans, and creates new loan offers at
            fair price (fair = average of the lowest three loan offers).
            """

        # return Loan(
        #     self.LENDER_API,
        #     self.logger,
        #     self.LOAN_ASSET,
        #     self.initial_deposit,
        #     self.duration,
        #     LoanAgent(
        #         self.logger,
        #         self.LENDER_API,
        #         {self.LOAN_ASSET: self.MIN_LOAN},
        #         self.initial_deposit))    


    def get_lending_stats(self):
        """ Return dict of loan stats, set current_interst_rate variable
            whenever this is invoked to reduce # of external polling.
        """

        stats = self.loan.api.returnActiveLoans()['provided'][0]
        self.current_interest_rate = float(stats['rate']) * 100
        self.loan.current_interest_rate = float(stats['rate']) * 100
        return stats

    def get_hedge_stats(self):
        """ Return a dict containing hedge stats."""

        # use stats['currentQty'] to get the size of the positon
        stats = self.hedge.api.Position.Position_get(
            filter=json.dumps(
                {'symbol': self.current_instrument})).result()[0][0]

    def get_avg_interest_rate(self):
        """ Return the average interest rate to date for the loaned asset."""

    def convert_currency(self):
        """ Convert deposited local currency to the target asset.
            Note that this functionality is not implemented for the demo app,
            we pre-converted our local currency to the target loan asset for
            speed and convenience (USDC being the loan asset).
            A full implementation of this app will require integration with a
            third party currency broker.
        """