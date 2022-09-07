from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
import os

API_KEY = os.environ.get("API_KEY")
app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# 'Cafe' TABLE CONFIGURATION
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Uses dictionary comprehensions
        # to loop through every column in the data record
        # and create a new dictionary entry
        # where the key is the name of the column
        # and the value is the value of the entry in the column

        dictionary = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return dictionary


# HOMEPAGE
@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
# "GET" method is allowed by default on all routes, no need to specify method in route
@app.route("/random")
def get_random_cafe():
    # Returns random cafe from database as JSON
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    random_cafe_dict = random_cafe.to_dict()
    return jsonify(cafe=random_cafe_dict)


@app.route("/all")
def get_all_cafes():
    # Returns all cafes in database as JSON
    cafes = db.session.query(Cafe).all()
    cafes_dict = [cafe.to_dict() for cafe in cafes]
    return jsonify(cafes=cafes_dict)


@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("location")
    cafes_at_location = Cafe.query.filter_by(location=query_location).all()
    if not cafes_at_location:
        # 404 = Resource not found
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404
    else:
        cafes_dict = [cafe.to_dict() for cafe in cafes_at_location]
        return jsonify(cafes=cafes_dict)


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def post_new_cafe():
    # Adds a new cafe record to the database
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        seats=request.form.get("seats"),
        has_toilet=bool(request.form.get("has_toilet")),
        has_wifi=bool(request.form.get("has_wifi")),
        has_sockets=bool(request.form.get("has_socket")),
        can_take_calls=bool(request.form.get("can_take_calls")),
        coffee_price=request.form.get("coffee_price")
    )
    api_key = request.args.get("api-key")

    if api_key == API_KEY:
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."})
    else:
        # 401 = User unauthorised
        return jsonify(
            error={"Unauthorised": "Sorry, that's not allowed. Make sure you have the correct 'api-key'."}), 401


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = Cafe.query.get(cafe_id)
    api_key = request.args.get("api-key")

    if api_key == API_KEY:
        if cafe and new_price:
            cafe.coffee_price = new_price
            db.session.commit()
            return jsonify(success=f"Successfully updated the price of coffee at {cafe.name}."), 200
        elif not cafe:
            # 404 = Resource not found
            return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."}), 404
            # 400 = Bad request
        elif not new_price:
            return jsonify(error={"Bad Request": "Please input 'new_price' as a parameter."}), 400
    else:
        # 401 = User unauthorised
        return jsonify(
            error={"Unauthorised": "Sorry, that's not allowed. Make sure you have the correct 'api-key'."}), 401


# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    api_key = request.args.get("api-key")

    if api_key == API_KEY:
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(success=f"Successfully removed {cafe.name} from the cafe database."), 200
        else:
            # 404 = Resource not found
            return jsonify(error={"Not Found": "Sorry, a cafe with that id was not found in the database."}), 404
    else:
        # 401 = User unauthorised
        return jsonify(
            error={"Unauthorised": "Sorry, that's not allowed. Make sure you have the correct 'api-key'."}), 401


if __name__ == '__main__':
    app.run(debug=True)
