
class User:
    """ User class models the customer (account holder)."""

    def __init__(self, user_id, fname, lname, email, pwd):
        self.user_id = user_id
        self.first_name = fname
        self.last_name = lname
        self.email = email
        self.password_hash = pwd
        self.account = None

    def init_account(self, account):
        """Create the account object. Account needs to be started with
        account.open_account() after creation to init the loan and hedge."""
