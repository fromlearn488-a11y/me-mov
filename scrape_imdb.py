from playwright.sync_api import sync_playwright
from datetime import datetime
import json

URL = "https://www.imdb.com/user/p.lduug7hx3zgtpyp77wrmnhuiyy/watchhistory/"

def scrape_movies():
    movies = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 🔥 capture network responses
        def handle_response(response):
            try:
                if "watchhistory" in response.url and response.request.resource_type == "fetch":
                    data = response.json()

                    # try different possible structures
                    if isinstance(data, dict):
                        if "mainColumnData" in str(data):
                            extract_from_json(data)
            except:
                pass

        def extract_from_json(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == "titleText" and isinstance(v, dict):
                        if "text" in v:
                            movies.append(v["text"])
                    else:
                        extract_from_json(v)
            elif isinstance(obj, list):
                for i in obj:
                    extract_from_json(i)

        page.on("response", handle_response)

        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(8000)

        browser.close()

    # clean duplicates
    seen = set()
    clean = []
    for m in movies:
        if m not in seen:
            seen.add(m)
            clean.append(m)

    return clean[:15]


def update_readme(movies):
    if not movies:
        print("No movies found")
        return

    block = "## 🎬 Recently Watched\n\n"
    for m in movies:
        block += f"- {m}\n"

    block += f"\n_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n"

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    start = content.find("<!-- IMDB_START -->")
    end = content.find("<!-- IMDB_END -->")

    new_content = (
        content[:start + len("<!-- IMDB_START -->")]
        + "\n\n"
        + block
        + "\n"
        + content[end:]
    )

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

    print("Updated README with", len(movies), "movies")


if __name__ == "__main__":
    movies = scrape_movies()
    print("Movies found:", len(movies))
    print(movies)
    update_readme(movies)
