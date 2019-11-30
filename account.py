from swagger_spec_validator.common import SwaggerValidationWarning
from polo_loan_agent import LoanAgent
import warnings
import datetime
import requests
import poloniex
import bitmex
import json
from hedge import Hedge
from loan import Loan


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

    """ BlockFi is a digital asset lender offering BTC, ETH and other assets.
        BlockFi was our first choice, but we were unable to get ID-verified and
        intergrate with their platform in time for this event. BlockFi would
        have been a great example of a legacy (non-USD pegged) DeFi loan
        (i.e using Bitcoin).
    """
    # LOAN_PROVIDER = "BlockFi"
    # LOAN_ASSET = "Bitcoin"
    # MIN_LOAN = ""
    # MIN_TERM = ""
    # HEDGE_REQUIRED = True
    # BLOCKFI_API = ""

    """ Poloniex is a JP-Morgan subsidiary digital asset exchange in the US.
        They offer spot, lending and borrowing of digital assets. Of interest
        to us is their capability to lend USDC, a new type of digital asset
        that has its value pegged to the US dollar. This simplifies and
        stabilises our hedged account concept; USDC also has a strong lending
        rate, typically 6-8% p/annum, often fluctuating above 10%. Poloniex is
        also an ideal lending platofrm as they offer very flexible loans, with
        a miunimum duration of 2 days, and interest calculated daily.
    """

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

    """ BitMEX is the largest digital assset derivatives exchange in the world.
        They offer a huge range of futures and swap contracts for Bitcoin, plus
        many other assets. Of interest to us are the perpetual and quarterly
        futures for Bitcoin (and other popular assets we may want to lend).
        BitMEX's perpetual swap contract has a funding rate, charged at 8hr
        intervals. The default funding rate is 10.95% p/year, or 0.01% p/8hrs.
        The way this works is "longs pay shorts" - this means traders in long
        positions will pay  (funding rate * position size) to traders in
        short postions, every funding interval.
        In times of extreme demand, the funding rate will fluctuate. A positive
        rate (default 0.01%) means longs pay shorts, though a negative rate
        means shorts pay longs. We want to avoid being positioned in the
        perpetual contract when the rate is negative, while being positioned in
        it when the rate is positive, to reap the funding interest payout.
        We apply machine learning to the price history of our hedged asset
        (Bitcoin) and the perpetual's funding rate to attempt to predict when
        the perpetual fudning rate will be negative, in order to consequently
        roll the hedge over into a different type of futures contract that does
        not attract funding, such as the quarterly futures.
        In this way, we can combine the base lending rate from BlockFi (~6.2%),
        and the positive funding to earn an aggregate rate of ~10-15% or more,
        all whilst having mitigated the volatile price movements of the
        underlying asset due to being hedged 100% of the time.
        Note that we could not utilise lending through with BlockFi due to time
        and legal constraints, instead using Poloniex to lend a non-volatile
        asset, USCD. We have still implemented hedging functionality for the
        sake of proof-of-concept of the combined higher interest rate.
    """

    # As described below, this demo uses USDC, an asset not requiring hedging,
    # however hedging is implemented, working and will be demonstrated.
    HEDGE_REQUIRED = False

    # Hedging platform
    HEDGE_PROVIDER = "BitMEX"

    # Hedging platform API client
    HEDGE_API = bitmex.bitmex(
        test=False,
        api_key='TsClPuXtKz8Yxtf5EPkNL0hV',
        api_secret='fFDYVqQl59Uku_1u8HFOnHHIXz1Tq5IM0H4wQIumgh-vvfun')

    def __init__(self, logger, account_id, duration=365, initial_deposit=50):
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

    def open_account(self):
        """ Initiate the loan and hedge. This method must be invoked to start
            the account after the account objcet has been created.
        """

        self.convert_currency()
        # Make a $50 loan for 2 days
        self.loan = self.init_loan()
        self.hedge = self.init_hedge()
        self.hedge.terminate_hedge()

    def init_loan(self):
        """ Open a loan with third party lending platform. We use Poloniex
            for this demo. Future versions can include integrations with
            multiple platforms, and the ability to automatically select the
            optimal (most stable and profitable) asset and lending provider.
            Loan class has a LoanAgent which cancels old loan offers, turns
            auto-renew off on active loans, and creates new loan offers at
            fair price (fair = average of the lowest three loan offers).
            """
        #Loan(logger, api, asset, deposit, duration, agent)
        return Loan(
            self.logger,
            self.LENDER_API,
            self.LOAN_ASSET,
            self.initial_deposit,
            self.duration,
            LoanAgent(
                self.logger,
                self.LENDER_API,
                {self.LOAN_ASSET: self.MIN_LOAN},       #{"USDC" : 50}
                self.initial_deposit))                  #50

    def init_hedge(self):
        """ Open a hedge with third party derivatives exchange. Because we
            use USDC for our loan, it doesnt require hedging. We use Bitcoin
            derivates for hedging Bitcoin, when we use Bitcoin as a lending
            asset.
        """

        hedge = Hedge(
            self.logger,
            self.HEDGE_API,
            self.LOAN_ASSET,
            self.initial_deposit,
            self.duration)

        hedge_details = hedge.open_hedge()

        print(hedge_details)
        print(hedge)

        return hedge

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
                {'symbol': self.hedge.current_instrument})).result()[0][0]
        return stats

    def get_avg_interest_rate(self):
        """ Return the average interest rate to date for the loaned asset."""

    def convert_currency(self):
        #Don't worry about this
        """ Convert deposited local currency to the target asset.
            Note that this functionality is not implemented for the demo app,
            we pre-converted our local currency to the target loan asset for
            speed and convenience (USDC being the loan asset).
            A full implementation of this app will require integration with a
            third party currency broker.
        """