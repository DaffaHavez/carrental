from flask import Blueprint, render_template, session, abort, request, flash
from . import db
from bson import ObjectId

db = db.db
account = Blueprint("account", __name__)


@account.route("/manage", methods=["GET", "POST"])
def manage():
    if "user" not in session:
        abort(404)

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
