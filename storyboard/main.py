from datetime import date, datetime
from sqlite3.dbapi2 import Error
from flask import Flask, json, render_template, render_template_string, request, session, url_for, redirect
import sqlite3
import hashlib


app = Flask(__name__)
app.secret_key = hashlib.md5("banana".encode()).hexdigest()[:10]


conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

@app.route('/')
def home():
    lst = list(cursor.execute("SELECT * FROM Appartments"))
    if "username" in session:
        return render_template('index.html', content=lst, isLogged=True)
    return render_template('index.html', content=lst, isLogged=False)

@app.route("/page")
def page():
    item_id = request.args.get('id')
    item = list(cursor.execute(f"SELECT * FROM Appartments WHERE id = {item_id}"))[0]
    print(item)
    return render_template('page.html', item = item)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error = "")
    data = request.form.get("username"), request.form.get("email"), request.form.get("password")
    hashed_password = hashlib.md5(data[2].encode()).hexdigest()[:10]
    result = list(cursor.execute("SELECT password FROM Users WHERE email = ?", (data[1],)))[0][0]
    print(result, hashed_password)
    if result == hashed_password:
        session["username"] = data[0]
        return redirect(url_for("home"))
    return render_template("login.html", error = "Wrong password or email")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    data = request.form.get("username"), request.form.get("email"), request.form.get("password")
    hashed_password = hashlib.md5(data[2].encode()).hexdigest()[:10]
    result = cursor.execute("INSERT INTO Users (username, email, password) VALUES (?, ?, ?)", (data[0], data[1], hashed_password))
    conn.commit()
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

@app.route("/payment")
def payment():
    if request.method == "GET":
        date_format = '%Y-%m-%d'
        checkin = datetime.strptime(request.args.get('checkin'), date_format)
        checkout = datetime.strptime(request.args.get('checkout'), date_format)
        print(checkin, checkout, checkout-checkin)
        return render_template("payment.html")


if __name__ == '__main__':
    app.run(debug=True)

conn.close()

