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
                    snippet_display = snippet_raw.replace(
                        content[idx:idx+len(q)], f"**{q}**"
                    )
                    results.append({
                        "file": file_path,
                        "snippet": snippet_display.strip().replace("\n", " "),
                        "url": f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/blob/{BRANCH}/{file_path}"
                    })
        except Exception as e:
            results.append({"file": file_path, "error": str(e)})

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
                "content": content[:4000]
            }
        else:
            return {"error": f"Failed to fetch file: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/list-files")
def list_files():
    tree_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/git/trees/{BRANCH}?recursive=1"
    response = requests.get(tree_url)
    files = {
        "protocols": [],
        "policies": [],
        "memos": []
    }

    if response.status_code == 200:
        tree = response.json().get("tree", [])
        for item in tree:
            if item["path"].endswith(".md"):
                if item["path"].lower().startswith("protocols/"):
                    files["protocols"].append(item["path"].split("/")[-1])
                elif item["path"].lower().startswith("policies/"):
                    files["policies"].append(item["path"].split("/")[-1])
                elif item["path"].lower().startswith("memos/"):
                    files["memos"].append(item["path"].split("/")[-1])

    return files

@app.get("/search-by-tag")
def search_by_tag(tag: str = Query(..., description="Tag or keyword to match filenames")):
    tag = tag.lower()
    md_files = get_markdown_files()
    results = []
    for file_path in md_files:
        if tag in file_path.lower():
            results.append({
                "file": file_path,
                "url": f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/blob/{BRANCH}/{file_path}"
            })
    return {"tag": tag, "matches": results}

@app.get("/compare")
def compare_files(
    file1: str = Query(..., description="Path to first markdown file"),
    file2: str = Query(..., description="Path to second markdown file")
):
    def fetch_file(path):
        url = f"https://raw.githubusercontent.com/{GITHUB_OWNE_
