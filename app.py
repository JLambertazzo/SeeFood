from flask import Flask, render_template
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort
from flask_sqlalchemy import SQLAlchemy
import uuid
app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

class RestaurantModel(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))

    def __repr__(self):
        return f"Restaurant(name={name}, description={description})"

class ItemModel(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    resturant = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    ingredients = db.Column(db.String(500))
    image = db.Column(db.String(500))
    qr = db.Column(db.String(500))

    def __repr__(self):
        return f"Item(restaurant={restaurant}, name={name}, description={description}, ingredients={ingredients}, image={image}, qr={qr})"


db.create_all()

restaurant_put_args = reqparse.RequestParser()
restaurant_put_args.add_argument("name", required=True, type=str, help='Restaurant name was not included')
restaurant_put_args.add_argument("description", type=str)

restaurant_patch_args = reqparse.RequestParser()
restaurant_patch_args.add_argument("name", type=str)
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
        for arg in args:
            result[arg] = args[arg]
        db.session.commit()
        return result

    @marshal_with(restaurant_fields)
    def delete(self, id):
        result = RestaurantModel.query.filter_by(id=id).first()
        if not result:
            abort(404, message="restaurant not found")
        db.session.remove(result)
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
        result = ItemModel.query.filter_by(id=id)
        if not result:
            abort(404, message="item not found")
        for arg in args:
            result[arg] = args[arg]
        db.session.commit()
        return result

    @marshal_with(item_fields)
    def delete(self, id):
        result = ItemModel.query.filter_by(id=id).first()
        if not result:
            abort(404, message="item not found")
        return result


class NewRestaurant(Resource):
    @marshal_with(restaurant_fields)
    def put(self):
        args = restaurant_put_args.parse_args()
        restaurant = RestaurantModel(id=str(uuid.uuid1()), name=args['name'], description=args['description'])
        db.session.add(restaurant)
        db.session.commit()
        return restaurant, 201

class NewItem(Resource):
    @marshal_with(item_fields)
    def put(self):
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