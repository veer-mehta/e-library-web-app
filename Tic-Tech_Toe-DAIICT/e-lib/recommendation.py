import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

a=pd.read_csv("Books_df.csv")
Model=pd.DataFrame(a)
Model_cleaned = Model.dropna(subset=['Author'])
books_df=Model_cleaned[['Title','Author','Sub Genre','Rating']]
Model_cleaned = Model_cleaned[['Author', 'Rating', 'Sub Genre']]

#We initially take genre and author but later we will get during login page itself
selected_genres = ['Cinema & Broadcast','Theory & Criticism']
selected_authors = ['J.K. Rowling', 'William Shakespeare']

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