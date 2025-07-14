from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import logging

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Setup Google Sheets
try:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
    client = gspread.authorize(creds)
    
    contact_sheet = client.open("Contact Leads").worksheet("Contact Form")
    enquiry_sheet = client.open("Contact Leads").worksheet("Enquiry Form")
except Exception as e:
    logging.error(f"[❌ ERROR] Google Sheet connection failed: {e}")
    contact_sheet = None
    enquiry_sheet = None

# Insert row into specific sheet below headers
def insert_row_to_sheet(sheet, values):
    if not sheet:
        return
    try:
        sheet.insert_row(values, index=2)
    except Exception as e:
        logging.error(f"[❌ ERROR] insert_row_to_sheet failed: {e}")

# ROUTES
@app.route("/")
def home():
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
            flash("⚠️ Please fill in all required fields.")
            return redirect(url_for("/contact.html"))

        if contact_sheet:
            try:
                values = [
                    full_name,
                    contact_number,
                    email,
                    message if message else "",
                    timestamp
                ]
                insert_row_to_sheet(contact_sheet, values)
                return redirect(url_for("product"))
            except Exception as e:
                logging.error(f"[❌ ERROR] Could not write contact data: {e}")
                flash("Something went wrong. Try again later.")
                return redirect(url_for("/contact.html"))
        else:
            flash("⚠️ Google Sheet not connected.")
            return redirect(url_for("/contact.html"))

    return render_template("contact.html")

@app.route("/submit-enquiry", methods=["POST"])
def submit_enquiry():
    if not enquiry_sheet:
        return jsonify({"error": "Google Sheet not connected"}), 500

    try:
        data = request.get_json()
        name = data.get("name")
        phone = data.get("phone")
        email = data.get("email")
        product = data.get("product")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        values = [name, phone, email, product, timestamp]
        insert_row_to_sheet(enquiry_sheet, values)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logging.error(f"[❌ ERROR] Could not submit enquiry: {e}")
        return jsonify({"error": "Submission failed"}), 500

if __name__ == "__main__":
    app.run(debug=True)
