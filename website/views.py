from flask import Blueprint, render_template, session, abort, request, flash
from . import db
from bson import ObjectId

db = db.db
views = Blueprint("views", __name__)


@views.route("/")
def home():
    brands = db.Cars.distinct("brand")
    cars = db.Cars.find({}).sort("model", -1).limit(6)
    return render_template("home.html", brands=brands, cars=cars)


@views.route("/cars")
def cars():
    brands = db.Cars.distinct("brand")

    brand = request.args.get("brand")
    search = request.args.get("search")
    sort = request.args.get("sort", default="name")
    order = request.args.get("order")

    query = {}
    if brand in brands:
        query["brand"] = brand
    if search:
        query["$and"] = [
            {"name": {"$regex": i, "$options": "i"}} for i in search.split()
        ]
    order = -1 if order == "desc" else 1

    cars = db.Cars.find(query).sort(sort, order)
    return render_template("cars.html", cars=cars, brands=brands)


@views.route("/cars/<car_id>")
def car_details(car_id):
    car = db.Cars.find_one({"_id": ObjectId(car_id)})
    return render_template("car-details.html", car=car)

@views.route("/about")
def about():
    return render_template("about.html")


@views.route("/contact")
def contact():
    return render_template("contact.html")
