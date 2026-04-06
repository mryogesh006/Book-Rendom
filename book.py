from flask import Flask, request
import requests
import os

app = Flask(__name__)

API_URL = "https://api.freeapi.app/api/v1/public/books?limit=210"


def get_books_payload():
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return response.json() or {}
    except requests.exceptions.RequestException as e:
        print("API Error:", e)
        return {}


def normalize_book(book_item):
    volume_info = (book_item or {}).get("volumeInfo") or {}
    return {
        "title": volume_info.get("title", "Title not available"),
        "description": volume_info.get("description", "Description not available"),
        "link": volume_info.get("previewLink") or volume_info.get("infoLink") or "#",
    }


def fetch_all_books():
    payload = get_books_payload()
    items = (payload.get("data") or {}).get("data", [])
    return [normalize_book(item) for item in items]


def get_index(total_books):
    requested_index = request.args.get("i", "0")
    try:
        return int(requested_index) % total_books
    except:
        return 0


def render_book_card(book, current_index, total_books):
    next_index = (current_index + 1) % total_books
    return f"""
    <div style='max-width:760px;margin:40px auto;padding:20px;border:1px solid #ddd;border-radius:12px;font-family:Arial'>
      <h2>{book['title']}</h2>
      <p>{book['description']}</p>
      <a href='{book['link']}' target='_blank' style='margin-right:12px'>Preview Book</a>
      <a href='/?i={next_index}'>Next</a>
      <p style='color:#666'>Book {current_index + 1} of {total_books}</p>
    </div>
    """


@app.route("/")
def home():
    try:
        books = fetch_all_books()

        if not books:
            return "<h2>No books found or API failed</h2>"

        current_index = get_index(len(books))
        selected_book = books[current_index]

        return render_book_card(selected_book, current_index, len(books))

    except Exception as e:
        print("Server Error:", e)
        return f"<h2>Error: {e}</h2>", 500


# IMPORTANT for Render deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)