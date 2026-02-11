
import requests
from bs4 import BeautifulSoup
import re

url = "https://www.gov.br/saude/pt-br/composicao/quem-e-quem"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# Search for Nisia
target = "Nísia"
tags = soup.find_all(string=re.compile(target, re.I))
for tag in tags:
    print(f"Found {target} in {tag.parent.name}: {tag.parent.get_text(strip=True)[:100]}")
    # Print parents to see if she is under a different class
    curr = tag.parent
    for _ in range(3):
        if curr and curr.parent:
            curr = curr.parent
            print(f"  Parent: {curr.name}|{curr.get('class')}")
