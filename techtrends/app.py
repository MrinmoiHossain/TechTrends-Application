import sqlite3
import logging
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Define the total DB connection
db_connection_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global db_connection_count

    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row

    db_connection_count += 1

    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.info(f'A non-existing article is accessed')
        return render_template('404.html'), 404
    else:
        title = post['title']
        app.logger.info(f'Article "{title}" retrieved!')
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info(f'The About Us page is retrieved successfully')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    app.logger.info(f'A new article "{title}" is created')
    return render_template('create.html')

# Define the Application Healthcheck page
@app.route('/healthz')
def healthcheck():
    try:
        connection = get_db_connection()
        connection.cursor()
        connection.execute('SELECT * FROM posts')
        connection.close()

        response = app.response_class(
            response = json.dumps({"result" : "OK - healthy - Troubleshoot"}),
            status = 200,
            mimetype = 'application/json'
        )

        app.logger.info(f'Healthcheck page is retrieved healthy')
        return response
    except Exception:
        response = app.response_class(
            response = json.dumps({"result" : "ERROR - unhealthy"}),
            status = 500,
            mimetype = 'application/json'
        )

        app.logger.info(f'Healthcheck page is retrieved unhealthy')
        return response

# Define the Application Metrics page
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()

    response = app.response_class(
        response = json.dumps({"db_connection_count": db_connection_count, "post_count": len(posts)}),
        status = 200,
        mimetype = 'application/json'
    )

    app.logger.info(f'Metrics page is retrieved successfully')
    return response

# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(format = '%(asctime)s, %(message)s', datefmt = '%m/%d/%Y, %I:%M:%S', level = logging.DEBUG, handlers = [
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ])
    app.run(host='0.0.0.0', port='3111')
