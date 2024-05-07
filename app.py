from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient, DESCENDING
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB connection
client = MongoClient('localhost', 27017)
db = client['content_database']
articles_collection = db['articles']

articles_collection.create_index([('title', 'text'), ('content', 'text')])

# Function to create an article
@app.route('/create', methods=['GET', 'POST'])
def create_article():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        # Basic validation
        if not (title and content):
            return "Please fill in all fields"

        article_data = {
            'title': title,
            'content': content
        }

        # Insert article data into MongoDB
        articles_collection.insert_one(article_data)
        return redirect(url_for('read_articles'))

    return render_template('create_article.html')

# Function to read articles
@app.route('/')
def read_articles():
    articles = articles_collection.find().sort('_id', DESCENDING)
    return render_template('read_articles.html', articles=articles)

# Function to delete an article
@app.route('/delete/<article_id>')
def delete_article(article_id):
    articles_collection.delete_one({'_id': ObjectId(article_id)})
    return redirect(url_for('read_articles'))

# Function to update an article
@app.route('/update/<article_id>', methods=['GET', 'POST'])
def update_article(article_id):
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        # Update article in MongoDB
        articles_collection.update_one(
            {'_id': ObjectId(article_id)},
            {'$set': {'title': title, 'content': content}}
        )
        return redirect(url_for('read_articles'))

    article = articles_collection.find_one({'_id': ObjectId(article_id)})
    return render_template('update_article.html', article=article)

# Function to search articles
@app.route('/search', methods=['GET', 'POST'])
def search_articles():
    if request.method == 'POST':
        keyword = request.form['keyword']
        articles = articles_collection.find({'$text': {'$search': keyword}})
    else:
        articles = articles_collection.find()
    return render_template('search_articles.html', articles=articles)

if __name__ == "__main__":
    app.run(debug=True)
