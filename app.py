from flask import Flask, render_template, request, redirect, flash
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import logging

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Google Sheets Setup
try:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("Contact Leads").sheet1
except Exception as e:
    logging.error(f"[❌ ERROR] Could not connect to Google Sheet: {e}")
    sheet = None

# Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/index.html")
def index_redirect():
    return render_template("index.html")


@app.route("/about.html")
def about():
    return render_template("about.html")

@app.route("/product.html")
def product():
    return render_template("product.html")

@app.route("/contact.html", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        contact_number = request.form.get("contact")
        email = request.form.get("email")
        message = request.form.get("message", "")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not full_name or not contact_number or not email:
            flash("Please fill in all required fields.")
            return redirect("/contact")

        if sheet:
            try:
                sheet.append_row([full_name, contact_number, email, message, timestamp])
                flash("Your message has been sent successfully! ✅")
                return redirect("/")
            except Exception as e:
                logging.error(f"[❌ ERROR] Could not write to sheet: {e}")
                flash("Something went wrong while saving your data. Please try again later.")
                return redirect("/contact")
        else:
            flash("Sheet not connected. Contact site admin.")
            return redirect("/contact")

    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)
