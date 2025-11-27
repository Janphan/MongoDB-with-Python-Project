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
    vocabulary_collection = db['vocabulary'].find()
    words = [vocab['word'] for vocab in vocabulary_collection]
    return render_template_string('''
    <h1>Vocabulary Words</h1>
    <ul>
    {% for word in words %}
        <li>{{ word }}</li>
    {% endfor %}
    </ul>
    <a href="/add">Add New Word</a>
    ''', words=words)

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
    <h1>Add New Word</h1>
    <form method="post">
        Word: <input type="text" name="word"><br>
        Definition: <input type="text" name="definition"><br>
        Part of Speech: <input type="text" name="part_of_speech"><br>
        <input type="submit" value="Add">
    </form>
    ''')

if __name__ == '__main__':
    app.run(debug=True)