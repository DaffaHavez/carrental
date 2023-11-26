from flask import Blueprint, render_template, session, abort, request, flash
from . import db
from bson import ObjectId
from datetime import datetime

db = db.db
views = Blueprint("views", __name__)

@views.before_request
def update_booking_status():
    today = datetime.now()
    db.Bookings.update_many(
        {"status": "active", "date_end": {"$lt": today}}, {"$set": {"status": "ended"}}
    )


# Home page
@views.route("/")
def home():
    # Getting list of brans
    brands = db.Cars.distinct("brand")
    # List of some cars
    cars = get_cars([{"$sort": {"model": -1}}, {"$limit": 6}])
    return render_template("home.html", brands=brands, cars=cars)


@views.route("/cars")
def cars():
    brands = db.Cars.distinct("brand")

    brand = request.args.get("brand")
    search = request.args.get("search")
    sort = request.args.get("sort", default="name")
    order = request.args.get("order")

    query = []
    if brand in brands:
        query.append({"brand": brand})
    if search:
        query.append(
            {"$and": [{"name": {"$regex": i, "$options": "i"}} for i in search.split()]}
        )
    order = -1 if order == "desc" else 1
    query = [{"$match": {"$and": query}}] if query else []
    query.append({"$sort": {sort: order}})
    cars = get_cars(query)
    return render_template("cars.html", cars=cars, brands=brands)


@views.route("/cars/<car_id>")
def car_details(car_id):
    car = get_cars([{"$match":{"_id":ObjectId(car_id)}}])[0]
    return render_template("car-details.html", car=car)


@views.route("/about")
def about():
    return render_template("about.html")


@views.route("/contact")
def contact():
    return render_template("contact.html")


def get_cars(filter=[]):
    pipeline = filter + [
        {
            "$lookup": {
                "from": "Bookings",
                "localField": "_id",
                "foreignField": "car_id",
                "pipeline": [{"$match": {"status": "active"}}],
                "as": "bookings",
            }
        },
        {
            "$addFields": {
                "available": {"$subtract": ["$quantity", {"$size": "$bookings"}]}
            }
        },
    ]
    cars = list(db.Cars.aggregate(pipeline))
    return cars

