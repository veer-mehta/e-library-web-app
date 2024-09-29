function searchBooks() {
    const title = document.getElementById('book-title').value;
    const author = document.getElementById('author-name').value;
    const genre = document.getElementById('book-genre').value;

    // Example of combining user inputs into a search query
    const query = `${title} ${author} ${genre}`;
    document.getElementById('search-query').innerText = query.trim() || 'Your Search';

    // TODO: Call backend search API with user inputs and update search results dynamically
    console.log("Searching for:", { title, author, genre });
}