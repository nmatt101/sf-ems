from fastapi import FastAPI, Query
from typing import List
import requests

app = FastAPI()

GITHUB_OWNER = "nmatt101"
GITHUB_REPO = "sf-ems"
BRANCH = "main"

def get_markdown_files():
    api_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/trees/{BRANCH}?recursive=1"
    response = requests.get(api_url)
    markdown_files = []

    if response.status_code == 200:
        tree = response.json().get("tree", [])
        for item in tree:
            if item["path"].endswith(".md"):
                markdown_files.append(item["path"])

    return markdown_files

@app.get("/search")
def search_documents(q: str = Query(..., description="Search query")):
    results = []
    md_files = get_markdown_files()

    for file_path in md_files:
        raw_url = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{BRANCH}/{file_path}"
        try:
            response = requests.get(raw_url)
            if response.status_code == 200:
                content = response.text.lower()
                if q.lower() in content:
                    idx = content.find(q.lower())
                    snippet = content[max(0, idx - 100): idx + 100]
                    results.append({
                        "file": file_path,
                        "snippet": snippet.strip().replace("\n", " ")
                    })
        except Exception as e:
            results.append({
                "file": file_path,
                "error": str(e)
            })

    return {"query": q, "matches": results}
