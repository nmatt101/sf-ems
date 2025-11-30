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
    query_lower = q.lower()

    for file_path in md_files:
        raw_url = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{BRANCH}/{file_path}"
        try:
            response = requests.get(raw_url)
            if response.status_code == 200:
                content = response.text
                content_lower = content.lower()
                if query_lower in content_lower:
                    idx = content_lower.find(query_lower)
                    start = max(0, idx - 200)
                    end = min(len(content), idx + len(q) + 200)
                    snippet_raw = content[start:end]

                    # Optional: bold the matched term
                    snippet_display = snippet_raw.replace(
                        content[idx:idx+len(q)], f"**{q}**"
                    )

                    results.append({
                        "file": file_path,
                        "snippet": snippet_display.strip().replace("\n", " "),
                        "url": f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/blob/{BRANCH}/{file_path}"
                    })
        except Exception as e:
            results.append({
                "file": file_path,
                "error": str(e)
            })

    return {"query": q, "matches": results}

@app.get("/summarize")
def summarize_file(file: str = Query(..., description="Path to a markdown file")):
    raw_url = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{BRANCH}/{file}"
    try:
        response = requests.get(raw_url)
        if response.status_code == 200:
            content = response.text
            return {
                "file": file,
                "content": content[:4000]  # GPT will summarize this
            }
        else:
            return {"error": f"Failed to fetch file: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
