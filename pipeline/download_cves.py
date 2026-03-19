import requests
import json
import time
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URLS = [
    "https://nvd.handsonhacking.org/nvd.jsonl",
    "http://nvd.handsonhacking.org/nvd.jsonl",
]
LOCAL_FILE = os.path.join(PROJECT_ROOT, "nvd.jsonl")
MAX_RETRIES = 3

def download():
    """Download NVD dataset with retry logic and JSON validation."""
    for url in URLS:
        for attempt in range(MAX_RETRIES):
            try:
                print(f"Downloading from {url} (attempt {attempt + 1})...")
                response = requests.get(url, timeout=300)
                response.raise_for_status()
                with open(LOCAL_FILE, 'wb') as f:
                    f.write(response.content)
                # Validate JSON (file is a JSON array despite .jsonl extension)
                with open(LOCAL_FILE, 'r', encoding='utf-8') as f:
                    json.load(f)
                print("Download and validation successful.")
                return LOCAL_FILE
            except (requests.RequestException, json.JSONDecodeError) as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    wait = 2 ** (attempt + 1)
                    print(f"Retrying in {wait}s...")
                    time.sleep(wait)
        print(f"All retries failed for {url}, trying next URL...")
    print("ERROR: All download attempts failed.", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    download()
