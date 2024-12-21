import os
import requests
from http import HTTPStatus
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///mutual_fund.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'sample'
jwt = JWTManager(app)
db = SQLAlchemy(app)

RAPID_API_HOST = os.getenv('RAPID_API_HOST')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')


class User(db.Model):
    id = db.Column(db.Integer)
    email = db.Column(db.String(100),primary_key=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    portfolio_value = db.Column(db.Float, default=0.0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
with app.app_context():
    db.create_all()



@app.route('/signup', methods=['POST'])
def signup():
    """
    This endpoint is used to sign up for the new users 
    Schema: 
    {
        "email": "test@example.com",
        "password": "password"
    }
    """
    data = request.get_json()  # Get the data sent in the POST request
    
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    # Check if the email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "Email is already registered"}), 400

    # Create new user and hash password
    new_user = User(email=email)
    new_user.set_password(password)

    # Save user to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully!"}), 201

@app.route('/login', methods=['POST'])
def login():
    """
    this endpoint checks whether the user has been registered with provided email and password is 
    correct or not 
    Schema:
    {   
        "email": "test@example.com",
        "password": "password"
    }
    """
    data = request.get_json()  # Get the data sent in the POST request
    
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    # Check if the email exists
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"message": "Email not found"}), 404

    # Check if the password is correct
    if not user.check_password(password):
        return jsonify({"message": "Incorrect password"}), 401
    
    access_token = create_access_token(identity=email, fresh=True)

    return jsonify({"message": "Login successful!", "access_token": access_token}), 200

@app.route('/open-schemes', methods=['GET'])
@jwt_required()
def get_all_open_schemes():
    """
    this endpoint is focused to fetch all the open schemes from the rapid api
    """
    url = "https://latest-mutual-fund-nav.p.rapidapi.com/latest"

    headers = {
        "x-rapidapi-host": RAPID_API_HOST,
        "x-rapidapi-key": RAPID_API_KEY
    }

    params = {"Schema_Type": "Open"}

    resp = requests.get(url=url, headers=headers, params=params)

    if resp.status_code == HTTPStatus.OK:
        all_open_schemes = resp.json()

        return all_open_schemes

@app.route('/fund-family', methods=['GET'])
@jwt_required()
def get_fund_family_house():
    """
    this endpoint is focused to fetch open ended schemes for a fund family house
    """
    try:
        url = "https://latest-mutual-fund-nav.p.rapidapi.com/latest"

        headers = {
            "x-rapidapi-host": RAPID_API_HOST,
            "x-rapidapi-key": RAPID_API_KEY
        }

        params = {
            "Scheme_Type": "Open",
            "Mutual_Fund_Family": request.args.get('family')
        }

        resp = requests.get(url=url, headers=headers, params=params)

        if resp.status_code == HTTPStatus.OK:
            return resp.json()
        else: 
            raise Exception
    except Exception as e:
        raise Exception("Error while Getting fund family house data {}".format(e))

@app.route('/buy-units',methods=['POST'])
@jwt_required()
def buy_units():
    """
    this end point helps us to buy mutual fund units 
    Schema
    {
        "scheme_code": "02-DP-L1", 
        "investment_amount": 500
    }
    """
    user_id = get_jwt_identity()  # Get the user ID from the JWT token
    user = db.session.get(User, user_id)

    # Fetch mutual fund details from the API
    url = "https://latest-mutual-fund-nav.p.rapidapi.com/master"
    headers = {
        "x-rapidapi-host": RAPID_API_HOST,
        "x-rapidapi-key": RAPID_API_KEY
    }

    params = {
        "Scheme_Code": request.args.get('scheme_code'),
    }

    try:
        resp = requests.get(url, headers=headers, params=params)
        data = resp
    except requests.exceptions.RequestException as e:
        return jsonify({"message": "Error fetching mutual fund data", "error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

    # Extract relevant mutual fund data from the API response
    scheme_code = request.json.get('scheme_code')
    investment_amount = request.json.get('investment_amount')

    # Find the mutual fund that matches the provided Scheme Code
    mutual_fund = next((mf for mf in data if mf["Scheme_Code"] == scheme_code), None)

    if not mutual_fund:
        return jsonify({"message": "Mutual fund not found for the given Scheme Code!"}), HTTPStatus.NOT_FOUND

    min_purchase_amount = mutual_fund.get('Minimum_Purchase_Amount')

    # Check if the investment amount is valid
    if investment_amount < min_purchase_amount:
        return jsonify({"message": f"Investment amount must be at least {min_purchase_amount}!"}), HTTPStatus.BAD_REQUEST

    # If the investment is valid, update the portfolio value
    user.portfolio_value += investment_amount
    db.session.commit()

    return jsonify({
        "message": "Investment successful!",
        "new_portfolio_value": user.portfolio_value
    }), HTTPStatus.OK

@app.route('/portfolio-value', methods=['GET'])
@jwt_required()
def get_portfolio_value():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    return {
        "portfolio_value": user.portfolio_value
    }


if __name__ == '__main__':
    app.run(debug=True)
