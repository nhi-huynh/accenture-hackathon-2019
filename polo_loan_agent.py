from threading import Thread
from time import time, sleep, strptime
from calendar import timegm


class LoanAgent:
    """Poloniex loan refresher agent. Keep offers current (i.e at fair rate)
    by cancelling loans older than 10min, and creating new loan offers at fair
    rates (average of lowest three rates)."""

    def __init__(self, logger, api, assets, initial_deposit=50):
        self.logger = logger
        self.api = api
        self.assets = assets
        self.delay = 150
        self.maxage = 300
        self.loan_size = initial_deposit
        self.active = True

        # Raise error if API/keys not present
        if api is None:
            raise ValueError("Poloniex API client required.")

        thread = Thread(
            target=lambda: self.run(),
            daemon=True)
        thread.start()
        self.logger.debug("Started loan agent daemon.")

    def run(self):
        """Main loop."""

        self.running = True

        # Check auto renew is not enabled for current loans
        self.autorenew_toggle(self.api)
        while self.running:
            if self.active:
                try:
                    # Check for old offers
                    self.cancelOldOffers()
                    # Create new offer (if can)
                    self.create_loan_offers()
                    # show active
                    active = self.api.returnActiveLoans()['provided']
                    self.logger.debug('Active Loan:')
                    for i in active:
                        self.logger.debug('%s|%s:%s-[rate:%s]-[fees:%s]',
                                          i['date'],
                                          i['currency'],
                                          i['amount'],
                                          str(float(i['rate']) * 100) + '%',
                                          i['fees'])
                except Exception as e:
                    self.logger.exception(e)

                finally:
                    for i in range(int(self.delay)):
                        sleep(1)

    def get_loan_offer_age(self, order):
        return time() - self.utc_to_timestamp(order['date'])

    def cancelOldOffers(self):
        offers = self.api.returnOpenLoanOffers()
        for asset in self.assets:
            if asset not in offers:
                self.logger.debug("No open %s offers found.", asset)
                continue
            for offer in offers[asset]:
                self.logger.debug(
                    "%s|%s:%s-[Daily rate:%s]",
                    offer['date'],
                    asset,
                    offer['amount'],
                    str(float(offer['rate']) * 100) + '%')
                if self.get_loan_offer_age(offer) > self.maxage:
                    self.logger.debug(
                        "Canceling %s offer %s",
                        asset, str(offer['id']))
                    self.logger.debug(self.api.cancelLoanOffer(offer['id']))

    def create_loan_offers(self):
        bals = self.api.returnAvailableAccountBalances()
        if 'lending' not in bals:
            return self.logger.debug("No assets found in lending account.")
        for asset in self.assets:
            if asset not in bals['lending']:
                continue
            amount = self.loan_size

            # Check there is enough currency to loan
            if float(amount) < self.assets[asset]:
                self.logger.debug(
                    "Not enough %s:%s, below set minimum: %s",
                    asset,
                    str(amount),
                    str(self.assets[asset]))
                continue
            else:
                self.logger.debug("%s:%s", asset, str(amount))
            orders = self.api.returnLoanOrders(asset)['offers']

            # Fair price strategy = use the average of the first three offers
            price = sum([float(o['rate']) for o in orders[:3]]) / 3

            # Aggressive price strategy = use current lowest offer * 0.99
            # price = sum([float(o['rate']) for o in orders[:1]]) * 0.99

            self.logger.debug(
                'Creating %s %s loan offer at %s',
                str(amount), asset, str(price * 100) + '%')
            r = self.api.createLoanOffer(asset, amount, price, autoRenew=0)
            self.logger.debug('%s', r["message"])

    def autorenew_toggle(self, api, toggle=False):
        """ Turns auto-renew on or off for all active loans """

        if toggle:
            toggle = 1
        else:
            toggle = 0
        for loan in api.returnActiveLoans()['provided']:
            if int(loan['autoRenew']) != toggle:
                self.logger.debug(
                    'Toggling autorenew offer %s',
                    str(loan['id']))
                api.toggleAutoRenew(loan['id'])

    def utc_to_timestamp(self, datestr, fmat="%Y-%m-%d %H:%M:%S"):
        """Takes UTC date string. Returns epoch timestamp. """

        return timegm(strptime(datestr, fmat))

    def update_loan_size(self, size):
        """Update loan_size for future loans."""

        self.loan_size = size