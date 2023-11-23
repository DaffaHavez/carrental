from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from . import db
from bson import ObjectId
from datetime import datetime

db = db.db
account = Blueprint("account", __name__)


@account.before_request
def is_user_logged_in():
    if "user" not in session:
        flash("Please login")
        return redirect(url_for("auth.login"))


@account.route("/rentcar/<car_id>", methods=["POST"])
def rent_car(car_id):
    car = db.Cars.find_one({"_id": ObjectId(car_id)})
    form = request.form.to_dict()
    date_format = "%Y-%m-%d"
    form["date_start"] = datetime.strptime(form["date_start"], date_format)
    form["date_end"] = datetime.strptime(form["date_end"], date_format)
    days = (form["date_end"] - form["date_start"]).days
    form["car_id"] = ObjectId(car_id)
    form["user_id"] = ObjectId(session["user"]["_id"])
    form["days"] = days
    form["total_price"] = car["price"] * days
    form["status"] = "pending"
    db.Bookings.insert_one(form)
    flash("Successfully placed an order. Please wait for confirmation.")
    return redirect(url_for("account.bookings"))


@account.route("/bookings")
def bookings():
    pipeline = [
        {
            "$lookup": {
                "from": "Cars",
                "localField": "car_id",
                "foreignField": "_id",
                "as": "car",
            }
        },
        {"$sort": {"_id": -1}},
    ]
    bookings = db.Bookings.aggregate(pipeline)
    return render_template("bookings.html", bookings=bookings)


@account.route("/manage", methods=["GET", "POST"])
def manage():
    if request.method == "POST":
        form = request.form.to_dict()
        if "roles" not in form:
            user_id = ObjectId(session["user"]["_id"])
            user = db.Users.find_one({"_id": {"$ne": user_id}, "email": form["email"]})
            if not user:
                if not form["password"]:
                    form.pop("password")
                user = db.Users.find_one_and_update(
                    {"_id": user_id},
                    {"$set": form},
                    return_document=True,
                )
                user["_id"] = str(user["_id"])
                session["user"] = user
                flash("Account details updated!")
            else:
                flash("Email already exists.")

    return render_template("account.html")
