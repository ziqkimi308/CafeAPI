"""
********************************************************************************
* Project Name:  CafeAPI
* Description:   The CafeAPI is a RESTful API designed to manage a database of cafes. It allows users to retrieve information about cafes, add new cafes, update existing information, and delete cafes based on specific conditions.
* Author:        ziqkimi308
* Created:       2025-01-19
* Updated:       2025-01-19
* Version:       1.0
********************************************************************************
"""

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

# --- CHANGE API KEY HERE ---
API_KEY = "TopSecretAPIKey"

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
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
		return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# Routes
@app.route("/")
def home():
	return render_template("index.html")

@app.route("/random")
def get_random_cafe():
	cafes = db.session.query(Cafe).all() # Get all cafes in database
	random_cafe = random.choice(cafes)
	return jsonify(cafe=random_cafe.to_dict())

@app.route("/all")
def get_all_cafes():
	cafes = db.session.query(Cafe).all()
	return jsonify(cafes=[cafe.to_dict() for cafe in cafes])

@app.route("/search")
def get_cafe_by_location():
	location = request.args.get("loc")
	cafe = db.session.query(Cafe).filter_by(location=location).first() # return first result of query
	if cafe:
		return jsonify(cafe=cafe.to_dict())
	else:
		return jsonify(error={"Not Found":"Sorry, we don't have a cafe at that location."})

@app.route("/add", methods=["POST"])
def post_new_cafe():
	new_cafe = Cafe(
		name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price")
	)
	db.session.add(new_cafe)
	db.session.commit()
	return jsonify(response={"Success": "New cafe successfully added!"})

@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_coffee_price(cafe_id):
	cafe_to_update = db.session.query(Cafe).get(cafe_id)
	if cafe_to_update:
		cafe_to_update.coffee_price = request.args.get("new_price") # Use request.args.get() because the PATCH was from params not body from P
		db.session.commit()
		return jsonify(success={"Success": f"Coffee price for cafe id {cafe_id} updated!"}), 200
	else:
		return jsonify(error={"Not Found":"Sorry, a cafe with that id was not found in the database."}), 404

@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
	cafe_to_delete = db.session.query(Cafe).get(cafe_id)
	if cafe_to_delete:
		api_key = request.args.get("api-key")
		if api_key == API_KEY: 
			db.session.delete(cafe_to_delete)
			db.session.commit()
			return jsonify(success={"success": f"Cafe with id {cafe_id} successfully deleted!"}), 200
		else:
			return jsonify(error={"error": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403
	else: 
		return jsonify(error={"Not Found":"Sorry, a cafe with that id was not found in the database."}), 404

if __name__ == '__main__':
	app.run(debug=True)
