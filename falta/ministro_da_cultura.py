import requests
from bs4 import BeautifulSoup
import json
import re

def get_minister_info():
    url = "https://www.gov.br/cultura/pt-br/composicao/gabinete-da-ministra"
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
    cargo = "Ministro de Estado da Cultura"  # Normalized (Ministra -> Ministro)
    phone = "N/A"
    email = "N/A"

    # Try to find content in the page
    content = soup.find('div', id='content-core')
    if not content:
        content = soup.body
    
    if content:
        contacts_text = content.get_text(separator=' ', strip=True)
        
        # Extract name - look for pattern "MARGARETH MENEZES" or similar
        # Pattern: All caps name followed by "Ministra de Estado"
        name_match = re.search(r'([A-ZÀÁÂÃÉÊÍÓÔÕÚÇ\s]+)\s+Ministra de Estado', contacts_text)
        if name_match:
            raw_name = name_match.group(1).strip()
            # Convert to title case
            name = raw_name.title()
        
        # Try to find phone in span tags first
        phone_spans = content.find_all('span')
        for span in phone_spans:
            span_text = span.get_text(strip=True)
            # Check if it contains a phone pattern
            if re.search(r'\(61\)\s*\d{4}', span_text):
                phone = span_text
                break
        
        # Fallback: try to find phone in text
        if phone == "N/A":
            phone_match = re.search(r'\(61\)\s*\d{4,5}[-\./\s]\d{4}(?:[^E]*)', contacts_text)
            if phone_match:
                phone_chunk = phone_match.group(0).strip()
                if "E-mail" in phone_chunk:
                    phone_chunk = phone_chunk.split("E-mail")[0].strip()
                phone = phone_chunk.strip().rstrip('/')
        
        # Try to find email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.gov\.br', contacts_text)
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
