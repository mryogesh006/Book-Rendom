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
    except (TypeError, ValueError):
        return 0


def render_book_card(book, current_index, total_books):
    import html

    next_index = (current_index + 1) % total_books
    title = html.escape(book.get("title", "Title not available"))
    description = html.escape(book.get("description", "Description not available"))
    link = html.escape(book.get("link", "#"), quote=True)

    return f"""
        <!doctype html>
        <html lang='en'>
            <head>
                <meta charset='utf-8'>
                <meta name='viewport' content='width=device-width, initial-scale=1'>
                <title>Book Browser</title>
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');

                    :root {{
                        --bg-1: #f8fbff;
                        --bg-2: #eef7f3;
                        --ink: #10231d;
                        --muted: #4e675f;
                        --primary: #0b6e4f;
                        --primary-hover: #09573f;
                        --line: #d8e7df;
                        --card: rgba(255, 255, 255, 0.88);
                    }}

                    * {{ box-sizing: border-box; }}

                    body {{
                        margin: 0;
                        min-height: 100vh;
                        font-family: 'Space Grotesk', sans-serif;
                        color: var(--ink);
                        background:
                            radial-gradient(circle at 85% 12%, #ffd9a8 0%, transparent 30%),
                            radial-gradient(circle at 15% 88%, #bde7d5 0%, transparent 32%),
                            linear-gradient(145deg, var(--bg-1), var(--bg-2));
                        display: grid;
                        place-items: center;
                        padding: 20px;
                    }}

                    .card {{
                        width: min(860px, 100%);
                        background: var(--card);
                        border: 1px solid var(--line);
                        border-radius: 20px;
                        backdrop-filter: blur(8px);
                        box-shadow: 0 18px 45px rgba(16, 35, 29, 0.14);
                        overflow: hidden;
                        animation: rise 500ms ease-out;
                    }}

                    .header {{
                        padding: 24px 26px 16px;
                        border-bottom: 1px solid var(--line);
                    }}

                    .badge {{
                        display: inline-block;
                        font-size: 12px;
                        font-weight: 700;
                        letter-spacing: 0.08em;
                        text-transform: uppercase;
                        color: #13553f;
                        background: #d4f1e6;
                        border: 1px solid #bce4d4;
                        padding: 6px 10px;
                        border-radius: 999px;
                        margin-bottom: 14px;
                    }}

                    h1 {{
                        margin: 0;
                        line-height: 1.2;
                        font-size: clamp(1.35rem, 2.1vw, 2rem);
                    }}

                    .content {{
                        padding: 22px 26px 8px;
                    }}

                    .description {{
                        margin: 0;
                        color: var(--muted);
                        line-height: 1.72;
                        font-size: 1rem;
                        max-height: 310px;
                        overflow: auto;
                        padding-right: 4px;
                    }}

                    .footer {{
                        display: flex;
                        gap: 12px;
                        align-items: center;
                        justify-content: space-between;
                        flex-wrap: wrap;
                        padding: 18px 26px 24px;
                    }}

                    .actions {{
                        display: flex;
                        gap: 10px;
                        flex-wrap: wrap;
                    }}

                    .btn {{
                        text-decoration: none;
                        border-radius: 12px;
                        padding: 10px 16px;
                        font-weight: 600;
                        transition: transform 120ms ease, background-color 120ms ease, box-shadow 120ms ease;
                    }}

                    .btn:active {{
                        transform: translateY(1px);
                    }}

                    .btn-primary {{
                        background: var(--primary);
                        color: #fff;
                        box-shadow: 0 10px 18px rgba(11, 110, 79, 0.26);
                    }}

                    .btn-primary:hover {{
                        background: var(--primary-hover);
                    }}

                    .btn-secondary {{
                        color: var(--ink);
                        background: #fff;
                        border: 1px solid var(--line);
                    }}

                    .btn-secondary:hover {{
                        background: #f2f8f5;
                    }}

                    .counter {{
                        color: var(--muted);
                        font-size: 0.95rem;
                    }}

                    @keyframes rise {{
                        from {{
                            opacity: 0;
                            transform: translateY(16px) scale(0.98);
                        }}
                        to {{
                            opacity: 1;
                            transform: translateY(0) scale(1);
                        }}
                    }}

                    @media (max-width: 640px) {{
                        .header,
                        .content,
                        .footer {{
                            padding-left: 18px;
                            padding-right: 18px;
                        }}

                        .actions {{
                            width: 100%;
                        }}

                        .btn {{
                            flex: 1;
                            text-align: center;
                        }}
                    }}
                </style>
            </head>
            <body>
                <main class='card'>
                    <section class='header'>
                        <span class='badge'>Discover</span>
                        <h1>{title}</h1>
                    </section>

                    <section class='content'>
                        <p class='description'>{description}</p>
                    </section>

                    <section class='footer'>
                        <div class='actions'>
                            <a class='btn btn-primary' href='{link}' target='_blank' rel='noopener noreferrer'>Preview Book</a>
                            <a class='btn btn-secondary' href='/?i={next_index}'>Next Book</a>
                        </div>
                        <p class='counter'>Book {current_index + 1} of {total_books}</p>
                    </section>
                </main>
            </body>
        </html>
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)