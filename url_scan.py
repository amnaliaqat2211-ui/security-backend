from fastapi import APIRouter
import re

router = APIRouter()

# Simple URL regex
url_pattern = r"(https?://[^\s]+)"

# Fake malicious keywords (for now)
dangerous_words = ["phishing", "hack", "malware", "attack"]

@router.post("/scan-url")
def scan_url(message: str):
    urls = re.findall(url_pattern, message)

    if not urls:
        return {"message": "No URL found"}

    results = []

    for url in urls:
        status = "Safe"

        for word in dangerous_words:
            if word in url.lower():
                status = "Malicious"

        results.append({
            "url": url,
            "status": status
        })

    return {"results": results}