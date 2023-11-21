from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from . import db
from bson import ObjectId

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
    return render_template("admin/dashboard.html")


@admin.route("/cars")
def cars():
    return render_template("admin/cars.html")


@admin.route("/bookings")
def bookings():
    return render_template("admin/bookings.html")


@admin.route("/users")
def users():
    users = db.Users.find({})
    return render_template("admin/users.html", users=users)


@admin.route("/manage-user/<user_id>", methods=["GET", "POST"])
def manage_user(user_id):
    user = db.Users.find_one({"_id": ObjectId(user_id)})
    if request.method == "POST":
        form = request.form.to_dict()
        form["roles"] = form["roles"].split(",")
        user = db.Users.find_one_and_update(user, {"$set": form}, return_document=True)
        flash("Details updated!")
    return render_template("admin/users/manage-user.html", user=user)
