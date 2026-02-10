import requests
from bs4 import BeautifulSoup
import json
import re

def get_minister_info():
    url = "https://www.gov.br/defesa/pt-br/composicao/quem-e-quem"
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
    cargo = "Ministro de Estado da Defesa"
    phone = "N/A"
    email = "N/A"

    # Try to find content in the page
    content = soup.find('div', id='content-core')
    if not content:
        content = soup.body
    
    if content:
        contacts_text = content.get_text(separator=' ', strip=True)
        
        # Extract name - look for pattern before "MINISTRO DE ESTADO DA DEFESA"
        # Pattern: "Ministro da Defesa José Mucio Monteiro Filho MINISTRO DE ESTADO"
        name_match = re.search(r'Ministro da Defesa\s+([A-Za-zÀ-ÿ\s]+?)\s+MINISTRO DE ESTADO', contacts_text)
        if name_match:
            name = name_match.group(1).strip()
        
        # Try to find phone in span tags first
        phone_spans = content.find_all('span')
        for span in phone_spans:
            span_text = span.get_text(strip=True)
            # Check if it contains a phone pattern
            if re.search(r'\(61\)\s*\d{4}', span_text):
                phone = span_text
                break
        
        # Fallback: try to find phone in text - look for the first phone after "MINISTRO DE ESTADO"
        if phone == "N/A":
            # Find the position of "MINISTRO DE ESTADO DA DEFESA" and look for phone after it
            minister_pos = contacts_text.find("MINISTRO DE ESTADO DA DEFESA")
            if minister_pos != -1:
                text_after_minister = contacts_text[minister_pos:minister_pos+200]
                phone_match = re.search(r'Telefone\(s\)\s*:\s*((?:\(61\)\s*\d{4}[-\s]\d{4}(?:\s*/\s*\d{4}[-\s]\d{4})*)+)', text_after_minister)
                if phone_match:
                    phone = phone_match.group(1).strip()
        
        # Try to find email - look for the first email after "MINISTRO DE ESTADO"
        minister_pos = contacts_text.find("MINISTRO DE ESTADO DA DEFESA")
        if minister_pos != -1:
            text_after_minister = contacts_text[minister_pos:minister_pos+300]
            email_match = re.search(r'E-mail\s*:\s*([\w\.-]+@[\w\.-]+\.gov\.br)', text_after_minister)
            if email_match:
                email = email_match.group(1).strip()

    data = {
        "Nome": name,
        "Cargo": cargo,
        "Telefone": phone,
        "Email": email
    }

    print(json.dumps(data, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    get_minister_info()
