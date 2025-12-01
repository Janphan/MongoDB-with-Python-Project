from flask import Flask, render_template_string, request, redirect, url_for
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')  # Add to .env

mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(mongo_uri)
db = client[os.getenv('MONGODB_DATABASE', 'Vocabulary-finnish')]

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_doc):
        self.id = str(user_doc['_id'])
        self.name = user_doc.get('name', '')
        self.email = user_doc.get('email', '')

@login_manager.user_loader
def load_user(user_id):
    user_doc = db['users'].find_one({'_id': ObjectId(user_id)})
    if user_doc:
        return User(user_doc)
    return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if db['users'].find_one({'email': email}):
            return 'User already exists'
        hashed_password = generate_password_hash(password)
        user_id = db['users'].insert_one({
            'name': name,
            'email': email,
            'password': hashed_password
        }).inserted_id
        user = User(db['users'].find_one({'_id': user_id}))
        login_user(user)
        return redirect('/')
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register</title>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                margin: 0; 
                color: #333; 
            }
            .container { 
                background: white; 
                padding: 40px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
                max-width: 400px; 
                width: 100%; 
                text-align: center; 
            }
            h1 { 
                margin-bottom: 30px; 
                color: #4CAF50; 
                font-size: 28px; 
                font-weight: 300; 
            }
            form { 
                display: flex; 
                flex-direction: column; 
            }
            label { 
                text-align: left; 
                margin-bottom: 8px; 
                font-weight: 600; 
                color: #555; 
            }
            input[type="text"], input[type="password"] { 
                padding: 12px; 
                margin-bottom: 20px; 
                border: 2px solid #e0e0e0; 
                border-radius: 8px; 
                width: 100%; 
                font-size: 16px; 
                transition: border-color 0.3s; 
            }
            input[type="text"]:focus, input[type="password"]:focus { 
                border-color: #4CAF50; 
                outline: none; 
            }
            input[type="submit"] { 
                background: #4CAF50; 
                color: white; 
                padding: 12px; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                font-size: 16px; 
                font-weight: 600; 
                transition: background 0.3s; 
                width: 100%; 
            }
            input[type="submit"]:hover { 
                background: #45a049; 
                transform: translateY(-2px); 
                box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3); 
            }
            p { 
                margin-top: 20px; 
                font-size: 14px; 
            }
            a { 
                color: #667eea; 
                text-decoration: none; 
                font-weight: 600; 
            }
            a:hover { 
                text-decoration: underline; 
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Register</h1>
            <form method="post">
                <label>Name: <input type="text" name="name" required></label>
                <label>Email: <input type="text" name="email" required></label>
                <label>Password: <input type="password" name="password" required></label>
                <input type="submit" value="Register">
            </form>
            <p>Already have an account? <a href="/login">Login</a></p>
        </div>
    </body>
    </html>
    ''')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_doc = db['users'].find_one({'email': email})
        if user_doc and check_password_hash(user_doc['password'], password):
            user = User(user_doc)
            login_user(user)
            return redirect('/')
        return 'Invalid credentials'
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login</title>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                margin: 0; 
                color: #333; 
            }
            .container { 
                background: white; 
                padding: 40px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
                max-width: 400px; 
                width: 100%; 
                text-align: center; 
            }
            h1 { 
                margin-bottom: 30px; 
                color: #4CAF50; 
                font-size: 28px; 
                font-weight: 300; 
            }
            form { 
                display: flex; 
                flex-direction: column; 
            }
            label { 
                text-align: left; 
                margin-bottom: 8px; 
                font-weight: 600; 
                color: #555; 
            }
            input[type="text"], input[type="password"] { 
                padding: 12px; 
                margin-bottom: 20px; 
                border: 2px solid #e0e0e0; 
                border-radius: 8px; 
                width: 100%; 
                font-size: 16px; 
                transition: border-color 0.3s; 
            }
            input[type="text"]:focus, input[type="password"]:focus { 
                border-color: #4CAF50; 
                outline: none; 
            }
            input[type="submit"] { 
                background: #4CAF50; 
                color: white; 
                padding: 12px; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                font-size: 16px; 
                font-weight: 600; 
                transition: background 0.3s; 
                width: 100%; 
            }
            input[type="submit"]:hover { 
                background: #45a049; 
                transform: translateY(-2px); 
                box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3); 
            }
            p { 
                margin-top: 20px; 
                font-size: 14px; 
            }
            a { 
                color: #667eea; 
                text-decoration: none; 
                font-weight: 600; 
            }
            a:hover { 
                text-decoration: underline; 
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Login</h1>
            <form method="post">
                <label>Email: <input type="text" name="email" required></label>
                <label>Password: <input type="password" name="password" required></label>
                <input type="submit" value="Login">
            </form>
            <p>Don't have an account? <a href="/register">Register</a></p>
        </div>
    </body>
    </html>
    ''')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/')
@login_required
def index():
    docs = list(db['vocabulary'].find())
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vocabulary Words</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }
            h1 { text-align: center; color: #333; }
            ul { list-style-type: none; padding: 0; }
            li { background: #f9f9f9; margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 5px solid #4CAF50; position: relative; }
            .actions { position: absolute; top: 50%; right: 15px; transform: translateY(-50%); }
            .actions a { margin-left: 10px; }
            strong { color: #555; }
            a { color: #4CAF50; text-decoration: none; font-weight: bold; }
            a:hover { text-decoration: underline; }
            .nav-bar { display: flex; justify-content: center; gap: 20px; margin-top: 20px; }
            .add-link { background: #4CAF50; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; }
            .add-link:hover { background: #45a049; }
            .user-info { text-align: center; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="user-info">
                <p>Welcome, {{ current_user.name }}! <a href="/logout">Logout</a></p>
            </div>
            <h1>Vocabulary Words</h1>
            <ul>
            {% for doc in docs %}
                <li>
                    <strong>Word:</strong> {{ doc.word }}<br>
                    <strong>Translation:</strong> {{ doc.get('translation', 'N/A') }}<br>
                    <strong>Part of Speech:</strong> {{ doc.get('partOfSpeech', doc.get('part_of_speech', 'N/A')) }}<br>
                    <strong>Examples:</strong> {{ doc.get('examples', []) | join(', ') }}<br>
                    <strong>Categories:</strong> {{ doc.get('categories', []) | join(', ') }}
                    <div class="actions">
                        <a href="/edit/{{ doc['_id'] }}">Edit</a>
                        <a href="/delete/{{ doc['_id'] }}" style="color: red;">Delete</a>
                    </div>
                </li>
            {% endfor %}
            </ul>
            <div class="nav-bar">
                <a href="/add" class="add-link">Add New Word</a>
                <a href="/categories" class="add-link" style="background: #2196F3;">View Categories</a>
                <a href="/statistics" class="add-link" style="background: #FF9800;">View Statistics</a>
            </div>
        </div>
    </body>
    </html>
    ''', docs=docs)

@app.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_word(id):
    from bson import ObjectId
    if request.method == 'POST':
        db['vocabulary'].update_one({'_id': ObjectId(id)}, {'$set': {
            'word': request.form['word'],
            'translation': request.form['translation'],
            'partOfSpeech': request.form['partOfSpeech'],
            'examples': [e.strip() for e in request.form['examples'].split(',') if e.strip()],
            'categories': [c.strip() for c in request.form['categories'].split(',') if c.strip()]
        }})
        return redirect('/')
    doc = db['vocabulary'].find_one({'_id': ObjectId(id)})
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Edit Word</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }
            h1 { text-align: center; color: #333; }
            form { display: flex; flex-direction: column; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input[type="text"] { padding: 10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 5px; width: 100%; }
            input[type="submit"] { background: #4CAF50; color: white; padding: 10px; border: none; border-radius: 5px; cursor: pointer; width: 100%; font-size: 16px; }
            input[type="submit"]:hover { background: #45a049; }
            .back-link { display: block; text-align: center; margin-top: 20px; background: #4CAF50; color: white; padding: 10px; border-radius: 5px; text-decoration: none; font-size: 16px; }
            .back-link:hover { background: #45a049; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Edit Word</h1>
            <form method="post">
                <label>Word: <input type="text" name="word" value="{{ doc.word }}" required></label>
                <label>Translation: <input type="text" name="translation" value="{{ doc.translation }}" required></label>
                <label>Part of Speech: <input type="text" name="partOfSpeech" value="{{ doc.partOfSpeech }}" required></label>
                <label>Examples: <input type="text" name="examples" value="{{ doc.get('examples', []) | join(', ') }}"></label>
                <label>Categories: <input type="text" name="categories" value="{{ doc.get('categories', []) | join(', ') }}"></label>
                <input type="submit" value="Update">
            </form>
            <a href="/" class="back-link">Back to Home</a>
        </div>
    </body>
    </html>
    ''', doc=doc)

@app.route('/delete/<id>')
@login_required
def delete_word(id):
    from bson import ObjectId
    db['vocabulary'].delete_one({'_id': ObjectId(id)})
    return redirect('/')

@app.route('/categories')
@login_required
def categories():
    cats = list(db['categories'].find())
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Categories</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }
            h1 { text-align: center; color: #333; }
            ul { list-style-type: none; padding: 0; }
            li { background: #f9f9f9; margin: 10px 0; padding: 10px; border-radius: 5px; border-left: 5px solid #2196F3; }
            a { color: #2196F3; text-decoration: none; font-weight: bold; }
            a:hover { text-decoration: underline; }
            .back-link { display: block; text-align: center; margin-top: 20px; background: #2196F3; color: white; padding: 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Categories</h1>
            <ul>
            {% for cat in cats %}
                <li>{% set name = cat.get('name', '') %}{% set desc = cat.get('description', '') %}{% if name %}{{ name }}{% if desc %} - {{ desc }}{% endif %}{% endif %}</li>
            {% endfor %}
            </ul>
            <a href="/" class="back-link">Back to Vocabulary</a>
        </div>
    </body>
    </html>
    ''', cats=cats)

@app.route('/statistics')
@login_required
def statistics():
    total_vocab = db['vocabulary'].count_documents({})
    total_categories = db['categories'].count_documents({})
    total_users = db['users'].count_documents({})
    # Perhaps more stats, like average words per category, etc.
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Statistics</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }
            h1 { text-align: center; color: #333; }
            .stat { background: #f9f9f9; margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 5px solid #FF9800; }
            .stat strong { color: #555; }
            a { color: #FF9800; text-decoration: none; font-weight: bold; }
            a:hover { text-decoration: underline; }
            .back-link { display: block; text-align: center; margin-top: 20px; background: #FF9800; color: white; padding: 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Statistics</h1>
            <div class="stat">
                <strong>Total Vocabulary Words:</strong> {{ total_vocab }}
            </div>
            <div class="stat">
                <strong>Total Categories:</strong> {{ total_categories }}
            </div>
            <div class="stat">
                <strong>Total Users:</strong> {{ total_users }}
            </div>
            <a href="/" class="back-link">Back to Vocabulary</a>
        </div>
    </body>
    </html>
    ''', total_vocab=total_vocab, total_categories=total_categories, total_users=total_users)

@app.route('/users')
@login_required
def users():
    users_list = list(db['users'].find())
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Users</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }
            h1 { text-align: center; color: #333; }
            ul { list-style-type: none; padding: 0; }
            li { background: #f9f9f9; margin: 10px 0; padding: 10px; border-radius: 5px; border-left: 5px solid #9C27B0; }
            a { color: #9C27B0; text-decoration: none; font-weight: bold; }
            a:hover { text-decoration: underline; }
            .back-link { display: block; text-align: center; margin-top: 20px; background: #9C27B0; color: white; padding: 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Users</h1>
            <ul>
            {% for user in users_list %}
                <li>{% set name = user.get('name', '') %}{% set email = user.get('email', '') %}{% if name %}{{ name }}{% if email %} - {{ email }}{% endif %}{% endif %}</li>
            {% endfor %}
            </ul>
            <a href="/" class="back-link">Back to Vocabulary</a>
        </div>
    </body>
    </html>
    ''', users_list=users_list)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_word():
    if request.method == 'POST':
        db['vocabulary'].insert_one({
            'word': request.form['word'],
            'translation': request.form['translation'],
            'partOfSpeech': request.form['partOfSpeech'],
            'examples': [e.strip() for e in request.form['examples'].split(',') if e.strip()],
            'categories': [c.strip() for c in request.form['categories'].split(',') if c.strip()]
        })
        return redirect(url_for('index'))
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add New Word</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 600px; width: 100%; }
            h1 { text-align: center; color: #333; }
            form { display: flex; flex-direction: column; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input[type="text"] { padding: 10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 5px; width: 100%; }
            input[type="submit"] { background: #4CAF50; color: white; padding: 10px; border: none; border-radius: 5px; cursor: pointer; width: 100%; font-size: 16px; }
            input[type="submit"]:hover { background: #45a049; }
            .back-link { display: block; text-align: center; margin-top: 20px; background: #4CAF50; color: white; padding: 10px; border-radius: 5px; text-decoration: none; font-size: 16px; }
            .back-link:hover { background: #45a049; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Add New Word</h1>
            <form method="post">
                <label>Word: <input type="text" name="word" required></label>
                <label>Translation: <input type="text" name="translation" required></label>
                <label>Part of Speech: <input type="text" name="partOfSpeech" placeholder="e.g., noun, verb" required></label>
                <label>Examples: <input type="text" name="examples" placeholder="Separate with commas, e.g., sentence1, sentence2"></label>
                <label>Categories: <input type="text" name="categories" placeholder="Separate with commas, e.g., Home & Living, A1 Basics"></label>
                <input type="submit" value="Add Word">
            </form>
            <a href="/" class="back-link">Back to Home</a>
        </div>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    app.run(debug=True)