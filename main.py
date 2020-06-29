from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # disable warnings
app.permanent_session_lifetime = timedelta(minutes=15)

db = SQLAlchemy(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    return render_template("login.html")


if __name__ == "__main__":
    db.create_all()  # create db
    app.run(debug=True)  # debug = True is for debugging.
