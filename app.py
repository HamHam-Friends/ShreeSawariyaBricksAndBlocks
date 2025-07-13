from flask import Flask, render_template, request, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

# Google Sheets API setup
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Contact Leads").sheet1  # Make sure this name matches your sheet

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        full_name = request.form['full_name']
        contact_number = request.form['contact']
        email = request.form['email']
        message = request.form.get('message', '')

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Append to sheet
        sheet.append_row([full_name, contact_number, email, message, timestamp])

        return redirect('/')  # or show a thank you page
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)

