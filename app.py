from flask import Flask, render_template, redirect, session
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort
from flask_sqlalchemy import SQLAlchemy
import uuid
import hashlib
import os
app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SECRET_KEY'] = 'TEMPORARYSECRET'
db = SQLAlchemy(app)

class RestaurantModel(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))

    def __repr__(self):
        return f"Restaurant(name={self.name}, description={self.description})"

class ItemModel(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    restaurant = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    ingredients = db.Column(db.String(500))
    image = db.Column(db.String(500))
    qr = db.Column(db.String(500))

    def __repr__(self):
        return f"Item(restaurant={self.restaurant}, name={self.name}, description={self.description}, ingredients={self.ingredients}, image={self.image}, qr={self.qr})"


db.create_all()

restaurant_put_args = reqparse.RequestParser()
restaurant_put_args.add_argument("name", required=True, type=str, help="Restaurant name was not included")
restaurant_put_args.add_argument("password", required=True, type=str, help="Password was not included")
restaurant_put_args.add_argument("description", type=str)

restaurant_patch_args = reqparse.RequestParser()
restaurant_patch_args.add_argument("name", type=str)
restaurant_patch_args.add_argument("password", type=str)
restaurant_patch_args.add_argument("description", type=str)

item_put_args = reqparse.RequestParser()
item_put_args.add_argument("restaurant", required=True, type=str, help='Restaurant id was not included')
item_put_args.add_argument("name", required=True, type=str, help='Item name was not included')
item_put_args.add_argument("description", type=str)
item_put_args.add_argument("ingredients", type=str)
item_put_args.add_argument("image", type=str)
item_put_args.add_argument("qr", type=str)

item_patch_args = reqparse.RequestParser()
item_patch_args.add_argument("restaurant", type=str)
item_patch_args.add_argument("name", type=str)
item_patch_args.add_argument("description", type=str)
item_patch_args.add_argument("ingredients", type=str)
item_patch_args.add_argument("image", type=str)
item_patch_args.add_argument("qr", type=str)

restaurant_fields = {
    'id': fields.String,
    'name': fields.String,
    'password': fields.String,
    'description': fields.String
}

item_fields = {
    'id': fields.String,
    'restaurant': fields.String,
    'name': fields.String,
    'description': fields.String,
    'ingredients': fields.String,
    'image': fields.String,
    'qr': fields.String
}

class Restaurants(Resource):
    @marshal_with(restaurant_fields)
    def get(self, id):
        result = RestaurantModel.query.filter_by(id=id).first()
        if not result:
            abort(404, message="restaurant not found")
        return result

    @marshal_with(restaurant_fields)
    def patch(self, id):
        args = restaurant_patch_args.parse_args()
        result = RestaurantModel.query.filter_by(id=id).first()
        if not result:
            abort(404, message="restaurant not found")
        if args['name']:
            result.name = args['name']
        if args['password']:
            salt = os.urandom(32)
            key = hashlib.pbkdf2_hmac('sha256', args['password'].encode('utf-8'), salt, 100000)
            result.password = salt + key
        if args['description']:
            result.description = args['description']
        db.session.commit()
        return result

    @marshal_with(restaurant_fields)
    def delete(self, id):
        result = RestaurantModel.query.filter_by(id=id).first()
        if not result:
            abort(404, message="restaurant not found")
        db.session.delete(result)
        db.session.commit()
        return result
        

class Items(Resource):
    @marshal_with(item_fields)
    def get(self, id):
        result = ItemModel.query.filter_by(id=id).first()
        if not result:
            abort(404, message="item not found")
        return result

    @marshal_with(item_fields)
    def patch(self, id):
        args = item_patch_args.parse_args()
        result = ItemModel.query.filter_by(id=id).first()
        if not result:
            abort(404, message="item not found")
        if args['name']:
            result.name = args['name']
        if args['description']:
            result.description = args['description']
        if args['ingredients']:
            result.ingredients = args['ingredients']
        if args['image']:
            result.image = args['image']
        db.session.commit()
        return result

    @marshal_with(item_fields)
    def delete(self, id):
        result = ItemModel.query.filter_by(id=id).first()
        if not result:
            abort(404, message="item not found")
        db.session.delete(result)
        db.session.commit()
        return result


class NewRestaurant(Resource):
    def post(self):
        args = restaurant_put_args.parse_args()
        found = RestaurantModel.query.filter_by(name=args['name']).first()
        if found:
            abort(409, message="Restaurant witht this name already exists")
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', args['password'].encode('utf-8'), salt, 100000)
        restaurant = RestaurantModel(id=str(uuid.uuid1()), name=args['name'], password=salt + key, description=args['description'])
        db.session.add(restaurant)
        db.session.commit()
        session['name'] = args['name']
        return redirect("/dashboard", 301)

    # handle login
    def get(self):
        args = restaurant_put_args.parse_args()
        found = RestaurantModel.query.filter_by(name=args['name']).first()
        if not found:
            abort(404, message="restaurant not found")
        found_salt = found.password[:32]
        found_key = found.password[32:]
        given_hash = hashlib.pbkdf2_hmac('sha256', args['password'].encode('utf-8'), found_salt, 100000)
        if given_hash == found_key:
            session['name'] = args['name']
            return redirect("/dashboard", 301)
        else:
            abort(403, message="Login Failed") 


class NewItem(Resource):
    @marshal_with(item_fields)
    def post(self):
        args = item_put_args.parse_args()
        item = ItemModel(id=str(uuid.uuid1()), restaurant=args['restaurant'], name=args['name'], description=args['description'],
        ingredients=args['ingredients'], image=args['image'], qr=args['qr'])
        db.session.add(item)
        db.session.commit()
        return item, 201

api.add_resource(NewRestaurant, '/api/restaurants')
api.add_resource(NewItem, '/api/item')
api.add_resource(Restaurants, '/api/restaurants/<string:id>')
api.add_resource(Items, '/api/item/<string:id>')

@app.route('/')
def hello():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)