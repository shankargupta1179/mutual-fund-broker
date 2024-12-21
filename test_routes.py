import unittest
from run import app, db, User
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        with app.app_context():
            db.create_all()

        self.user_data = {
            "email": "test@example.com",
            "password": "testpassword"
        }
        self.user = User(
            email=self.user_data['email'],
            password_hash=generate_password_hash(self.user_data['password'])
        )
        with app.app_context():
            db.session.add(self.user)
            db.session.commit()

    # Clean up
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def get_auth_token(self):
        access_token = create_access_token(identity=self.user_data['email'])
        return access_token

    def test_signup(self):
        new_user = {
            "email": "newuser@example.com",
            "password": "newpassword"
        }
        response = self.app.post('/signup', json=new_user)
        self.assertEqual(response.status_code, 201)
        self.assertIn('User created successfully!', response.get_data(as_text=True))

    def test_login(self):
        response = self.app.post('/login', json=self.user_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)

    def test_get_all_open_schemes(self):
        response = self.app.get('/open-schemes')
        self.assertEqual(response.status_code, 401)

    def test_buy_units(self):
        token = self.get_auth_token()
        data = {
            "scheme_code": "02-DP-L1",
            "investment_amount": 500
        }
        response = self.app.post(
            '/buy-units', 
            json=data, 
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Investment successful!', response.get_data(as_text=True))

    def test_get_portfolio_value(self):
        token = self.get_auth_token()
        response = self.app.get(
            '/portfolio-value', 
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('portfolio_value', response.json)

    def test_get_fund_family_house(self):
        response = self.app.get('/fund-family?family=Birla')
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
