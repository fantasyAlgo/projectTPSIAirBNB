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

@app.route("/payment", methods=["GET", "POST"])
def payment():
    if request.method == "GET":
        item_id = request.args.get('id')
        item = list(cursor.execute(f"SELECT * FROM Appartments WHERE id = {item_id}"))[0]
        date_format = '%Y-%m-%d'
        checkin = datetime.strptime(request.args.get('checkin'), date_format)
        checkout = datetime.strptime(request.args.get('checkout'), date_format)
        nPeople = request.args.get("people")
        days = (checkout-checkin).days
        return render_template("payment.html", passed_data = [checkin, checkout, nPeople, item], money =  round(days*float(item[2]), 3))
    ### In case of a POST request
    if not "username" in session:
        return redirect(url_for("login"))
    item_id = request.args.get('id')
    date_format = '%Y-%m-%d'
    checkin = datetime.strptime(request.form.get('checkin').split(" ")[0], date_format)
    checkout = datetime.strptime(request.form.get('checkout').split(" ")[0], date_format)
    nPeople = request.form.get("people")
    user_id = list(cursor.execute(f"SELECT * FROM Users WHERE username = 'sk' "))[0]
    result = cursor.execute(f"INSERT INTO Renting (user_id, appartment_id, checkin, checkout, NPeople) VALUES (?, ?, ?, ?, ?)", (user_id, item_id, checkin, checkout, nPeople))
    conn.commit()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)

conn.close()

