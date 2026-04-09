from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ── DATABASE MODEL ────────────────────────────────────────────
class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    business = db.Column(db.String(200), nullable=False)
    service = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Lead {self.name}>'

# ── ROUTES ───────────────────────────────────────────────────

@app.route('/', methods=['GET', 'POST'])
def index():
    success = False
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        business = request.form.get('business')
        service = request.form.get('service')
        message = request.form.get('message')

        new_lead = Lead(
            name=name,
            email=email,
            business=business,
            service=service,
            message=message
        )
        db.session.add(new_lead)
        db.session.commit()
        success = True

    return render_template('index.html', success=success)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == os.getenv('ADMIN_PASSWORD'):
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            error = 'Incorrect password. Please try again.'
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    leads = Lead.query.order_by(Lead.date.desc()).all()
    total = Lead.query.count()
    return render_template('dashboard.html', leads=leads, total=total)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete_lead(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    lead = Lead.query.get_or_404(id)
    db.session.delete(lead)
    db.session.commit()
    return redirect(url_for('dashboard'))

# ── MAIN ─────────────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database created successfully!")
    print("🚀 Starting Lead Tracker...")
    app.run(debug=True)