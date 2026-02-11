
import requests
from bs4 import BeautifulSoup
import re

urls = [
    "https://www.gov.br/saude/pt-br/composicao",
    "https://www.gov.br/saude/pt-br/composicao/quem-e-quem",
    "https://www.gov.br/saude/pt-br/composicao/gabinete"
]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

for url in urls:
    print(f"Checking {url}...")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.content, "html.parser")
        
        # Find all names
        containers = soup.find_all("div", class_=re.compile(r'dados-p[oe]ssoa'))
        print(f"  Found {len(containers)} containers.")
        for i, c in enumerate(containers):
            name = c.find("p", class_="nome")
            if name:
                print(f"  {i}: {name.get_text(strip=True)}")
                
        # Broad search for any "Trindade"
        text = soup.get_text()
        if "Trindade" in text:
            print("  Found Trindade somewhere in text.")
            
    except Exception as e:
        print(f"  Error: {e}")
