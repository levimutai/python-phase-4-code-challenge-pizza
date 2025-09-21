#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants')
def get_restaurants():
    restaurants = Restaurant.query.all()
    return [restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants]

@app.route('/restaurants/<int:id>')
def get_restaurant(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()
    if restaurant:
        return restaurant.to_dict(only=('id', 'name', 'address', 'restaurant_pizzas.id', 'restaurant_pizzas.price', 'restaurant_pizzas.pizza_id', 'restaurant_pizzas.restaurant_id', 'restaurant_pizzas.pizza.id', 'restaurant_pizzas.pizza.name', 'restaurant_pizzas.pizza.ingredients'))
    return {'error': 'Restaurant not found'}, 404

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    return {'error': 'Restaurant not found'}, 404

@app.route('/pizzas')
def get_pizzas():
    pizzas = Pizza.query.all()
    return [pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas]

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    try:
        data = request.get_json()
        restaurant_pizza = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(restaurant_pizza)
        db.session.commit()
        return restaurant_pizza.to_dict(only=('id', 'price', 'pizza_id', 'restaurant_id', 'pizza.id', 'pizza.name', 'pizza.ingredients', 'restaurant.id', 'restaurant.name', 'restaurant.address')), 201
    except ValueError as e:
        return {'errors': [str(e)]}, 400
    except Exception as e:
        return {'errors': ['validation errors']}, 400


if __name__ == "__main__":
    app.run(port=5555, debug=True)
