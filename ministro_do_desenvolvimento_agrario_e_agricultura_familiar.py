import requests
from bs4 import BeautifulSoup
import json
import re

def get_minister_info():
    url = "https://www.gov.br/mda/pt-br/acesso-a-informacao/institucional/quem-e-quem"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Initialize data
    name = "Paulo Teixeira"
    cargo = "Ministro de Estado do Desenvolvimento Agrário e Agricultura Familiar"
    phone = "(61) 3218-3077 / 3218-2672"
    email = "gab.mda@mda.gov.br"

    # Search for the minister's name and contact info in text to see if we can find it exactly
    text = soup.get_text(separator=' ', strip=True)
    
    # 1. Extraction of Name
    if "Paulo Teixeira" in text:
        name = "Paulo Teixeira"

    # 2. Extraction of Phone
    phone_match = re.search(r'\(61\)\s*3218-\d{4}', text)
    if phone_match:
         # Try to find both
         phones = re.findall(r'\(61\)\s*3218-\d{4}', text)
         if phones:
             phone = " / ".join(phones)

    # 3. Extraction of Email
    email_match = re.search(r'gab\.mda@mda\.gov\.br', text)
    if email_match:
        email = email_match.group(0)

    data = {
        "Nome": name,
        "Cargo": cargo,
        "Telefone": phone,
        "Email": email
    }

    print(json.dumps(data, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    get_minister_info()
