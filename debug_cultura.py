
import requests
from bs4 import BeautifulSoup
import re

url = "https://www.gov.br/cultura/pt-br/composicao/gabinete-da-ministra"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# Inspect item divs
items = soup.find_all("div", class_="item")
for item in items:
    print(f"Item attributes: {item.attrs}")
    print(f"Item content: {item.get_text(strip=True)[:100]}")
    # Also check all sub-elements for attributes
    for child in item.find_all(True):
        if child.attrs:
            print(f"  {child.name} attributes: {child.attrs}")

# Print all p and span tags
for tag in soup.find_all(["p", "span"]):
    txt = tag.get_text(strip=True)
    if len(txt) > 5 and ("@" in txt or any(c.isdigit() for c in txt)):
        print(f"{tag.name}: {txt}")

# Specifically look for Margareth
target = "MARGARETH"
for tag in soup.find_all(string=re.compile(target, re.I)):
    curr = tag.parent
    print(f"--- Context for {target} ---")
    # Go up a few levels
    for _ in range(3):
        if curr and curr.parent:
            curr = curr.parent
    print(curr.prettify() if hasattr(curr, 'prettify') else str(curr))
    print("-" * 40)
