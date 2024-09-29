from flask import Flask, render_template, request, redirect, url_for, g, session
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from fuzzywuzzy import process  # Fuzzy matching

from mega import Mega
import os, pymysql

app = Flask(__name__)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = 'dfsdf'

db = pymysql.connections.Connection(host='localhost', user='root', password='Vam#090905', db='bookslib')

cursor = db.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS bookslib")

cursor.execute("use bookslib")

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
mega = mega.login('veeramehta09@gmail.com', 'vam#090905')


@app.before_request
def load_logged_in_user():
	user_id = session['user_id']
	if user_id == None:
		user_id = 0
	cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
	g.user = cursor.fetchone()


@app.route('/', methods=["GET"])											#HOME
def home():
	return render_template('home.html')


@app.route('/login', methods=["GET", "POST"])
def login():
	if request.method == "POST":
		email = request.form['email']
		pswd = request.form['password']
		
		cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, pswd))
		user = cursor.fetchone()
		if user:
			session['user_id'] = user[0]  # Store user_id in session
			db.commit()
			return redirect(url_for('home'))
		else:
			return redirect(url_for('signup'))

		#####

		cursor.execute(f"select * from users where email = '{email}'")
		d = cursor.fetchone()
		if len(d):
			globaluser['id'] = d[0]
			globaluser['name'] = d[1]
			globaluser['email'] = d[2]
			globaluser['pwd'] = d[3]
			open("abc.txt", "w").write(str(globaluser))
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

		cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
		if cursor.fetchone():
			return redirect(url_for('login'))
		else:
			cursor.execute("INSERT INTO users (user_name, email, password) VALUES (%s, %s, %s)", (name, email, pswd))
			cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
			session['user_id'] = cursor.fetchone()[0]
			db.commit()
			return redirect(url_for('authorselectionpage'))


		#####

		cursor.execute(f"select * from users where email = '{email}'")
		d = cursor.fetchall()
		open("abc.txt", "w").write(str(d))

		if len(d):
			return redirect(url_for('login'))
		else:
			cursor.execute(f'insert into users values (0, "{name}", "{email}", "{pswd}")')
			cursor.execute(f'select * from users where user_name = "{name}"')
			d = cursor.fetchone()
			globaluser['id'] = d[0]
			globaluser['name'] = d[1]
			globaluser['email'] = d[2]
			globaluser['pwd'] = d[3]
			open("abc.txt", "w").write(str(globaluser))
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
			cursor.execute(f'insert into books (book_name, author_id, uploader_id, genre_id, link, description) values ("{book_name}", {author_id[0]}, {session["user_id"]}, {genre_id[0]}, "{link}", "-")')
			open("abc.txt", "a").write(str(session['user_id']) + str(cursor.fetchall()))

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
	cursor.execute(f"select * from books where uploader_id = {session['user_id']}")
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
	open("abc.txt", "w").write(str(session['user_id']) + str(bu))

	return render_template('userprofile.html', books=bu[:5])


@app.route('/searchpage', methods=["POST", "GET"])
def searchpage():

	if request.method == "POST":
		book_name = request.form['book_name']
		author_name = request.form['author_name']
		genre_name = request.form['genre_name']

		srch()


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
	return render_template('searchpage.html', books=books)


@app.route('/book')
def book():
	return render_template('book.html')



def srch(nm, au, gn):
	a=pd.read_csv("Books_df.csv")
	Model=pd.DataFrame(a)
	Model_cleaned = Model.dropna(subset=['Author'])
	books_df=Model_cleaned[['Title','Author','Sub Genre','Rating']]
	Model_cleaned = Model_cleaned[['Author', 'Rating', 'Sub Genre']]

	#We initially take genre and author but later we will get during login page
	selected_genres = [gn]
	selected_authors = [au]

	# Step 1: Filter books by preferred genres
	genre_filtered_books = books_df[books_df['Sub Genre'].apply(lambda genres: any(genre in genres for genre in selected_genres))]
	genre_filtered_books = genre_filtered_books.sort_values(by='Rating', ascending=False)

	# Step 2: Filter books by preferred authors
	author_filtered_books = books_df[books_df['Author'].isin(selected_authors)]
	author_filtered_books = author_filtered_books.sort_values(by='Rating', ascending=False)

	# Step 3: Select top 5 books from genres and authors
	top_genre_books = genre_filtered_books.head(5)
	top_author_books = author_filtered_books.head(5)
	if len(top_genre_books) < 5:
		remaining_genre_slots = 5 - len(top_genre_books)
		top_genre_books = pd.concat([top_genre_books, author_filtered_books.head(remaining_genre_slots)]).drop_duplicates()

	if len(top_author_books) < 5:
		remaining_author_slots = 5 - len(top_author_books)
		top_author_books = pd.concat([top_author_books, genre_filtered_books.head(remaining_author_slots)]).drop_duplicates()

	# Final recommendation of 10 books
	recommended_books = pd.concat([top_genre_books, top_author_books]).drop_duplicates().head(10)

	# Display the final recommended books
	print(recommended_books[['Title', 'Rating']])

	# Based on the searches 

	# Step 1: One-Hot Encode 'Author'
	author_encoder = OneHotEncoder(sparse_output=False)
	encoded_author = author_encoder.fit_transform(books_df[['Author']])

	# Step 2: One-Hot Encode 'Sub Genre'
	genre_encoder = OneHotEncoder(sparse_output=False)
	encoded_genre = genre_encoder.fit_transform(books_df[['Sub Genre']])

	# Step 3: Normalize 'Rating' column
	scaler = MinMaxScaler()
	normalized_ratings = scaler.fit_transform(books_df[['Rating']])

	# Step 4: Apply weights
	author_weight = 3
	genre_weight = 1
	rating_weight = 1

	# Step 5: Create DataFrames for weighted features
	df_encoded_author = pd.DataFrame(encoded_author * author_weight, columns=author_encoder.get_feature_names_out(['Author']))
	df_encoded_genre = pd.DataFrame(encoded_genre * genre_weight, columns=genre_encoder.get_feature_names_out(['Sub Genre']))

	# Step 6: Combine all features
	combined_features = df_encoded_author.join(df_encoded_genre).join(
		pd.DataFrame(normalized_ratings * rating_weight, columns=['Rating'])
	)

	# Step 7: Compute Cosine Similarity
	similarity_matrix = cosine_similarity(combined_features)

	# Step 8: Recommend books by title, using fuzzy matching for spelling errors
	def recommend_books_by_title(book_title, similarity_matrix, df, top_n=5):
		# Check if the book title exists exactly in the dataset
		if book_title not in df['Title'].values:
			# Use fuzzy matching to find the closest matches
			closest_matches = process.extract(book_title, df['Title'].values, limit=top_n)
			
			# If close matches are found, return them
			if closest_matches:
				return f"Book not found. Did you mean one of these?: {[match[0] for match in closest_matches]}"
			else:
				return "No similar books found."
		
		# If exact match is found, continue with the recommendation
		book_index = df[df['Title'] == book_title].index[0]
		
		# Calculate similarity scores
		similarity_scores = list(enumerate(similarity_matrix[book_index]))
		similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
		
		# Get the indices of the top similar books (excluding itself)
		top_books_indices = [i[0] for i in similarity_scores[1:top_n+1]]
		
		# Return the recommended books sorted by their rating in descending order
		recommended_books = df.iloc[top_books_indices].sort_values(by='Rating', ascending=False)
		
		return recommended_books

	recommended_books = recommend_books_by_title(nm, similarity_matrix, books_df, top_n=10)

	# Print fuzzy matches or the actual recommendations
	if isinstance(recommended_books, str):
		return recommended_books  # Prints fuzzy-matched suggestions
	elif isinstance(recommended_books, pd.DataFrame):
		return recommended_books[['Title', 'Author', 'Sub Genre', 'Rating']]




if __name__ == '__main__':
	app.run(debug=True)
