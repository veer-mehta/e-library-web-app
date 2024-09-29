import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


#Based on preferences and Genre given immediately after Login






#################################################################################################################

a=pd.read_csv("Books_df.csv")
Model=pd.DataFrame(a)
Model_cleaned = Model.dropna(subset=['Author'])
books_df=Model_cleaned[['Title','Author','Sub Genre','Rating']]
Model_cleaned = Model_cleaned[['Author', 'Rating', 'Sub Genre']]

#We initially take genre and author but later we will get during login page
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

# Based on the searches 
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from fuzzywuzzy import process  # Fuzzy matching

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

# Example usage: Recommend books similar to a misspelled title
book_title = "Harri Poter"  # Example with spelling error
recommended_books = recommend_books_by_title(book_title, similarity_matrix, books_df, top_n=10)

# Print fuzzy matches or the actual recommendations
if isinstance(recommended_books, str):
    print(recommended_books)  # Prints fuzzy-matched suggestions
elif isinstance(recommended_books, pd.DataFrame):
    print(recommended_books[['Title', 'Author', 'Sub Genre', 'Rating']])
