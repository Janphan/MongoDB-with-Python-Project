from flask import Flask, render_template_string, request, redirect, url_for
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(mongo_uri)
db = client[os.getenv('MONGODB_DATABASE', 'Vocabulary-finnish')]

@app.route('/')
def index():
    docs = list(db['vocabulary'].find())
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vocabulary Words</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }
            h1 { text-align: center; color: #333; }
            ul { list-style-type: none; padding: 0; }
            li { background: #f9f9f9; margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 5px solid #4CAF50; position: relative; }
            .actions { position: absolute; top: 50%; right: 15px; transform: translateY(-50%); }
            .actions a { margin-left: 10px; }
            strong { color: #555; }
            a { color: #4CAF50; text-decoration: none; font-weight: bold; }
            a:hover { text-decoration: underline; }
            .add-link { float: right; background: #4CAF50; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; margin: 10px; }
            .add-link:hover { background: #45a049; }
        </style>
    </head>
    <body>
        <div class="container">
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
                <button><a href="/edit/{{ doc._id }}">Edit</a></button>
                <button><a href="/delete/{{ doc._id }}">Delete</a></button>
            {% endfor %}
            </ul>
            <a href="/add" class="add-link">Add New Word</a>
            <a href="/categories" class="add-link" style="background: #2196F3;">View Categories</a>
        </div>
    </body>
    </html>
    ''', docs=docs)

@app.route('/edit/<id>', methods=['GET', 'POST'])
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
            body { font-family: Arial, sans-serif; background-color: #f4f4f4; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 400px; width: 100%; }
            h1 { text-align: center; color: #333; }
            form { display: flex; flex-direction: column; }
            label { margin-bottom: 5px; font-weight: bold; }
            input[type="text"] { padding: 10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 5px; }
            input[type="submit"] { background: #4CAF50; color: white; padding: 10px; border: none; border-radius: 5px; cursor: pointer; }
            input[type="submit"]:hover { background: #45a049; }
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
        </div>
    </body>
    </html>
    ''', doc=doc)

@app.route('/delete/<id>')
def delete_word(id):
    from bson import ObjectId
    db['vocabulary'].delete_one({'_id': ObjectId(id)})
    return redirect('/')

@app.route('/categories')
def categories():
    cats = list(db['categories'].find())
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Categories</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }
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
                <li>{{ cat.get('name', 'N/A') }} - {{ cat.get('description', 'N/A') }}</li>
            {% endfor %}
            </ul>
            <a href="/" class="back-link">Back to Vocabulary</a>
        </div>
    </body>
    </html>
    ''', cats=cats)

@app.route('/add', methods=['GET', 'POST'])
def add_word():
    if request.method == 'POST':
        word = request.form['word']
        definition = request.form['definition']
        part_of_speech = request.form['part_of_speech']
        db['vocabulary'].insert_one({
            'word': word,
            'definition': definition,
            'part_of_speech': part_of_speech
        })
        return redirect(url_for('index'))
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add New Word</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f4; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 400px; width: 100%; }
            h1 { text-align: center; color: #333; }
            form { display: flex; flex-direction: column; }
            label { margin-bottom: 5px; font-weight: bold; }
            input[type="text"] { padding: 10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 5px; }
            input[type="submit"] { background: #4CAF50; color: white; padding: 10px; border: none; border-radius: 5px; cursor: pointer; }
            input[type="submit"]:hover { background: #45a049; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Add New Word</h1>
            <form method="post">
                <label>Word: <input type="text" name="word" required></label>
                <label>Definition: <input type="text" name="definition"></label>
                <label>Part of Speech: <input type="text" name="part_of_speech"></label>
                <input type="submit" value="Add">
            </form>
        </div>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    app.run(debug=True)