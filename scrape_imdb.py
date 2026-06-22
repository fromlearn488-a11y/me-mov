from playwright.sync_api import sync_playwright
import json
from datetime import datetime

URL = "https://www.imdb.com/user/p.lduug7hx3zgtpyp77wrmnhuiyy/watchhistory/"


def scrape_movies():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, wait_until="domcontentloaded")

        # wait for hydration
        page.wait_for_timeout(5000)

        html = page.content()

        browser.close()

    # extract __NEXT_DATA__
    start_tag = '<script id="__NEXT_DATA__" type="application/json">'
    start = html.find(start_tag)

    if start == -1:
        print("No __NEXT_DATA__ found")
        return []

    start += len(start_tag)
    end = html.find("</script>", start)

    json_text = html[start:end]

    try:
        data = json.loads(json_text)
    except:
        print("JSON parse failed")
        return []

    # navigate safely
    movies = []

    try:
        edges = (
            data["props"]["pageProps"]
            ["mainColumnData"]
            ["advancedTitleSearch"]
            ["edges"]
        )

        for e in edges:
            try:
                title = e["node"]["title"]["titleText"]["text"]
                if title:
                    movies.append(title)
            except:
                continue

    except Exception as e:
        print("Path error:", e)

    # remove duplicates
    seen = set()
    clean = []
    for m in movies:
        if m not in seen:
            seen.add(m)
            clean.append(m)

    return clean[:20]


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

    print("Updated README with", len(movies), "movies")


if __name__ == "__main__":
    movies = scrape_movies()
    print("Movies found:", len(movies))
    print(movies)
    update_readme(movies)
