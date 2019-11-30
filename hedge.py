from time import time, sleep, strptime
from datetime import datetime, timedelta
import requests
import logging
import json

class Hedge:
    """Hedge class models the hedge taken to mitigate loan volatility."""

    """ Industry-standard monthly futures contract codes. The month code
        signifies contract delivery month e.g AUDJPYZ19 would be a contract
        derived from the AUDJPY pair with settlement (expiry) in December 2019.
    """
    FUTURES_MONTH_CODES = {
        'F': 'Jan', 'G': 'Feb', 'H': 'Mar', 'J': 'Apr', 'K': 'mar', 'M': 'Jun',
        'N': 'Jul', 'Q': 'Aug', 'U': 'Sep', 'V': 'Oct', 'X': 'Nov', 'Z': 'Dec'}

    def __init__(self, logger, api, asset, value, duration):
        self.logger = logger
        self.api = api

        # Asset the hedge is covering. For our example, Bitcoin
        self.underlying_asset = asset

        # USD value of the hedge. Must have exact 1:1 parity with loan size.
        self.value = value

        # Fixed termination date of the hedge (and loan).
        self.close_date = self.get_close_date(duration)

        # Use the perpetual swap contract as the default hedging instrument.
        self.default_instrument = "XBTUSD"

        # Instrument code currently in use, perpetual swap is default.
        self.current_instrument = self.default_instrument

        # Futures rollover date for instrument in use.
        self.rollover_date = None

        # Hedge status - when hedge terminated, this will be false.
        self.active = True

    def open_hedge(self):
        """Open a hedge (short positon) with the specified instrument, default
        is perpetual swap contact."""

        order = self.api.Order.Order_new(
            symbol=self.current_instrument,
            orderQty=(self.value * -1)).result()

        print("Hedge opened for " + str(self.value) + " contracts.")
        self.active = True

        # Return transaction details json
        return order

    def terminate_hedge(self):
        """Close the hedge postion and return confirmation dict containing
        details of the closed positon. Hedge cLosure effective immediately."""

        # Close all positions
        result = self.api.Order.Order_new(
            symbol=self.current_instrument,
            ordType='Market',
            execInst='Close').result()

        print("Hedge closed for " + str(result[0]['orderQty']) + " contracts.")
        self.active = False

        # Return transaction details json
        return result

    def update_hedge_size(self, amount):
        """Adjust total size of hedge to match provided amount."""

        # Get size of existing postion
        positions = self.api.Position.Position_get(
            filter=json.dumps({'symbol': self.current_instrument})).result()

        # Update position to match new amount
        val = positions[0][0]['currentQty']
        new_val = (amount * -1) - val
        order = self.api.Order.Order_new(
            symbol=self.current_instrument,
            orderQty=(new_val * -1)).result()

        # Return transaction details json
        return order

    def get_close_date(self, duration):
        """Return the date [duration] days from now."""

        close = datetime.utcnow() + timedelta(days=10)
        close = close.replace(microsecond=0, second=0, minute=0, hour=0)
        return close

    def rollover_instrument(self, new_instr):
        """Incrementally close the current hedge and re-initiate it in a
        new instrument."""

    def get_quarterly_future(self, asset):
        """Return the appropriate contract code for quarterly futures."""

    def get_biannual_future(self, asset):
        """Return the appropriate contract code for quarterly futures."""