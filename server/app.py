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

class Restaurants(Resource):
    def get(self):
        restaurants = [r.to_dict() for r in Restaurant.query.all()]
        return restaurants

class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        return restaurant.to_dict(include_pizzas=True)

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204

class Pizzas(Resource):
    def get(self):
        pizzas = [p.to_dict() for p in Pizza.query.all()]
        return pizzas

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_rp = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(new_rp)
            db.session.commit()
            return new_rp.to_dict(), 201
        except:
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantById, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

if __name__ == "__main__":
    app.run(port=5555, debug=True)

