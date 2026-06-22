import requests
from datetime import datetime

USER_ID = "p.lduug7hx3zgtpyp77wrmnhuiyy"

GRAPHQL_URL = "https://www.imdb.com/graphql"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# This query is based on IMDb internal structure (watch history feed)
query = {
    "query": """
    query WatchHistory($id: ID!) {
      user(id: $id) {
        name
        watchHistory {
          edges {
            node {
              titleText {
                text
              }
            }
          }
        }
      }
    }
    """,
    "variables": {
        "id": USER_ID
    }
}

def fetch_movies():
    res = requests.post(GRAPHQL_URL, json=query, headers=headers)

    if res.status_code != 200:
        print("Request failed:", res.status_code)
        return []

    data = res.json()

    edges = data["data"]["user"]["watchHistory"]["edges"]

    movies = []
    for e in edges:
        title = e["node"]["titleText"]["text"]
        movies.append(title)

    return movies


def update_readme(movies):
    movies = movies[:10]

    block = "## 🎬 Recently Watched\n\n"
    for m in movies:
        block += f"- {m}\n"

    block += f"\n_Last updated: {datetime.now().strftime('%Y-%m-%d')}_\n"

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

    print("Updated README")


def main():
    movies = fetch_movies()

    if not movies:
        print("No data found")
        return

    update_readme(movies)


if __name__ == "__main__":
    main()
