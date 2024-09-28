from flask import Flask, render_template, request, redirect, url_for, jsonify, g
from werkzeug.utils import secure_filename

from mega import Mega
import os, pymysql

app = Flask(__name__)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = 'SECRET_PASSWORD'

db = pymysql.connections.Connection(host='localhost', user='root', password='your_password', db='bookslib')

cursor = db.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS bookslib")


cursor.execute("""
	CREATE TABLE IF NOT EXISTS users (
	user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL
);
""")


cursor.execute("""
	CREATE TABLE IF NOT EXISTS authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    author_name VARCHAR(200) NOT NULL
);
""")


cursor.execute("""
	CREATE TABLE IF NOT EXISTS genres (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    genre_name VARCHAR(100) NOT NULL
);
""")


cursor.execute("""
	CREATE TABLE IF NOT EXISTS books (book_id INT AUTO_INCREMENT PRIMARY KEY,
    book_name VARCHAR(255) NOT NULL,
    author_id INT,
	uploader_id INT,
    genre_id INT,
	link VARCHAR(300),
    description TEXT,
    FOREIGN KEY (author_id) REFERENCES authors(author_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id),
    FOREIGN KEY (uploader_id) REFERENCES users(user_id)
);
""")


mega = Mega()
mega = mega.login('your_email_id', 'your_password')


@app.route('/', methods=["GET"])											#HOME
def home():
	return render_template('home.html')


@app.route('/login', methods=["GET", "POST"])
def login():
	if request.method == "POST":
		email = request.form['email']
		pswd = request.form['password']

		cursor.execute(f"select * from users where email = '{email}'")
		d = cursor.fetchone()
		if len(d):
			g.user = {}
			g.user['id'] = d[0]
			g.user['name'] = d[1]
			g.user['email'] = d[2]
			g.user['pwd'] = d[3]
			open("abc.txt", "w").write(str(g.user))
			db.commit()
			return redirect(url_for('home'))
		else:
			db.commit()
			return redirect(url_for('signup'))
		
	return render_template('login.html')


@app.route('/signup', methods=["GET", "POST"])
def signup():
	if request.method == "POST":
		name = request.form['username']
		email = request.form['email']
		pswd = request.form['password']

		cursor.execute(f"select * from users where email = '{email}'")
		d = cursor.fetchall()
		open("abc.txt", "w").write(str(d))

		if len(d):
			return redirect(url_for('login'))
		else:
			cursor.execute(f'insert into users values (0, "{name}", "{email}", "{pswd}")')
			cursor.execute(f'select * from users where user_name = "{name}"')
			d = cursor.fetchone()
			g.user = {}
			g.user['id'] = d[0]
			g.user['name'] = d[1]
			g.user['email'] = d[2]
			g.user['pwd'] = d[3]
			open("abc.txt", "w").write(str(g.user))
			db.commit()
			return redirect(url_for('authorselectionpage'))
		
	return render_template('signup.html')


@app.route('/upload', methods=['GET', 'POST'])								#UPLOAD
def upload():
	if request.method == 'POST':

		file = request.files['file']
		book_name = request.form['book_name']
		author = request.form['author']
		genre = request.form['genre']

		if file.filename:
			filename = secure_filename(file.filename)
			file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
			file.save(file_path)
			mega_file = mega.upload(file_path)
			link = mega.get_upload_link(mega_file)
			open("abc.txt", "w").write(str(link))
			cursor.execute(f'select id from authors where author_name = "{author}"')
			author_id = cursor.fetchone()
			cursor.execute(f'select id from genres where genre_name = "{genre}"')
			genre_id = cursor.fetchone()
			
			if author_id == []:
				cursor.execute(f'insert into authors values(0, "{author}")')
				cursor.execute(f'select author_id from authors where author_name = "{author}"')
				author_id = cursor.fetchone()[0]
			if genre_id == []:
				cursor.execute(f'insert into genres values(0, "{genre}")')
				cursor.execute(f'select genre_id from genres where author_name = "{genre}"')
				genre_id = cursor.fetchone()[0]

			cursor.execute(f'insert into books values("{book_name}", {author_id[0]}, {g.user[1]}, {genre_id[0]}, "{link}")')
			db.commit()
			return redirect(url_for('home'))

	return render_template('upload.html')


@app.route('/genreselectionpage', methods=["POST", "GET"])
def genreselectionpage():


	return render_template('genreselectionpage.html')


@app.route('/authorselectionpage', methods=["POST", "GET"])
def authorselectionpage():
	return render_template('authorselectionpage.html')


@app.route('/userprofile')
def userprofile():
	cursor.execute(f"select * from books where uploader_id = {g.user['id']}")
	bu = cursor.fetchall()
	cursor.execute(f"""
	SELECT 
		books.book_name, 
		authors.author_name, 
		genres.genre_name
	FROM 
		books JOIN authors ON books.author_id = authors.author_id JOIN genres ON books.genre_id = genres.genre_id
	WHERE 
		books.uploader_id = {g.user['id']};
	""")
	return render_template('userprofile.html', books=bu[:5])


@app.route('/searchpage', methods=["POST", "GET"])
def searchpage():
	return render_template('searchpage.html')


if __name__ == '__main__':
	app.run(debug=True)
