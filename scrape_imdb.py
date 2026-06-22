from playwright.sync_api import sync_playwright
from datetime import datetime

URL = "https://www.imdb.com/user/p.lduug7hx3zgtpyp77wrmnhuiyy/watchhistory/"


def scrape_movies():
    movies = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, wait_until="domcontentloaded")

        # IMPORTANT: wait extra for JS hydration
        page.wait_for_timeout(5000)

        # scroll slowly to trigger lazy load
        for _ in range(8):
            page.mouse.wheel(0, 2500)
            page.wait_for_timeout(1500)

        # 🎯 target movie title containers (IMPORTANT FIX)
        elements = page.query_selector_all("li a")

        for el in elements:
            try:
                text = el.inner_text().strip()
                href = el.get_attribute("href")

                # filter real IMDb titles
                if (
                    text
                    and href
                    and "/title/" in href
                    and len(text) > 2
                    and "Episode" not in text
                ):
                    movies.append(text)

            except:
                continue

        browser.close()

    # remove duplicates while preserving order
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
