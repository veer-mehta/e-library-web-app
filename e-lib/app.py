from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename

from mega import Mega
import os, pymysql

app = Flask(__name__)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = 'dfsdf'

db = pymysql.connections.Connection(host='localhost', user='root', password='Vam#090905', db='bookslib')

cursor = db.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS bookslib")

cursor.execute("""
	CREATE TABLE IF NOT EXISTS authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    author_name VARCHAR(255) NOT NULL
);
""")

cursor.execute("""
	CREATE TABLE IF NOT EXISTS genres (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    genre_name VARCHAR(100) NOT NULL
);
""")

cursor.execute("""
	CREATE TABLE IF NOT EXISTS users (
    userid INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);
""")

cursor.execute("""
	CREATE TABLE IF NOT EXISTS books (book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_id INT,
    genre_id INT,
    description TEXT,
    FOREIGN KEY (author_id) REFERENCES authors(author_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);
""")


mega = Mega()


@app.route('/', methods=["GET"])											#HOME
def home():
	return render_template('home.html')


@app.route('/login', methods=["GET", "POST"])
def login():
	if request.method == "POST":
		name = request.form['name']
		pswd = request.form['password']
		email = request.form['email']

		cursor.execute(f"select count(*) from users where email = {email}")
		if cursor.fetchone()[0]:
			#record exists
			pass
		else:
			cursor.execute(f"insert into users values (0, {name}, {pswd}, {email})")
		
		return render_template('home.html')


	return render_template('login.html')


@app.route('/signup', methods=["GET", "POST"])
def signup():
	return render_template('signup.html')


@app.route('/upload', methods=['GET', 'POST'])								#UPLOAD
def upload():
	if request.method == 'POST':

		file = request.files['file']
		book_name = request.form['book_name']
		author = request.form['author']

		if file.filename:
			filename = secure_filename(file.filename)
			file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			file.save(file_path)
			mega_file = mega.upload(file_path)
			link = mega.get_upload_link(mega_file)
			return render_template('home.html')

	return render_template('upload.html')


@app.route('/genreselectionpage')
def genreselectionpage():
	return render_template('genreselectionpage.html')


@app.route('/authorselectionpage')
def authorselectionpage():
	return render_template('authorselectionpage.html')


@app.route('/userprofile')
def userprofile():
	return render_template('userprofile.html')


@app.route('/searchpage')
def searchpage():
	return render_template('searchpage.html')


if __name__ == '__main__':
	app.run(debug=True)
