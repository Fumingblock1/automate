import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from database import init_db, get_db
import requests
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "automate_secret_key_2025"

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

with app.app_context():
    init_db()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def ai_query(prompt):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/free",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
        result = response.json()
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        return "AI service unavailable right now."
    except Exception as e:
        return f"Error: {str(e)}"

# ── PUBLIC ROUTES ──────────────────────────
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/customer/calculator")
def customer_calculator():
    return render_template("calculator.html", customer=True)

@app.route("/customer/recommender")
def customer_recommender():
    return render_template("recommender.html", customer=True)

@app.route("/customer/finance")
def customer_finance():
    return render_template("finance.html", customer=True)

@app.route("/customer/compare")
def customer_compare():
    return render_template("compare.html", customer=True)

@app.route("/customer/chatbot")
def customer_chatbot():
    return render_template("chatbot.html", customer=True)

@app.route("/customer/book")
def customer_book():
    return render_template("customer_book.html")

@app.route("/customer/book/submit", methods=["POST"])
def customer_book_submit():
    db = get_db()
    db.execute("INSERT INTO bookings (name, email, phone, car_interest, date, time, status) VALUES (?,?,?,?,?,?,?)",
        (request.form["name"], request.form["email"], request.form["phone"],
         request.form["car_interest"], request.form["date"], request.form["time"], "pending"))
    db.commit()
    db.close()
    flash("Test drive booked! We will confirm shortly.")
    return redirect(url_for("customer_book"))

# ── LOGIN ──────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            flash("Incorrect password!")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ── ADMIN ROUTES ───────────────────────────
@app.route("/admin")
@login_required
def index():
    db = get_db()
    total_cars = db.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
    available_cars = db.execute("SELECT COUNT(*) FROM inventory WHERE status='available'").fetchone()[0]
    total_leads = db.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    new_leads = db.execute("SELECT COUNT(*) FROM leads WHERE status='new'").fetchone()[0]
    total_bookings = db.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    pending_bookings = db.execute("SELECT COUNT(*) FROM bookings WHERE status='pending'").fetchone()[0]
    recent_leads = db.execute("SELECT * FROM leads ORDER BY date_added DESC LIMIT 5").fetchall()
    recent_bookings = db.execute("SELECT * FROM bookings ORDER BY date_added DESC LIMIT 5").fetchall()
    db.close()
    return render_template("index.html",
        total_cars=total_cars, available_cars=available_cars,
        total_leads=total_leads, new_leads=new_leads,
        total_bookings=total_bookings, pending_bookings=pending_bookings,
        recent_leads=recent_leads, recent_bookings=recent_bookings)

@app.route("/inventory")
@login_required
def inventory():
    db = get_db()
    cars = db.execute("SELECT * FROM inventory ORDER BY date_added DESC").fetchall()
    db.close()
    return render_template("inventory.html", cars=cars)

@app.route("/inventory/add", methods=["POST"])
@login_required
def add_car():
    db = get_db()
    db.execute("INSERT INTO inventory (make, model, year, price, mileage, color, status, description) VALUES (?,?,?,?,?,?,?,?)",
        (request.form["make"], request.form["model"], request.form["year"],
         request.form["price"], request.form["mileage"], request.form["color"],
         request.form["status"], request.form["description"]))
    db.commit()
    db.close()
    flash("Car added successfully!")
    return redirect(url_for("inventory"))

@app.route("/inventory/delete/<int:id>")
@login_required
def delete_car(id):
    db = get_db()
    db.execute("DELETE FROM inventory WHERE id=?", (id,))
    db.commit()
    db.close()
    flash("Car removed!")
    return redirect(url_for("inventory"))

@app.route("/leads")
@login_required
def leads():
    db = get_db()
    all_leads = db.execute("SELECT * FROM leads ORDER BY date_added DESC").fetchall()
    db.close()
    return render_template("leads.html", leads=all_leads)

@app.route("/leads/add", methods=["POST"])
@login_required
def add_lead():
    db = get_db()
    db.execute("INSERT INTO leads (name, email, phone, interest, budget, status, notes, follow_up) VALUES (?,?,?,?,?,?,?,?)",
        (request.form["name"], request.form["email"], request.form["phone"],
         request.form["interest"], request.form["budget"], request.form["status"],
         request.form["notes"], request.form["follow_up"]))
    db.commit()
    db.close()
    flash("Lead added!")
    return redirect(url_for("leads"))

@app.route("/leads/delete/<int:id>")
@login_required
def delete_lead(id):
    db = get_db()
    db.execute("DELETE FROM leads WHERE id=?", (id,))
    db.commit()
    db.close()
    flash("Lead removed!")
    return redirect(url_for("leads"))

@app.route("/bookings")
@login_required
def bookings():
    db = get_db()
    all_bookings = db.execute("SELECT * FROM bookings ORDER BY date DESC").fetchall()
    db.close()
    return render_template("bookings.html", bookings=all_bookings)

@app.route("/bookings/add", methods=["POST"])
@login_required
def add_booking():
    db = get_db()
    db.execute("INSERT INTO bookings (name, email, phone, car_interest, date, time, status) VALUES (?,?,?,?,?,?,?)",
        (request.form["name"], request.form["email"], request.form["phone"],
         request.form["car_interest"], request.form["date"], request.form["time"], "pending"))
    db.commit()
    db.close()
    flash("Test drive booked!")
    return redirect(url_for("bookings"))

@app.route("/bookings/delete/<int:id>")
@login_required
def delete_booking(id):
    db = get_db()
    db.execute("DELETE FROM bookings WHERE id=?", (id,))
    db.commit()
    db.close()
    flash("Booking removed!")
    return redirect(url_for("bookings"))

@app.route("/estimator")
@login_required
def estimator():
    return render_template("estimator.html")

@app.route("/estimator/calculate", methods=["POST"])
@login_required
def calculate_value():
    data = request.get_json()
    prompt = f"""You are a car valuation expert. Estimate the market value of this car:
Make: {data['make']}, Model: {data['model']}, Year: {data['year']}, Mileage: {data['mileage']} miles, Condition: {data['condition']}

## Estimated Value
Give a realistic price range in USD.

## Value Factors
What affects this car's value most?

## Best Selling Tips
3 tips to get the best price for this car."""
    result = ai_query(prompt)
    return jsonify({"result": result})

@app.route("/compare")
@login_required
def compare():
    return render_template("compare.html")

@app.route("/compare/analyze", methods=["POST"])
def analyze_compare():
    data = request.get_json()
    prompt = f"""Compare these two cars:
Car 1: {data['car1_year']} {data['car1_make']} {data['car1_model']} - ${data['car1_price']}
Car 2: {data['car2_year']} {data['car2_make']} {data['car2_model']} - ${data['car2_price']}

## Side by Side Comparison
## Pros and Cons
## Verdict"""
    result = ai_query(prompt)
    return jsonify({"result": result})

@app.route("/calculator")
@login_required
def calculator():
    return render_template("calculator.html")

@app.route("/recommender")
@login_required
def recommender():
    return render_template("recommender.html")

@app.route("/recommender/suggest", methods=["POST"])
def suggest_car():
    data = request.get_json()
    prompt = f"""Recommend the perfect car for this customer:
Budget: ${data['budget']}, Lifestyle: {data['lifestyle']}, Use: {data['use']}, Family: {data['family']}, Must Haves: {data['must_haves']}

## Top 3 Recommendations
## What To Look For
## Budget Advice"""
    result = ai_query(prompt)
    return jsonify({"result": result})

@app.route("/finance")
@login_required
def finance():
    return render_template("finance.html")

@app.route("/finance/check", methods=["POST"])
def check_finance():
    data = request.get_json()
    prompt = f"""Assess car finance eligibility:
Car Price: ${data['price']}, Income: ${data['income']}, Credit: {data['credit']}, Deposit: ${data['deposit']}, Employment: {data['employment']}

## Finance Eligibility
## Estimated Monthly Payments
## Best Finance Options
## Tips To Improve Chances"""
    result = ai_query(prompt)
    return jsonify({"result": result})

@app.route("/chatbot")
@login_required
def chatbot():
    return render_template("chatbot.html")

@app.route("/chatbot/message", methods=["POST"])
def chatbot_message():
    data = request.get_json()
    history = data.get("history", [])
    message = data.get("message", "")
    messages = [
        {"role": "system", "content": "You are AutoMate, a friendly car sales assistant. Help customers with questions about cars, financing, test drives, and anything automotive. Be helpful and professional. Keep responses concise."}
    ]
    for h in history:
        messages.append(h)
    messages.append({"role": "user", "content": message})
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={"model": "openrouter/free", "messages": messages}
        )
        result = response.json()
        if "choices" in result:
            return jsonify({"result": result["choices"][0]["message"]["content"]})
        return jsonify({"result": "Sorry I could not process that."})
    except Exception as e:
        return jsonify({"result": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)