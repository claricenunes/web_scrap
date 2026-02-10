import requests
from bs4 import BeautifulSoup
import json
import re

def get_minister_info():
    url = "https://www.gov.br/mcti/pt-br/composicao/ministra"
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
    name = "N/A"
    cargo = "Ministro de Estado da Ciência, Tecnologia e Inovação"  # Normalized (Ministra -> Ministro)
    phone = "N/A"
    email = "N/A"

    # Extract name from title tag
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.get_text()
        # Title format: "Luciana Santos — Ministério da Ciência, Tecnologia e Inovação"
        if "—" in title_text:
            name = title_text.split("—")[0].strip()
        elif "–" in title_text:
            name = title_text.split("–")[0].strip()
    
    # Try to find content in the page
    content = soup.find('div', id='content-core')
    if not content:
        content = soup.body
    
    if content:
        contacts_text = content.get_text(separator=' ', strip=True)
        
        # Try to find email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.gov\.br', contacts_text)
        if email_match:
            email = email_match.group(0)
        
        # Try to find phone
        phone_match = re.search(r'\(61\)\s*\d{4,5}[-\.]\d{4}(?:[^E]*)', contacts_text)
        if phone_match:
            phone_chunk = phone_match.group(0).strip()
            if "E-mail" in phone_chunk:
                phone_chunk = phone_chunk.split("E-mail")[0].strip()
            phone = phone_chunk.strip().rstrip('/')

    data = {
        "Nome": name,
        "Cargo": cargo,
        "Telefone": phone,
        "Email": email
    }

    print(json.dumps(data, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    get_minister_info()
