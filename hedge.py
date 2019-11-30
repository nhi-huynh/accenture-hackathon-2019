class Hedge:
    """Hedge class models the hedge taken to mitigate loan volatility."""

    """ Industry-standard monthly futures contract codes. The month code
        signifies contract delivery month e.g AUDJPYZ19 would be a contract
        derived from the AUDJPY pair with settlement (expiry) in December 2019.
    """
    FUTURES_MONTH_CODES = {
        'F': 'Jan', 'G': 'Feb', 'H': 'Mar', 'J': 'Apr', 'K': 'mar', 'M': 'Jun',
        'N': 'Jul', 'Q': 'Aug', 'U': 'Sep', 'V': 'Oct', 'X': 'Nov', 'Z': 'Dec'}