from flask import Flask, render_template, request, redirect, url_for, g, session
from werkzeug.utils import secure_filename
from fuzzywuzzy import process  # Fuzzy matching

from mega import Mega
import os, psycopg2

app = Flask(__name__)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = 'dfsdf'


def close_db(con, cursor):
	con.commit()
	cursor.close()
	con.close()


def open_db(isinit=True):
	con = psycopg2.connect(host='localhost', user='postgres', password='veer', port='5432', database='bookslib')
	cursor = con.cursor()

	if isinit:
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS users (
			user_id SERIAL PRIMARY KEY,
			user_name VARCHAR(100) NOT NULL,
			email VARCHAR(100) UNIQUE NOT NULL,
			password VARCHAR(50) NOT NULL
		);
		""")


		cursor.execute("""
			CREATE TABLE IF NOT EXISTS authors (
			author_id SERIAL PRIMARY KEY,
			author_name VARCHAR(200) NOT NULL
		);
		""")


		cursor.execute("""
			CREATE TABLE IF NOT EXISTS genres (
			genre_id SERIAL PRIMARY KEY,
			genre_name VARCHAR(100) NOT NULL
		);
		""")


		cursor.execute("""
			CREATE TABLE IF NOT EXISTS books (
			book_id SERIAL PRIMARY KEY,
			book_name VARCHAR(255) NOT NULL,
			author_id INT REFERENCES authors(author_id),
			uploader_id INT REFERENCES users(user_id),
			genre_id INT REFERENCES genres(genre_id),
			link VARCHAR(300),
			description TEXT
		);
		""")

		return (con, cursor)


con, cursor = open_db(True)
cursor.close()
con.close()
mega = Mega()
mega = mega.login('veeramehta09@gmail.com', 'vam#090905')


@app.before_request
def load_logged_in_user():
	if 'id' in session:
		open('abc.txt', 'a').write(str(session))
		user_id = session['id']
		con, cursor = open_db()
		cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
		g.user = cursor.fetchone()
		close_db(con, cursor)
	else:
		g.user = 0


@app.route('/', methods=["GET"])											#HOME
def home():
	return render_template('home.html')


@app.route('/login', methods=["GET", "POST"])
def login():
	con, cursor = open_db()
	if request.method == "POST":
		email = request.form['email']
		pswd = request.form['password']
		
		cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, pswd))
		user = cursor.fetchone()
		if user:
			session['id'] = user[0]  # Store user_id in session
			close_db(con, cursor)
			return redirect(url_for('home'))
		else:
			return redirect(url_for('signup'))
	
	return render_template('login.html')


@app.route('/signup', methods=["GET", "POST"])
def signup():
	if request.method == "POST":
		con, cursor = open_db()
		name = request.form['username']
		email = request.form['email']
		pswd = request.form['password']

		cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
		if cursor.fetchone():
			return redirect(url_for('login'))
		else:
			cursor.execute("INSERT INTO users (user_name, email, password) VALUES (%s, %s, %s)", (name, email, pswd))
			cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
			session['id'] = cursor.fetchone()[0]

			close_db(con, cursor)

			return redirect(url_for('authorselectionpage'))
	
	return render_template('signup.html')


@app.route('/upload', methods=['GET', 'POST'])								#UPLOAD
def upload():
	if request.method == 'POST':
		con, cursor = open_db()

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

			cursor.execute(f'select author_id from authors where author_name = "{author}"')
			cursor.execute(f'select genre_id from genres where genre_name = "{genre}"')
			author_id = cursor.fetchone()
			genre_id = cursor.fetchone()
			
			cursor.execute(f'select count(*) from books where book_name = "{book_name}"')
			if cursor.fetchone():
				return redirect(url_for('home'))
			if author_id == None:
				cursor.execute(f'insert into authors values(0, "{author}")')
				cursor.execute(f'select author_id from authors where author_name = "{author}"')
				author_id = cursor.fetchall()[0]
			if genre_id == None:
				cursor.execute(f'insert into genres values(0, "{genre}")')
				cursor.execute(f'select genre_id from genres where genre_name = "{genre}"')
				genre_id = cursor.fetchall()[0]
			cursor.execute(f'insert into books (book_name, author_id, uploader_id, genre_id, link, description) values ("{book_name}", {author_id[0]}, {session["id"]}, {genre_id[0]}, "{link}", "-")')

			close_db(con, cursor)
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
	con, cursor = open_db()
	cursor.execute(f"select * from books where uploader_id = {session['id']}")
	bu = cursor.fetchall()
	cursor.execute(f"""
	SELECT 
		books.book_name, 
		authors.author_name, 
		genres.genre_name
	FROM 
		books JOIN authors ON books.author_id = authors.author_id JOIN genres ON books.genre_id = genres.genre_id
	WHERE 
		books.uploader_id = {session['user_id']};
	""")
	close_db(con, cursor)
	return render_template('userprofile.html', books=bu[:5])


@app.route('/searchpage', methods=["POST", "GET"])
def searchpage():
	con, cursor = open_db()
	if request.method == "POST":
		book_name = request.form['book_name']
		author_name = request.form['author_name']
		genre_name = request.form['genre_name']


	cursor.execute("""
		SELECT 
			books.book_name, 
			authors.author_name, 
			genres.genre_name
		FROM 
			books
		JOIN 
			authors ON books.author_id = authors.author_id
		JOIN 
			genres ON books.genre_id = genres.genre_id
		ORDER BY 
			books.book_id DESC
		LIMIT 5;
""")
	books = cursor.fetchall()
	open("abc.txt", "w").write(str(books))
	close_db(con, cursor)
	return render_template('searchpage.html', books=books)


@app.route('/book')
def book():
	return render_template('book.html')


if __name__ == '__main__':
	app.run(debug=True)
