from flask import Flask, render_template, redirect, session, Response, send_file
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.utils import secure_filename
import werkzeug
import uuid
import hashlib
import os
import qrcode
import PIL
import io
import requests
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'TEMPORARYSECRET'
local = True
Base = None

dbpass = os.environ.get('DBPASS')
if local:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    db = SQLAlchemy(app)
    Base = db.Model
    Column = db.Column
    String = db.String
else:
    Base = declarative_base()
    engine = create_engine(f"cockroachdb://julien:{dbpass}@free-tier.gcp-us-central1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&sslrootcert=cert/cc-ca.crt&options=--cluster=good-bat-867", echo=True)

class RestaurantModel(Base):
    __tablename__ = 'Restaurants'
    id = Column(String(100), primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    description = Column(String(500))

    def __repr__(self):
        return f"Restaurant(name={self.name}, description={self.description})"

class ItemModel(Base):
    __tablename__ = 'Items'
    id = Column(String(100), primary_key=True)
    restaurant = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    ingredients = Column(String(500))
    image = Column(String(500))
    qr = Column(String(500))

    def __repr__(self):
        return f"Item(restaurant={self.restaurant}, name={self.name}, description={self.description}, ingredients={self.ingredients}, image={self.image}, qr={self.qr})"

class ImageModel(Base):
    __tablename__ = 'Images'
    id = Column(String(100), primary_key=True)
    image = Column(String(500), unique=True)
    mimetype = Column(String(500), nullable=False)
    name = Column(String(500), nullable=False)

    def __repr__(self):
        return self.name

if local:
    db.create_all()
else:
    Base.metadata.create_all(engine)

restaurant_post_args = reqparse.RequestParser()
restaurant_post_args.add_argument("name", required=True, type=str, help="Restaurant name was not included")
restaurant_post_args.add_argument("password", required=True, type=str, help="Password was not included")
restaurant_post_args.add_argument("description", type=str)

restaurant_patch_args = reqparse.RequestParser()
restaurant_patch_args.add_argument("name", type=str)
restaurant_patch_args.add_argument("password", type=str)
restaurant_patch_args.add_argument("description", type=str)

item_post_args = reqparse.RequestParser()
item_post_args.add_argument("restaurant", required=True, type=str, help='Restaurant id was not included')
item_post_args.add_argument("name", required=True, type=str, help='Item name was not included')
item_post_args.add_argument("description", type=str)
item_post_args.add_argument("ingredients", type=str)
item_post_args.add_argument("image", type=werkzeug.datastructures.FileStorage, location='files')
item_post_args.add_argument("qr", type=str)

item_patch_args = reqparse.RequestParser()
item_patch_args.add_argument("name", type=str)
item_patch_args.add_argument("description", type=str)
item_patch_args.add_argument("ingredients", type=str)
item_patch_args.add_argument("image", type=werkzeug.datastructures.FileStorage, location='files')
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
        image = args['image']
        if args['image']:
            filename = secure_filename(args['image'].filename)
            mimetype = args['image'].mimetype
            image = args['image'].read()
            img = ImageModel(image=image, mimetype=mimetype, name=filename)
        if args['name']:
            result.name = args['name']
        if args['description']:
            result.description = args['description']
        if args['ingredients']:
            result.ingredients = args['ingredients']
        if image:
            result.image = image
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
    @marshal_with(restaurant_fields)
    def post(self):
        args = restaurant_post_args.parse_args()
        found = RestaurantModel.query.filter_by(name=args['name']).first()
        if found:
            abort(409, message="Restaurant witht this name already exists")
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', args['password'].encode('utf-8'), salt, 100000)
        restaurant = RestaurantModel(id=str(uuid.uuid1()), name=args['name'], password=salt + key, description=args['description'])
        db.session.add(restaurant)
        db.session.commit()
        session['name'] = args['name']
        return restaurant, 201

    # handle login
    @marshal_with(restaurant_fields)
    def get(self):
        args = restaurant_post_args.parse_args()
        found = RestaurantModel.query.filter_by(name=args['name']).first()
        if not found:
            abort(404, message="restaurant not found")
        found_salt = found.password[:32]
        found_key = found.password[32:]
        given_hash = hashlib.pbkdf2_hmac('sha256', args['password'].encode('utf-8'), found_salt, 100000)
        if given_hash == found_key:
            session['name'] = args['name']
            return found
        else:
            abort(403, message="Login Failed") 


class NewItem(Resource):
    @marshal_with(item_fields)
    def post(self):
        args = item_post_args.parse_args()
        found = ItemModel.query.filter_by(restaurant=args['restaurant'], name=args['name']).first()
        if found:
            abort(409, message="You already have an item with this name")
        print('args:' + str(args))
        iid = None
        if args['image']:
            filename = secure_filename(args['image'].filename)
            mimetype = args['image'].mimetype
            iid = str(uuid.uuid1())
            newimage = ImageModel(id=iid, image=args['image'].read(), mimetype=mimetype, name=filename)
            db.session.add(newimage)
        else:
            print('no image given')

        item = ItemModel(id=str(uuid.uuid1()), restaurant=args['restaurant'], name=args['name'], description=args['description'],
        ingredients=args['ingredients'], image=iid, qr=args['qr'])
        print('new item:' + item.id)
        db.session.add(item)
        db.session.commit()
        return item, 201


class Search(Resource):
    @marshal_with(item_fields)
    def get(self, query):
        results = []
        name_matches = ItemModel.query.filter_by(name=query).first()
        desc_matches = ItemModel.query.filter_by(description=query).first()
        ingr_matches = ItemModel.query.filter_by(ingredients=query).first()
        if name_matches:
            return name_matches
        elif desc_matches:
            return desc_matches
        elif ingr_matches:
            return ingr_matches
        else:
            return abort(404, message="no resource found")

class Image(Resource):
    def get(self, id):
        found = ImageModel.query.filter_by(id=id).first()
        if not found:
            abort(404, message="image could not be found")
        return Response(found.image, mimetype=found.mimetype)

class QR(Resource):
    def get(self, id):
        img = qrcode.make(f"http://localhost:5000/viewitem/{id}")
        print(type(img))
        image = img.get_image()
        output = io.BytesIO()
        image.convert('RGBA').save(output, format='PNG')
        output.seek(0, 0)

        return Response(output, mimetype="image/png")
        
        

api.add_resource(NewRestaurant, '/api/restaurants')
api.add_resource(NewItem, '/api/item')
api.add_resource(Restaurants, '/api/restaurants/<string:id>')
api.add_resource(Items, '/api/item/<string:id>')
api.add_resource(Search, '/api/search/<string:query>')
api.add_resource(Image, '/api/image/<string:id>')
api.add_resource(QR, '/api/qr/<string:id>')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if not session['name']:
        return redirect('/', 301)
    found = RestaurantModel.query.filter_by(name=session['name']).first()
    items = ItemModel.query.filter_by(restaurant=found.id).all()
    return render_template('dashboard.html', name=found.name, description=found.description, items=items)

@app.route('/newitem')
def newitempage():
    if not session['name']:
        return redirect('/', 301)
    found = RestaurantModel.query.filter_by(name=session['name']).first()
    return render_template('newitem.html', rest_id=found.id)

@app.route('/viewitem/<string:id>')
def viewitempage(id):
    found = ItemModel.query.filter_by(id=id).first()
    if not session or not session['name']:
        return redirect('/', 301)
    rest = RestaurantModel.query.filter_by(name=session['name']).first()
    if rest.id != found.restaurant:
        abort(409, message="This item belongs to another restaurant")
    if not found:
        abort(404, message="Item was not found")
    image = ImageModel.query.filter_by(id=found.image).first()
    if not image:
        abort(404, message="Error loading image")
    return render_template('viewitem.html', mimetype=image.mimetype, image=f"/api/image/{image.id}", qr=f"/api/qr/{id}", name=found.name, description=found.description, ingredients=found.ingredients)

@app.route('/edititem/<string:id>')
def edititempage(id):
    found = ItemModel.query.filter_by(id=id).first()
    if not session or not session['name']:
        return redirect('/', 301)
    rest = RestaurantModel.query.filter_by(name=session['name']).first()
    if rest.id != found.restaurant:
        abort(409, message="This item belongs to another restaurant")
    if not found:
        abort(404, message="Item was not found")
    return render_template('edititem.html', id=found.id, name=found.name, description=found.description, ingredients=found.ingredients)

@app.route('/search')
def searchpage():
    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=False)