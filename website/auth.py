from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from . import db

db = db.db
auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        fields = ["email", "password"]
        form = request.form.to_dict()

        # Check if email and password are given
        if all(field in fields and form[field] for field in form):
            # Get user details from the database
            # 1. returns an object if user exists
            # 2. return nothing (None) if user does not exist
            user = db.Users.find_one(
                {
                    "email": form["email"],
                    "password": form["password"],
                }
            )

            # Check if user exists in the database (if "1" is true)
            if user:
                user["_id"] = str(user["_id"])
                session["user"] = user  # Add user to session
                flash("Successfully logged in!")  # Display success message
                return redirect(url_for("views.home"))  # Redirect to home page

            else:
                # If user not found
                flash("User not found. Please check your email and password.")
        else:
            # If email and password not given
            flash("Please fill all fields")

    return render_template("login.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fields = ["first_name", "last_name", "email", "phone", "password"]
        form = request.form.to_dict()
        if all(field in fields and form[field] for field in form):
            user = db.Users.find_one({"email": form["email"]})
            if not user:
                db.Users.insert_one(form)
                flash("Successfully registered. Please login to continue.")
                return redirect(url_for("auth.login"))
            else:
                flash("Email already exists.")
        else:
            flash("Please fill all fields")
    return render_template("register.html")


@auth.route("/logout")
def logout():
    session.pop("user", None)
    flash("Successfully logged out!")
    return redirect(url_for("auth.login"))
