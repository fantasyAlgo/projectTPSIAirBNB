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
    if "user_id" in session:
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
    result = list(cursor.execute("SELECT * FROM Users WHERE email = ?", (data[1],)))[0]
    password = result[3]
    print(result, hashed_password)
    if password == hashed_password:
        session["user_id"] = result[0]
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
    session.pop("user_id", None)
    return redirect(url_for("home"))

def checkAvailable(checkin, checkout):
    query = """
        SELECT * FROM Renting 
        WHERE (checkin BETWEEN ? AND ?)
           OR (checkout BETWEEN ? AND ?)
           OR (? BETWEEN checkin AND checkout)
           OR (? BETWEEN checkin AND checkout);
    """
    cursor.execute(query, (checkin, checkout, checkin, checkout, checkin, checkout))
    overlapping_reservations = cursor.fetchall()
    if len(overlapping_reservations) < 3:
        return True 
    return False

@app.route("/payment", methods=["GET", "POST"])
def payment():
    if request.method == "GET":
        if not "user_id" in session or session["user_id"] == None:
            return redirect(url_for("login"))
        item_id = request.args.get('id')
        item = list(cursor.execute(f"SELECT * FROM Appartments WHERE id = {item_id}"))[0]
        date_format = '%Y-%m-%d'
        checkin = datetime.strptime(request.args.get('checkin'), date_format)
        checkout = datetime.strptime(request.args.get('checkout'), date_format)
        nPeople = request.args.get("people")
        days = (checkout-checkin).days
        return render_template("payment.html", passed_data = [checkin, checkout, nPeople, item_id], money =  round(days*float(item[2]), 3))
    ### In case of a POST request
    if not "user_id" in session or session["user_id"] == None:
        return redirect(url_for("login"))
    date_format = '%Y-%m-%d'
    checkin = datetime.strptime(request.form.get('checkin').split(" ")[0], date_format)
    checkout = datetime.strptime(request.form.get('checkout').split(" ")[0], date_format)
    if not checkAvailable(checkin, checkout):
        return redirect(url_for("paymentError"))
    item_id = request.form.get('id')
    print("item_id: ", item_id)
    nPeople = request.form.get("people")
    user_id = session["user_id"]
    print(user_id, item_id)
    result = cursor.execute(f"INSERT INTO Renting (user_id, appartment_id, checkin, checkout, NPeople) VALUES (?, ?, ?, ?, ?)", 
                            (user_id, item_id, checkin, checkout, nPeople))
    conn.commit()
    return redirect(url_for("paymentDone"))

@app.route("/paymentError", methods=["GET"])
def paymentError():
    return render_template("paymentError.html")

@app.route("/paymentDone", methods=["GET"])
def paymentDone():
    return render_template("paymentDone.html")

@app.route("/bookings")
def bookings():
    query = f"SELECT link_img, title, checkin, checkout, NPeople FROM Renting INNER JOIN Appartments ON Renting.appartment_id = Appartments.id WHERE Renting.user_id = {session["user_id"]}"
    items = list(cursor.execute(query))
    print(items)
    return render_template("bookings.html", items=items)


if __name__ == '__main__':
    app.run(debug=True)

conn.close()

