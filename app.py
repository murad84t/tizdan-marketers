from datetime import date
import io, os
import pandas as pd
from flask import (Flask, render_template, redirect, url_for,
                   flash, request, send_file)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, TransactionForm
from models import db, User, Transaction

app = Flask(__name__)
app.config['SECRET_KEY']  = os.getenv('SECRET_KEY', 'dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 'sqlite:///tizdan.sqlite'
).replace("postgres://", "postgresql://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_mgr = LoginManager(app)
login_mgr.login_view = 'login'


@login_mgr.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Welcome, ' + user.name + '!', 'success')
            return redirect(url_for('admin_dashboard' if user.role == 'admin'
                                                 else 'marketer_dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('login'))


# ----------  Admin  ----------
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Admin only', 'danger')
        return redirect(url_for('logout'))

    tform = TransactionForm()
    marketers = User.query.filter_by(role='marketer').all()

    if tform.validate_on_submit():
        m_id = int(tform.marketer.data)
        amt  = -abs(tform.amount.data)   # store as negative (withdraw)
        db.session.add(Transaction(user_id=m_id, amount=amt))
        db.session.commit()
        flash('Recorded request for £{:.2f}'.format(abs(amt)), 'success')
        return redirect(url_for('admin_dashboard'))

    # summary for table
    today = date.today()
    summary = {m.name: m.balance(start=date(2025,1,1), end=today)
               for m in marketers}
    return render_template('admin_dashboard.html',
                           marketers=marketers,
                           summary=summary,
                           tform=tform)


# ----------  Marketer  ----------
@app.route('/dashboard')
@login_required
def marketer_dashboard():
    if current_user.role != 'marketer':
        return redirect(url_for('admin_dashboard'))

    start = date.fromisoformat(request.args.get('start', '2025-01-01'))
    end   = date.fromisoformat(request.args.get('end', str(date.today())))
    txs   = current_user.transactions_between(start, end)
    return render_template('marketer_dashboard.html',
                           txs=txs, start=start, end=end)


@app.route('/download')
@login_required
def download_excel():
    """Download marketer's report as Excel."""
    if current_user.role != 'marketer':
        return redirect(url_for('logout'))

    start = date.fromisoformat(request.args.get('start', '2025-01-01'))
    end   = date.fromisoformat(request.args.get('end', str(date.today())))
    txs   = current_user.transactions_between(start, end)

    df = pd.DataFrame([{
        'Date': t.timestamp.date(),
        'Type': 'Deposit' if t.amount > 0 else 'Withdraw',
        'Amount': abs(t.amount)
    } for t in txs])

    with io.BytesIO() as b:
        with pd.ExcelWriter(b, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Report')
        b.seek(0)
        return send_file(b,
            download_name=f'{current_user.username}_report.xlsx',
            as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
