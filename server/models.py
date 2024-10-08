from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    super_name = db.Column(db.String, nullable=False)

    # Relationship
    powers = db.relationship('HeroPower', back_populates='hero', cascade="all, delete-orphan")

    # Serialization rules
    def to_dict(self, include_powers=True):
        data = {
            "id": self.id,
            "name": self.name,
            "super_name": self.super_name
        }
        if include_powers:
            data["hero_powers"] = [hp.to_dict(include_hero=False) for hp in self.powers]
        return data

    def __repr__(self):
        return f'<Hero {self.id}>'

class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    # Relationship
    heroes = db.relationship('HeroPower', back_populates='power', cascade="all, delete-orphan")

    # Serialization rules
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }

    # Validation
    @validates('description')
    def validate_description(self, key, description):
        if len(description) < 20:
            raise ValueError("description must be at least 20 characters long")
        return description

    def __repr__(self):
        return f'<Power {self.id}>'

class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)

    # Relationships
    hero = db.relationship('Hero', back_populates='powers')
    power = db.relationship('Power', back_populates='heroes')

    # Serialization rules
    def to_dict(self, include_hero=True, include_power=True):
        data = {
            "id": self.id,
            "hero_id": self.hero_id,
            "power_id": self.power_id,
            "strength": self.strength
        }
        if include_hero:
            data["hero"] = self.hero.to_dict(include_powers=False)
        if include_power:
            data["power"] = self.power.to_dict()
        return data

    # Validation
    @validates('strength')
    def validate_strength(self, key, strength):
        if strength not in ['Strong', 'Weak', 'Average']:
            raise ValueError("strength must be one of: Strong, Weak, Average")
        return strength

    def __repr__(self):
        return f'<HeroPower {self.id}>'
