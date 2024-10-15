#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# GET /heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([hero.to_dict(include_powers=False) for hero in heroes])

# GET /heroes/:id
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = db.session.get(Hero, id)  # Updated line
    if hero is None:
        return jsonify({"error": "Hero not found"}), 404
    return jsonify(hero.to_dict())

# GET /powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([power.to_dict() for power in powers])

# GET /powers/:id
@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = db.session.get(Power, id)  # Updated line
    if power is None:
        return jsonify({"error": "Power not found"}), 404
    return jsonify(power.to_dict())

# PATCH /powers/:id
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = db.session.get(Power, id)  # Updated line
    if power is None:
        return jsonify({"error": "Power not found"}), 404

    data = request.get_json()
    if 'description' in data:
        if not isinstance(data['description'], str) or len(data['description']) < 20:
            return jsonify({"errors": ["validation errors"]}), 400  # Changed here
        power.description = data['description']
        db.session.commit()
        return jsonify(power.to_dict()), 200

    return jsonify({"error": "No valid fields provided"}), 400

# POST /hero_powers
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()

    # Validate the strength field
    valid_strengths = ['Strong', 'Weak', 'Average']
    strength = data.get('strength')

    if strength not in valid_strengths:
        return jsonify({"errors": ["validation errors"]}), 400  # Match the expected error response

    try:
        new_hero_power = HeroPower(
            strength=strength,
            hero_id=data['hero_id'],
            power_id=data['power_id']
        )
        db.session.add(new_hero_power)
        db.session.commit()
        return jsonify(new_hero_power.to_dict()), 200  # Resource created
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400
    except Exception as e:
        return jsonify({"errors": ["An unexpected error occurred."]}), 500

if __name__ == '__main__':
    app.run(port=5555, debug=True)
