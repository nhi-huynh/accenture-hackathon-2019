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

#------------------------ INDEX ENDPOINTS ------------------------------  

@app.route('/')
def index():
    return "API for the DeFiBank app"

#------------------------ USERS ENDPOINTS ------------------------------        
# Use this json to test the user endpoints using Postman
#   {
#         "user_id": "U001",
#         "first_name": "Nhi",
#         "last_name": "Huynh",
#         "email": "nhi.huynh@gmail.com",
#         "password_hash": "password", 
#         "account_id": "A001"
#     }

# Test with a second user
# {
#     "user_id": "U002",
#     "first_name": "Sam",
#     "last_name": "Breznika",
#     "email": "sam.brez@gmail.com",
#     "password_hash": "password", 
#     "account_id": "A002",
#     "account_type": "standard_user"
# }
# 

@app.route('/users', methods=["GET"])
def get_users():
    return jsonify(user_controller.get_entities())

@app.route('/users/<user_id>', methods=["GET"])
def get_user_by_id(user_id):
    return jsonify(user_controller.get_entity(user_id))

@app.route('/users', methods=["POST"])
def create_user():
    return jsonify(user_controller.create_entity(request.json))

@app.route('/users/<user_id>', methods = ["PUT"])
def update_user(user_id):
    return jsonify(user_controller.update_entity(request.json))

@app.route('/users/<user_id>', methods = ["DELETE"])
def delete_user(user_id):
    return jsonify(user_controller.delete_entity(user_id))



#------------------------ LOANS ENDPOINTS ------------------------------    
# Use this json to test the account endpoints using Postman
#   "total" is a reserved key word so change it to "total_loan"
# {
#     "loan_id": "L001",
#     "asset": "Bitcoin",
#     "total_loan": "1000",
#     "current_price": "7000",
#     "current_interest_rate": "10", 
#     "close_date": "2019-11-27 14:09:01.772253",
#     "active": "true",
#     "account_id": "A001",
#     "interest_rate_history": ""
# }
# 

@app.route('/loans', methods=["GET"])
def get_loans():
    return jsonify(loan_controller.get_entities())

@app.route('/loans/<loan_id>', methods=["GET"])
def get_loan_by_id(loan_id):
    return jsonify(loan_controller.get_entity(loan_id))

@app.route('/loans', methods=["POST"])
def create_loan():
    return jsonify(loan_controller.create_entity(request.json))

@app.route('/loans/<loan_id>', methods = ["PUT"])
def update_loan(loan_id):
    return jsonify(loan_controller.update_entity(request.json))

@app.route('/loans/<loan_id>', methods = ["DELETE"])
def delete_loan(loan_id):
    return jsonify(loan_controller.delete_entity(loan_id))
