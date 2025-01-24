import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from marshmallow import Schema, fields, ValidationError
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{os.getenv("POSTGRES_PASSWORD")}@db/{os.getenv("POSTGRES_DB")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    account = db.relationship('Account', backref='user', uselist=False, cascade="all, delete-orphan")
    records = db.relationship('Record', backref='user', lazy=True)

    def __init__(self, name):
        self.name = name

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    balance = db.Column(db.Float, default=0)

    def __init__(self, balance=0):
        self.balance = balance

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __init__(self, name):
        self.name = name

class Record(db.Model):
    __tablename__ = 'records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id, category_id, amount):
        self.user_id = user_id
        self.category_id = category_id
        self.amount = amount

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class RecordSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    category_id = fields.Int(required=True)
    amount = fields.Float(required=True)
    timestamp = fields.DateTime(dump_only=True)

class AccountSchema(Schema):
    user_id = fields.Int(dump_only=True)
    balance = fields.Float(dump_only=True)

with app.app_context():
    db.create_all()

@app.route("/user", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        user_schema = UserSchema()
        user_data = user_schema.load(data)

        user = User(name=user_data['name'])
        db.session.add(user)
        db.session.commit()

        
        account = Account()
        user.account = account
        db.session.add(account)
        db.session.commit()

        user_dumped = user_schema.dump(user)
        return jsonify(user_dumped), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        app.logger.error(f"Error in creating user: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/users", methods=["GET"])
def get_users():
    try:
        users = User.query.all()
        user_schema = UserSchema(many=True)
        users_dumped = user_schema.dump(users)
        return jsonify(users_dumped)
    except Exception as e:
        app.logger.error(f"Error in fetching users: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/category", methods=["POST"])
def create_category():
    try:
        data = request.get_json()
        category_schema = CategorySchema()
        category_data = category_schema.load(data)

        category = Category(name=category_data['name'])
        db.session.add(category)
        db.session.commit()

        category_dumped = category_schema.dump(category)
        return jsonify(category_dumped), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        app.logger.error(f"Error in creating category: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/record", methods=["POST"])
def create_record():
    try:
        data = request.get_json()
        record_schema = RecordSchema()
        record_data = record_schema.load(data)

        user = User.query.get(record_data['user_id'])
        category = Category.query.get(record_data['category_id'])
        if not user or not category:
            return jsonify({"error": "Invalid User ID or Category ID"}), 400

        account = user.account
        if not account:
            return jsonify({"error": "Account not found"}), 404

        if account.balance < record_data['amount']:
            return jsonify({"error": "Insufficient funds"}), 400

        account.balance -= record_data['amount']
        db.session.add(account)

        record = Record(user_id=record_data['user_id'], category_id=record_data['category_id'], amount=record_data['amount'])
        db.session.add(record)
        db.session.commit()

        record_dumped = record_schema.dump(record)
        return jsonify(record_dumped), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        app.logger.error(f"Error in creating record: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/record", methods=["GET"])
def get_records():
    try:
        user_id = request.args.get("user_id", type=int)
        category_id = request.args.get("category_id", type=int)

        query = Record.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        if category_id:
            query = query.filter_by(category_id=category_id)

        records = query.all()
        record_schema = RecordSchema(many=True)
        records_dumped = record_schema.dump(records)
        return jsonify(records_dumped)
    except Exception as e:
        app.logger.error(f"Error in fetching records: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/account/<int:user_id>", methods=["GET"])
def get_account(user_id):
    try:
        account = Account.query.get(user_id)
        if not account:
            return jsonify({"error": "Account not found"}), 404
        account_schema = AccountSchema()
        account_dumped = account_schema.dump(account)
        return jsonify(account_dumped)
    except Exception as e:
        app.logger.error(f"Error in fetching account: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/account/<int:user_id>/deposit", methods=["POST"])
def deposit(user_id):
    try:

        amount = request.json.get("amount")
        

        if not amount or float(amount) <= 0:
            return jsonify({"error": "Deposit amount must be greater than 0"}), 400
        

        amount = float(amount)
        

        account = Account.query.get(user_id)
        if not account:
            return jsonify({"error": "Account not found"}), 404
        

        account.balance += amount
        db.session.add(account)
        db.session.commit()

        account_schema = AccountSchema()
        account_dumped = account_schema.dump(account)
        return jsonify(account_dumped)
    except Exception as e:
        app.logger.error(f"Error in deposit: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        app.logger.error(f"Healthcheck failed: {str(e)}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
