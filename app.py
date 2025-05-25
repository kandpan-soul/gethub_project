from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os
import openai
import cohere

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///holyspirit.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Prayer Request model
class PrayerRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    prayed_for = db.Column(db.Integer, default=0)

# Testimony model
class Testimony(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Devotion model
class Devotion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.Date, default=datetime.date.today)
    verse = db.Column(db.String(255))
    reflection = db.Column(db.Text)
    journal = db.Column(db.Text)

# Fruits of the Spirit Tracker model
class FruitTracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fruit = db.Column(db.String(50))
    date = db.Column(db.Date, default=datetime.date.today)
    value = db.Column(db.Integer, default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper function to get user fruit tracker

def get_user_fruits(user_id):
    fruits_list = ['Love', 'Joy', 'Peace', 'Patience', 'Kindness', 'Goodness', 'Faithfulness', 'Gentleness', 'Self-control']
    user_fruits = {fruit: 0 for fruit in fruits_list}
    for fruit in fruits_list:
        latest = FruitTracker.query.filter_by(user_id=user_id, fruit=fruit).order_by(FruitTracker.date.desc()).first()
        if latest:
            user_fruits[fruit] = latest.value
    return user_fruits

# AI-powered homepage
@app.route('/', methods=['GET', 'POST'])
def home():
    ai_response = None
    if request.method == 'POST':
        user_message = request.form['message']
        system_prompt = "You are a helpful Christian assistant. Give a warm, inspiring introduction to the Holy Spirit and answer the user's question."
        try:
            ai_result = co.chat(
                model="command-r-plus",
                message=user_message,
                chat_history=[],
                temperature=0.5,
                connectors=None,
                preamble=system_prompt
            )
            ai_response = ai_result.text
        except Exception as e:
            ai_response = f"Cohere Error: {str(e)}"
    return render_template('home.html', ai_response=ai_response)

# AI-powered scripture explorer
@app.route('/explorer', methods=['GET', 'POST'])
def explorer():
    ai_response = None
    if request.method == 'POST':
        user_message = request.form['message']
        system_prompt = "You are a Christian assistant. Help the user explore Bible verses about the Holy Spirit. Suggest relevant scriptures and explain their meaning."
        try:
            ai_result = co.chat(
                model="command-r-plus",
                message=user_message,
                chat_history=[],
                temperature=0.5,
                connectors=None,
                preamble=system_prompt
            )
            ai_response = ai_result.text
        except Exception as e:
            ai_response = f"Cohere Error: {str(e)}"
    return render_template('explorer.html', ai_response=ai_response)

# AI-powered daily devotion
@app.route('/devotion', methods=['GET', 'POST'])
@login_required
def devotion():
    ai_response = None
    if request.method == 'POST':
        user_message = request.form['message']
        system_prompt = "You are a Christian devotion assistant. Suggest a daily verse, provide a reflection, and encourage journaling."
        try:
            ai_result = co.chat(
                model="command-r-plus",
                message=user_message,
                chat_history=[],
                temperature=0.5,
                connectors=None,
                preamble=system_prompt
            )
            ai_response = ai_result.text
        except Exception as e:
            ai_response = f"Cohere Error: {str(e)}"
    return render_template('devotion.html', ai_response=ai_response)

# AI-powered fruits tracker
@app.route('/fruits', methods=['GET', 'POST'])
@login_required
def fruits():
    ai_response = None
    fruits_list = ['Love', 'Joy', 'Peace', 'Patience', 'Kindness', 'Goodness', 'Faithfulness', 'Gentleness', 'Self-control']
    user_fruits = get_user_fruits(current_user.id)
    if request.method == 'POST':
        if 'message' in request.form:
            user_message = request.form['message']
            fruit_status = ', '.join([f"{k}: {v}" for k, v in user_fruits.items()])
            system_prompt = f"You are a Christian assistant. The user's Fruits of the Spirit tracker is: {fruit_status}. Give encouragement, practical tips, and a summary of their spiritual growth based on these values."
            try:
                ai_result = co.chat(
                    model="command-r-plus",
                    message=f"My tracker: {fruit_status}. {user_message}",
                    chat_history=[],
                    temperature=0.5,
                    connectors=None,
                    preamble=system_prompt
                )
                ai_response = ai_result.text
            except Exception as e:
                ai_response = f"Cohere Error: {str(e)}"
        else:
            # Handle tracker update form
            for fruit in fruits_list:
                value = int(request.form.get(fruit, 0))
                tracker = FruitTracker(user_id=current_user.id, fruit=fruit, value=value)
                db.session.add(tracker)
            db.session.commit()
            flash('Fruits of the Spirit updated!')
            return redirect(url_for('fruits'))
    # Always show AI summary of current tracker
    if not ai_response and user_fruits:
        fruit_status = ', '.join([f"{k}: {v}" for k, v in user_fruits.items()])
        system_prompt = f"You are a Christian assistant. The user's Fruits of the Spirit tracker is: {fruit_status}. Give a summary and encouragement based on these values."
        try:
            ai_result = co.chat(
                model="command-r-plus",
                message=f"My tracker: {fruit_status}. Give me a summary and encouragement.",
                chat_history=[],
                temperature=0.5,
                connectors=None,
                preamble=system_prompt
            )
            ai_response = ai_result.text
        except Exception as e:
            ai_response = f"Cohere Error: {str(e)}"
    return render_template('fruits.html', fruits=fruits_list, ai_response=ai_response)

# AI-powered prayer wall
@app.route('/prayer', methods=['GET', 'POST'])
@login_required
def prayer():
    ai_response = None
    if request.method == 'POST':
        user_message = request.form['message']
        system_prompt = "You are a Christian prayer assistant. Help the user write, reflect on, or pray for requests. Offer encouragement and scriptural support."
        try:
            ai_result = co.chat(
                model="command-r-plus",
                message=user_message,
                chat_history=[],
                temperature=0.5,
                connectors=None,
                preamble=system_prompt
            )
            ai_response = ai_result.text
        except Exception as e:
            ai_response = f"Cohere Error: {str(e)}"
    requests = PrayerRequest.query.order_by(PrayerRequest.timestamp.desc()).all()
    return render_template('prayer.html', requests=requests, ai_response=ai_response)

# AI-powered testimony sharing
@app.route('/testimony', methods=['GET', 'POST'])
@login_required
def testimony():
    ai_response = None
    if request.method == 'POST':
        user_message = request.form['message']
        system_prompt = "You are a Christian testimony assistant. Encourage the user to share their experiences and offer uplifting feedback."
        try:
            ai_result = co.chat(
                model="command-r-plus",
                message=user_message,
                chat_history=[],
                temperature=0.5,
                connectors=None,
                preamble=system_prompt
            )
            ai_response = ai_result.text
        except Exception as e:
            ai_response = f"Cohere Error: {str(e)}"
    testimonies = Testimony.query.order_by(Testimony.timestamp.desc()).all()
    return render_template('testimony.html', testimonies=testimonies, ai_response=ai_response)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return redirect(url_for('signup'))
        hashed_password = generate_password_hash(password)
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Signup successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials!')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    ai_response = None
    if request.method == 'POST' and 'ai_message' in request.form:
        user_message = request.form['ai_message']
        system_prompt = "You are a helpful Christian assistant focused on the Holy Spirit. Give spiritual guidance, encouragement, or practical help as requested."
        try:
            ai_result = co.chat(
                model="command-r-plus",
                message=user_message,
                chat_history=[],
                temperature=0.5,
                connectors=None,
                preamble=system_prompt
            )
            ai_response = ai_result.text
        except Exception as e:
            ai_response = f"Cohere Error: {str(e)}"
    return render_template('dashboard.html', ai_response=ai_response)

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    response = None
    if request.method == 'POST':
        user_message = request.form['message']
        # Simple rule-based bot for demonstration
        if 'holy spirit' in user_message.lower():
            response = "The Holy Spirit is our Comforter, Guide, and Helper. (John 14:26)"
        elif 'fruit' in user_message.lower():
            response = "The fruits of the Spirit are: Love, Joy, Peace, Patience, Kindness, Goodness, Faithfulness, Gentleness, and Self-control. (Galatians 5:22-23)"
        elif 'pray' in user_message.lower():
            response = "Prayer is our way to communicate with God. The Holy Spirit helps us in our prayers. (Romans 8:26)"
        else:
            response = "I'm here to help you learn about the Holy Spirit! Ask me about the Holy Spirit, fruits of the Spirit, or prayer."
    return render_template('chatbot.html', response=response)

COHERE_API_KEY = '7PQEt4URxaK3mGGx1AVcHXu6QoqAqgRADiFWQPRS'
co = cohere.Client(COHERE_API_KEY)

@app.route('/ai-chatbot', methods=['GET', 'POST'])
def ai_chatbot():
    ai_response = None
    fruits_list = ['Love', 'Joy', 'Peace', 'Patience', 'Kindness', 'Goodness', 'Faithfulness', 'Gentleness', 'Self-control']
    user_fruits = None
    if current_user.is_authenticated:
        user_fruits = {fruit: 0 for fruit in fruits_list}
        for fruit in fruits_list:
            latest = FruitTracker.query.filter_by(user_id=current_user.id, fruit=fruit).order_by(FruitTracker.date.desc()).first()
            if latest:
                user_fruits[fruit] = latest.value
    if request.method == 'POST':
        user_message = request.form['message']
        try:
            if user_fruits:
                fruit_status = ', '.join([f"{k}: {v}" for k, v in user_fruits.items()])
                system_prompt = f"You are a helpful Christian assistant focused on the Holy Spirit and spiritual growth. The user's current Fruits of the Spirit tracker is: {fruit_status}. Give personalized, encouraging, and practical advice for their faith journey. Also, suggest ways to improve their spiritual life and how to use this website."
            else:
                system_prompt = "You are a helpful Christian assistant focused on the Holy Spirit and spiritual growth. Give practical advice for faith and how to use this website."
            response = co.chat(
                model="command-r-plus",
                message=user_message,
                chat_history=[],
                temperature=0.5,
                connectors=None,
                preamble=system_prompt
            )
            ai_response = response.text
        except Exception as e:
            ai_response = f"Cohere Error: {str(e)}"
    return render_template('ai_chatbot.html', response=ai_response)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
