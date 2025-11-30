from fastapi import FastAPI, Query
from typing import List
import requests

app = FastAPI()

# List of .md files to search in your GitHub repo
files_to_search = [
    "protocols/airway-management.md",
    "protocols/cardiac-arrest.md",
    "policies/transport-guidelines.md",
    "memos/2023-paramedic-memo.md"
]

# Your GitHub username and repo
GITHUB_OWNER = "nmatt101"
GITHUB_REPO = "sf-ems"
BRANCH = "main"

@app.get("/search")
def search_documents(q: str = Query(..., description="Search query")):
    results = []

    for file_path in files_to_search:
        url = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{BRANCH}/{file_path}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                content = response.text.lower()
                if q.lower() in content:
                    # Return a snippet with context
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
