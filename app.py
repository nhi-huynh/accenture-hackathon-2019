from flask import Flask, jsonify, request

from entity_controller import EntityController

app = Flask(__name__)

# Create controllers to control each entity
user_controller = EntityController("Users", "user_id", "last_name")
account_controller = EntityController("Accounts", "account_id", "user_id")
loan_controller = EntityController("Loans", "loan_id")
hedge_controller = EntityController("Hedges", "hedge_id")

# A controller to the balance table
balance_controller = EntityController("Balances", "timestamp", "account_id")

# A controller to the net interests of the account
net_interest_controller = EntityController("Net_interests", "timestamp", "account_id")

# A controller to the loan interests of the account
loan_interest_controller = EntityController("Loan_interests", "timestamp", "account_id")

# A controller to the funding rates of the account
funding_rate_controller = EntityController("Funding_rates", "timestamp", "account_id")