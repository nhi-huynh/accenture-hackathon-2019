rom time import time, sleep, strptime
from polo_loan_agent import LoanAgent
import poloniex
import requests
import datetime
import logging


class LoanAgent:
    """ Poloniex loan refresher. Keep offers current (i.e at fair rate)
    by cancelling loans older than 10min, and creating new loan offers at fair
    rates (average of lowest three rates)."""

    def __init__(self, logger, api, assets, initial_deposit):
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
