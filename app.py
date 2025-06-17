from flask import Flask, render_template, request, redirect, session, send_file
from datetime import datetime
import pandas as pd
import io

app = Flask(__name__)
app.secret_key = 'supersecret'

users = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'abdulla': {'password': '1234', 'role': 'marketer'},
    'salem': {'password': '1234', 'role': 'marketer'},
    'moad': {'password': '1234', 'role': 'marketer'},
    'riyad': {'password': '1234', 'role': 'marketer'},
    'kilani': {'password': '1234', 'role': 'marketer'}
}

transactions = []

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username'].lower()
        p = request.form['password']
        if u in users and users[u]['password'] == p:
            session['user'] = u
            role = users[u]['role']
            return redirect('/admin' if role == 'admin' else '/dashboard')
        return 'Login Failed'
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session or users[session['user']]['role'] != 'marketer':
        return redirect('/')
    user = session['user']
    if request.method == 'POST':
        amount = float(request.form['amount'])
        ttype = request.form['type']
        transactions.append({'name': user, 'type': ttype, 'amount': amount, 'date': datetime.now().strftime('%Y-%m-%d')})
    user_data = [t for t in transactions if t['name'] == user]
    return render_template('dashboard.html', name=user.capitalize(), records=user_data)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' not in session or users[session['user']]['role'] != 'admin':
        return redirect('/')
    if request.method == 'POST':
        name = request.form['name']
        amount = float(request.form['amount'])
        ttype = request.form['type']
        transactions.append({'name': name.lower(), 'type': ttype, 'amount': amount, 'date': datetime.now().strftime('%Y-%m-%d')})
    return render_template('admin.html', records=transactions)

@app.route('/export_excel')
def export_excel():
    df = pd.DataFrame(transactions)
    if df.empty:
        return "No data to export."
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for name in df['name'].unique():
            df[df['name'] == name].to_excel(writer, sheet_name=name.capitalize(), index=False)
    output.seek(0)
    return send_file(output, download_name="Tizdan_Transactions.xlsx", as_attachment=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
