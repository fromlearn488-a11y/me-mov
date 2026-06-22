import requests
import json
from datetime import datetime

URL = "https://www.imdb.com/user/p.lduug7hx3zgtpyp77wrmnhuiyy/watchhistory/"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

def fetch_html():
    res = requests.get(URL, headers=headers)

    print("Status:", res.status_code)

    if res.status_code != 200:
        return None

    return res.text


def extract_json(html):
    start = html.find('__NEXT_DATA__')
    if start == -1:
        return None

    start = html.find('>', start) + 1
    end = html.find('</script>', start)

    try:
        return json.loads(html[start:end])
    except:
        return None


def extract_movies(data):
    movies = []

    try:
        edges = data["props"]["pageProps"]["mainColumnData"]["edges"]

        for e in edges:
            node = e.get("node", {})
            title = node.get("titleText", {}).get("text")

            if title:
                movies.append(title)

    except:
        pass

    return movies


def update_readme(movies):
    if not movies:
        print("No movies found")
        return

    block = "## 🎬 Recently Watched\n\n"
    for m in movies[:10]:
        block += f"- {m}\n"

    block += f"\n_Last updated: {datetime.now().strftime('%Y-%m-%d')}_\n"

    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
    except:
        print("README.md not found")
        return

    start = content.find("<!-- IMDB_START -->")
    end = content.find("<!-- IMDB_END -->")

    if start == -1 or end == -1:
        print("Missing README markers")
        return

    new_content = (
        content[:start + len("<!-- IMDB_START -->")]
        + "\n\n"
        + block
        + "\n"
        + content[end:]
    )

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

    print("README updated")


def main():
    html = fetch_html()
    if not html:
        print("Failed to fetch IMDb page")
        return

    data = extract_json(html)
    if not data:
        print("Failed to parse JSON")
        return

    movies = extract_movies(data)

    print("Movies found:", len(movies))

    update_readme(movies)


if __name__ == "__main__":
    main()
