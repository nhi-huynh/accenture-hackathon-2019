from time import time, sleep, strptime
import requests
import datetime
import logging


class Hedge:
    """	Hedge class models the hedge taken to mitigate loan volatility."""

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
        self.close_date = self.close_date(duration)

        # Use the perpetual swap contract as the default hedging instrument.
        self.default_instrument = "XBTUSD"

        # Instrument code currently in use, perpetual swap is default.
        self.current_instrument = self.default_instrument

        # Futures rollover date for instrument in use.
        self.rollover_date = None

        # Hedge status - when hedge terminated, this will be false.
        self.active = True
