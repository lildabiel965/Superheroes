#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_migrate import Migrate

from models import db, Hero, Power, HeroPower
import os

# Configure database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)



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
    hero = db.session.get(Hero, id)
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
    power = db.session.get(Power, id)
    if power is None:
        return jsonify({"error": "Power not found"}), 404
    return jsonify(power.to_dict())

# PATCH /powers/:id
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = db.session.get(Power, id)
    if power is None:
        return jsonify({"error": "Power not found"}), 404

    data = request.get_json()
    if 'description' not in data:
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        power.description = data['description']
        db.session.commit()
        return jsonify(power.to_dict())
    except ValueError:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400

# POST /hero_powers
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    required_fields = ['strength', 'hero_id', 'power_id']
    
    if not all(field in data for field in required_fields):
        return jsonify({"errors": ["validation errors"]}), 400

    hero = db.session.get(Hero, data['hero_id'])
    power = db.session.get(Power, data['power_id'])
    if not hero or not power:
        return jsonify({"errors": ["validation errors"]}), 400

    if data['strength'] not in ['Strong', 'Weak', 'Average']:
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        hero_power = HeroPower(
            strength=data['strength'],
            hero_id=data['hero_id'],
            power_id=data['power_id']
        )
        db.session.add(hero_power)
        db.session.commit()
        return jsonify({
            "id": hero_power.id,
            "hero_id": hero_power.hero_id,
            "power_id": hero_power.power_id,
            "strength": hero_power.strength,
            "hero": hero.to_dict(include_powers=False),
            "power": power.to_dict()
        }), 200  # Changed from 201 to 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400

def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()
    app.run(port=5555, debug=True)
