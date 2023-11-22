from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from . import db
from bson import ObjectId
import base64

db = db.db
admin = Blueprint("admin", __name__)


@admin.before_request
def is_user_admin():
    user = session["user"]  # Get the user from session
    roles = []

    # Check if user  has roles
    if "roles" in user:
        roles = user["roles"]

    # Check if user is admin
    if "admin" not in roles:
        flash("You are not authorized")
        return redirect(url_for("views.home"))


@admin.route("/")
def dashboard():
    collections = [
        {"collection": collection, "documents": db[collection].count_documents({})}
        for collection in db.list_collection_names()
    ]
    return render_template("admin/dashboard.html", collections=collections)


@admin.route("/cars")
def cars():
    cars = db.Cars.find({})
    return render_template("admin/cars.html", cars=cars)


@admin.route("/bookings")
def bookings():
    bookings = db.Bookings.find({})
    return render_template("admin/bookings.html", bookings=bookings)


@admin.route("/users")
def users():
    users = db.Users.find({})
    return render_template("admin/users.html", users=users)


# Add Cars
@admin.route("/cars/add-car", methods=["GET", "POST"])
def add_car():
    if request.method == "POST":
        form = request.form.to_dict()
        image = request.files.get("image")
        form["image"] = convert_img_to_base64(image)
        db.Cars.insert_one(form)
        flash(f'Successfully added {form["brand"]} {form["name"]} to the database')
        return redirect(url_for("admin.cars"))
    return render_template("admin/cars/add-car.html")


# Edit Car
@admin.route("/cars/edit-car/<car_id>", methods=["GET", "POST"])
def edit_car(car_id):
    car = db.Cars.find_one({"_id": ObjectId(car_id)})
    if request.method == "POST":
        form = request.form.to_dict()
        image = request.files.get("image")
        if image:
            form["image"] = convert_img_to_base64(image)
        car = db.Cars.find_one_and_update(car, {"$set": form}, return_document=True)
        flash("Car details updated successfully!")

    return render_template("admin/cars/edit-car.html", car=car)


# Delete Car
@admin.route("/cars/delete-car/<car_id>", methods=["GET", "POST"])
def delete_car(car_id):
    db.Cars.delete_one({"_id": ObjectId(car_id)})
    flash("Car deleted successfully!")
    return redirect(url_for("admin.cars"))


# Edit Users
@admin.route("/users/edit-user/<user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    user = db.Users.find_one({"_id": ObjectId(user_id)})
    if request.method == "POST":
        form = request.form.to_dict()
        form["roles"] = form["roles"].split(",")
        user = db.Users.find_one_and_update(user, {"$set": form}, return_document=True)
        flash("Details updated!")
    return render_template("admin/users/edit-user.html", user=user)


# Delete User
@admin.route("/users/delete-user/<user_id>", methods=["GET", "POST"])
def delete_user(user_id):
    db.Users.delete_one({"_id": ObjectId(user_id)})
    flash("User deleted successfully!")
    return redirect(url_for("admin.users"))


def convert_img_to_base64(image):
    image = image.read()
    image = base64.b64encode(image).decode("utf-8")
    image = f"data:image/*;base64,{image}"
    return image
